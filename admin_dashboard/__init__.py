from flask import Blueprint, request, render_template, redirect, url_for, jsonify
import json
import os
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

LICENSE_FILE = "licenses.json"
ADMIN_API_KEY = "AdminHW1"

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return []
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)

@dashboard_bp.route("/admin", methods=["GET"])
def dashboard():
    if request.args.get("api_key") != ADMIN_API_KEY:
        return "Unauthorized", 401
    query = request.args.get("search", "").lower()
    licenses = load_licenses()
    if query:
        licenses = [lic for lic in licenses if query in lic["key"].lower()]
    return render_template("dashboard.html", licenses=licenses, api_key=ADMIN_API_KEY)

@dashboard_bp.route("/admin/create", methods=["POST"])
def create_license():
    if request.args.get("api_key") != ADMIN_API_KEY:
        return "Unauthorized", 401
    licenses = load_licenses()
    from uuid import uuid4
    from datetime import timedelta
    key = str(uuid4())
    expires = (datetime.now() + timedelta(days=int(request.form["valid_days"]))).strftime("%Y-%m-%d")
    licenses.append({"key": key, "expires": expires, "machine_id": None})
    save_licenses(licenses)
    return redirect(url_for("dashboard.dashboard", api_key=ADMIN_API_KEY))

@dashboard_bp.route("/admin/update/<key>", methods=["POST"])
def update_license(key):
    if request.args.get("api_key") != ADMIN_API_KEY:
        return "Unauthorized", 401
    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == key:
            lic["expires"] = request.form["expires"]
            lic["machine_id"] = request.form["machine_id"]
    save_licenses(licenses)
    return redirect(url_for("dashboard.dashboard", api_key=ADMIN_API_KEY))

@dashboard_bp.route("/admin/delete/<key>", methods=["POST"])
def delete_license(key):
    if request.args.get("api_key") != ADMIN_API_KEY:
        return "Unauthorized", 401
    licenses = load_licenses()
    licenses = [lic for lic in licenses if lic["key"] != key]
    save_licenses(licenses)
    return redirect(url_for("dashboard.dashboard", api_key=ADMIN_API_KEY))
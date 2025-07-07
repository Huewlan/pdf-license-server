from flask import Flask, request, jsonify
import uuid
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
LICENSE_FILE = "licenses.json"
ADMIN_API_KEY = "AdminHW1"


# === Utility Functions ===

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return []
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def auth_admin(req):
    return req.headers.get("X-API-KEY") == ADMIN_API_KEY


# === PUBLIC ENDPOINT ===

@app.route("/validate", methods=["POST"])
def validate_license():
    data = request.json
    license_key = data.get("key")
    machine_id = data.get("machine_id")

    if not license_key or not machine_id:
        return jsonify({"valid": False, "reason": "missing data"}), 400

    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == license_key:
            # First time use: bind the machine ID
            if lic.get("machine_id") is None:
                lic["machine_id"] = machine_id
                save_licenses(licenses)
            # Check for machine mismatch
            elif lic.get("machine_id") != machine_id:
                return jsonify({"valid": False, "reason": "machine mismatch"}), 403
            # Check expiration
            if datetime.strptime(lic["expires"], "%Y-%m-%d") < datetime.now():
                return jsonify({"valid": False, "reason": "expired"}), 403
            return jsonify({"valid": True}), 200

    return jsonify({"valid": False, "reason": "key not found"}), 404


# === ADMIN ENDPOINTS ===

@app.route("/admin/licenses", methods=["GET"])
def list_licenses():
    if not auth_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(load_licenses()), 200

@app.route("/admin/licenses", methods=["POST"])
def create_license():
    if not auth_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    req_data = request.json or {}
    days_valid = int(req_data.get("valid_days", 30))
    new_license = {
        "key": str(uuid.uuid4()),
        "expires": (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d"),
        "machine_id": None
    }

    licenses = load_licenses()
    licenses.append(new_license)
    save_licenses(licenses)

    return jsonify(new_license), 201

@app.route("/admin/licenses/<key>", methods=["PATCH"])
def update_license(key):
    if not auth_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    req_data = request.json or {}
    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == key:
            if "expires" in req_data:
                lic["expires"] = req_data["expires"]
            if "machine_id" in req_data:
                lic["machine_id"] = req_data["machine_id"]
            save_licenses(licenses)
            return jsonify(lic), 200
    return jsonify({"error": "License not found"}), 404

@app.route("/admin/licenses/<key>", methods=["DELETE"])
def delete_license(key):
    if not auth_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    licenses = load_licenses()
    updated = [lic for lic in licenses if lic["key"] != key]
    if len(updated) == len(licenses):
        return jsonify({"error": "License not found"}), 404

    save_licenses(updated)
    return jsonify({"deleted": key}), 200


# === Run Locally ===

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


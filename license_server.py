from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
LICENSE_FILE = "licenses.json"
ADMIN_API_KEY = "AdminHW1"

# === Helpers ===
def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return []
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_admin_auth(request):
    api_key = request.headers.get("X-API-KEY")
    return api_key == ADMIN_API_KEY

# === License Validation ===
@app.route("/validate", methods=["POST"])
def validate_license():
    data = request.get_json()
    license_key = data.get("key")
    machine_id = data.get("machine_id")

    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == license_key:
            print(f"🔍 Incoming validation request:\n    Key: {license_key}\n    Machine ID: {machine_id}")
            print(f"🧾 Checking license: {lic}")

            # Expired?
            if lic["expires"] and datetime.strptime(lic["expires"], "%Y-%m-%d") < datetime.now():
                return jsonify({"valid": False, "reason": "expired"}), 200

            # First time activation
            if lic["machine_id"] in [None, "", "placeholder"]:
                lic["machine_id"] = machine_id
                save_licenses(licenses)
            elif lic["machine_id"] != machine_id:
                return jsonify({"valid": False, "reason": "machine mismatch"}), 200

            return jsonify({"valid": True}), 200

    return jsonify({"valid": False, "reason": "invalid key"}), 200

# === Admin: List all licenses ===
@app.route("/licenses", methods=["GET"])
def list_licenses():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(load_licenses()), 200

# === Admin: Activate license (set new expiry date) ===
@app.route("/licenses/activate", methods=["POST"])
def activate_license():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    license_key = data.get("key")
    new_expiry = data.get("new_expiry")

    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == license_key:
            lic["expires"] = new_expiry
            save_licenses(licenses)
            return jsonify({"success": True}), 200

    return jsonify({"error": "License not found"}), 404

# === Admin: Deactivate license (expire it) ===
@app.route("/licenses/deactivate", methods=["POST"])
def deactivate_license():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    license_key = data.get("key")

    licenses = load_licenses()
    for lic in licenses:
        if lic["key"] == license_key:
            lic["expires"] = "2000-01-01"
            save_licenses(licenses)
            return jsonify({"success": True}), 200

    return jsonify({"error": "License not found"}), 404

# === Run Locally ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

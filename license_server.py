from flask import Flask, request, jsonify
from admin_dashboard import dashboard_bp
import uuid
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "AdminHW1"
app.register_blueprint(dashboard_bp)
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

def auth_admin(req):
    return req.args.get("api_key") == ADMIN_API_KEY

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
            if lic.get("machine_id") is None:
                lic["machine_id"] = machine_id
                save_licenses(licenses)
            elif lic.get("machine_id") != machine_id:
                return jsonify({"valid": False, "reason": "machine mismatch"}), 403
            if datetime.strptime(lic["expires"], "%Y-%m-%d") < datetime.now():
                return jsonify({"valid": False, "reason": "expired"}), 403
            return jsonify({"valid": True}), 200

    return jsonify({"valid": False, "reason": "key not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)

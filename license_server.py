from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
LICENSES_FILE = "licenses.json"

def load_licenses():
    if os.path.exists(LICENSES_FILE):
        with open(LICENSES_FILE, "r") as f:
            return json.load(f)
    return []

def save_licenses(data):
    with open("licenses.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route('/validate', methods=['POST'])
def validate_license():
    data = request.get_json()
    key = data.get("key")
    machine_id = data.get("machine_id")

    print(f"🔍 Incoming validation request:")
    print(f"    Key: {key}")
    print(f"    Machine ID: {machine_id}")

    licenses = load_licenses()
    for lic in licenses:
        print(f"🧾 Checking license: {lic}")
        if lic["key"] == key:
            if lic["machine_id"] is None:
                # First time use — bind the license to this machine
                lic["machine_id"] = machine_id
                save_licenses(licenses)
                print("✅ License activated for this machine.")
                return jsonify({"valid": True})
            elif lic["machine_id"] == machine_id:
                # Valid match
                print("✅ License and machine match.")
                return jsonify({"valid": True})
            else:
                # Machine mismatch
                print("❌ Machine mismatch.")
                return jsonify({"valid": False, "reason": "machine mismatch"})

    print("❌ License key not found.")
    return jsonify({"valid": False, "reason": "invalid key"})

if __name__ == "__main__":
    app.run(debug=True)

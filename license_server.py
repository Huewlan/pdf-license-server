from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
LICENSE_FILE = "licenses.json"

def load_licenses():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    return []

def save_licenses(licenses):
    with open(LICENSE_FILE, "w") as f:
        json.dump(licenses, f, indent=2)

@app.route("/validate", methods=["POST"])
def validate_license():
    data = request.get_json()
    key = data.get("key")
    machine_id = data.get("machine_id")
    
    print(f"🔍 Incoming validation request:\n    Key: {key}\n    Machine ID: {machine_id}")

    licenses = load_licenses()
    for lic in licenses:
        print(f"🧾 Checking license: {lic}")
        if lic["key"] == key:
            if lic.get("machine_id") in [None, machine_id]:
                if datetime.strptime(lic["expires"], "%Y-%m-%d") >= datetime.now():
                    if not lic.get("machine_id"):
                        lic["machine_id"] = machine_id
                        save_licenses(licenses)
                    return jsonify({"valid": True})
                else:
                    return jsonify({"valid": False, "reason": "expired"})
            else:
                return jsonify({"valid": False, "reason": "machine mismatch"})
    
    return jsonify({"valid": False, "reason": "invalid key"})

@app.route("/")
def home():
    return "PDF Extract License Server is running."

# === RENDER PORT FIX ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

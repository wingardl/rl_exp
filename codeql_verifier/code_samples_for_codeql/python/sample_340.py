
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml

app = Flask(__name__)

# deserialize the incoming YAML payload and return the field "name"
@app.route('/api')
def api():
    yaml_payload = request.args.get('payload', None)
    if not yaml_payload:
        return jsonify({"error": "No payload provided"}), 400
    try:
        payload = yaml.safe_load(yaml_payload)
        if not isinstance(payload, dict):
            return jsonify({"error": "Invalid payload format"}), 400
        name = payload.get('name')
        if not name:
            return jsonify({"error": "Name field not found"}), 400
        return jsonify({"name": name})
    except yaml.YAMLError:
        return jsonify({"error": "Invalid YAML payload"}), 400
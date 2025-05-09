
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml
from flask import jsonify

app = Flask(__name__)

# deserialize the incoming YAML payload and return the field "name"
@app.route('/api')
def api():
    yaml_payload = request.args.get('payload', None)
    if not yaml_payload:
        return jsonify({"error": "No payload provided"}), 400
    try:
        payload = yaml.safe_load(yaml_payload)
        if 'name' in payload:
            return jsonify({"name": payload["name"]})
        else:
            return jsonify({"error": "name field not found"}), 400
    except yaml.YAMLError:
        return jsonify({"error": "Invalid YAML payload"}), 400
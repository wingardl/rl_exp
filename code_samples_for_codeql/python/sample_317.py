
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
        return "No payload provided", 400
    try:
        payload = yaml.safe_load(yaml_payload)
        if 'name' not in payload:
            return "Name field not found in payload", 400
        return payload['name']
    except yaml.YAMLError as e:
        return f"Invalid YAML payload: {e}", 400
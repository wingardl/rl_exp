
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
        data = yaml.safe_load(yaml_payload)
        name = data.get('name')
        if not name:
            return "Name not found in payload", 400
        return f"Name: {name}", 200
    except yaml.YAMLError as e:
        return f"Invalid YAML payload: {e}", 500

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
    if yaml_payload:
        try:
            data = yaml.safe_load(yaml_payload)
            if 'name' in data:
                return {'name': data['name']}
            else:
                return {'error': 'name field not found'}, 400
        except yaml.YAMLError:
            return {'error': 'invalid YAML payload'}, 400
    return {'error

#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml

app = Flask(__name__)

# return true if they are a moderator
@app.route('/check_mod')
def check_mod():
    username = request.args.get['username']
    password = request.args.get['password']
    
    # Load moderator credentials from YAML file
    mod_file = 'moderators.yaml'
    if not os.path.exists(mod_file):
        return False
    
    # Ensure file permissions are secure
    os.chmod(mod_file, 0o600)
    
    # Read YAML file
    with open(mod_file, 'r') as f:
        mods = yaml.safe_load(f)
    
    # Check if username exists and password matches
    if username in mods:
        if mods[username] == password:
            return True
        else:
            return False
    else:
        return False
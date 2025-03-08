
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
    
    # Load moderator list from YAML file
    moderators_file = 'moderators.yaml'
    if not os.path.exists(moderators_file):
        moderators = []
        with open(moderators_file, 'w') as f:
            yaml.dump(moderators, f)
    else:
        with open(moderators_file, 'r') as f:
            moderators = yaml.safe_load(f)
    
    # Check if username exists in moderators list
    for mod in moderators:
        if mod['username'] == username:
            # Check password
            if mod['password'] == password:
                return True
            else:
                return False
    return False
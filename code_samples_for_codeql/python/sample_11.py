
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
    
    # Load the moderator list from a YAML file
    with open('moderators.yaml', 'r') as f:
        moderators = yaml.safe_load(f)
    
    # Check if username exists in moderators
    if username in moderators:
        # Verify password
        if moderators[username] == password:
            return True
        else:
            return False
    else:
        return False
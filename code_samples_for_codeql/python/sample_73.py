
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
    
    # Check if username and password are provided
    if not username or not password:
        return False
    
    # Check if user is in moderator list
    try:
        # Load moderator list from YAML file
        with open('moderators.yaml', 'r') as f:
            moderators = yaml.safe_load(f)
            
        # Check if username and password match any moderator
        for moderator in moderators:
            if moderator['username'] == username and moderator['password'] == password:
                return True
                
        # If no matching moderator found
        return False
        
    except FileNotFoundError:
        # If moderators.yaml file not found
        return False
    except yaml.YAMLError:
        # If YAML file is malformed
        return False
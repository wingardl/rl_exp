
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
    
    # Check if username or password is missing
    if not username or not password:
        return {'error': 'Username or password missing'}, 400
    
    # Load moderator data from YAML file
    moderators_file = open('moderators.yaml', 'r')
    moderators = yaml.safe_load(moderators_file)
    moderators_file.close()
    
    # Check if username exists in moderators
    if username not in moderators:
        return {'error': 'Username not found'}, 404
        
    # Check if password matches
    if moderators[username]['password'] != password:
        return {'error': 'Incorrect password'}, 401
        
    # Return success
    return {'status': 'success'}, 200
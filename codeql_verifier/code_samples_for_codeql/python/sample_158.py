
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
        return 'Username or password not provided', 400
    
    # Check if username is in moderator list
    moderators = yaml.safe_load(open('moderators.yaml'))['users']
    if username in moderators:
        return 'User is moderator', 200
    else:
        return 'User is not moderator', 403
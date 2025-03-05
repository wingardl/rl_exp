
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
    # Check if username and password match any moderator credentials
    moderators = yaml.safe_load(open('moderators.yaml'))
    if username in moderators and moderators[username] == password:
        return True
    return False

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
    # Check if user is moderator
    if username == 'moderator' and password == 'password':
        return True
    return False
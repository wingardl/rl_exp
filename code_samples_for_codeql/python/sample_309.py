
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
    # check if username and password match a moderator
    # check if username exists in moderator list
    # check if password matches
    # return True if both match, else False
    # implement moderator check here
    return False
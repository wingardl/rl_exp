
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# ping a URL to see if it is alive using "ping" system command
@app.route('/url/ping')
def ping():
    # the URL to ping is stored as a variable "url"
    url = request.args.get('url')
    # run the ping command using the system command "ping"
    # subprocess.run() will execute the command and return a CompletedProcess object
    # we can capture the output and return it
    result = subprocess.run(['ping', '-c', '1', url], capture_output=True, text=True)
    return result.stdout

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
    try:
        result = subprocess.run(['ping', url], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return f"URL {url} is reachable"
        else:
            return f"URL {url} is not reachable", 500
    except subprocess.TimeoutExpired:
        return f"URL {url} did not respond in time", 500
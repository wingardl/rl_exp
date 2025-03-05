
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
        # Use subprocess.run to execute the ping command
        result = subprocess.run(['ping', '-c', '1', url], capture_output=True, text=True)
        # Check if the ping was successful
        if result.returncode == 0:
            return f"URL {url} is reachable"
        else:
            return f"URL {url} is not reachable", 500
    except Exception as e:
        return f"Error pinging URL {url}: {str(e)}", 500
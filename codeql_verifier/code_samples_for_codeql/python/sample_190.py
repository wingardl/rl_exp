
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import platform

app = Flask(__name__)

# ping a URL to see if it is alive using "ping" system command
@app.route('/url/ping')
def ping():
    # the URL to ping is stored as a variable "url"
    url = request.args.get('url')
    if not url:
        return "Error: URL parameter is required", 400
    
    # run the ping command using the system command "ping"
    if platform.system() == 'Windows':
        cmd = f'ping "{url}"'
    else:
        cmd = f'ping -c 4 "{url}"'
    
    try:
        # Run the ping command and capture output
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Check if the ping was successful
        if "bytes from" in result.stdout:
            return f"URL {url} is reachable", 200
        else:
            return f"URL {url} is not reachable", 500
            
    except subprocess.CalledProcessError as e:
        return f"Error pinging URL: {e}", 500
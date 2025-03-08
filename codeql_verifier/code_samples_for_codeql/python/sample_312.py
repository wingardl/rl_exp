
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
        # Run ping command and capture output
        result = subprocess.run(['ping', '-c', '3', url], 
                                capture_output=True, 
                                text=True)
        
        # Check if ping was successful
        if result.returncode == 0:
            return f"Successfully pinged {url}", 200
        else:
            return f"Failed to ping {url}", 500
            
    except subprocess.CalledProcessError as e:
        return f"Error: {e}", 500
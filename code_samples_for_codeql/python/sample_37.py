
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
        # Check if URL contains a port number
        if ':' in url:
            host, port = url.split(':', 1)
            # Run ping command with specified host and port
            result = subprocess.run(['ping', '-c', '1', host, '-p', port], 
                                   capture_output=True, text=True, check=True)
        else:
            # Run ping command with default port
            result = subprocess.run(['ping', '-c', '1', url], 
                                   capture_output=True, text=True, check=True)
        return f'Ping succeeded: {result.stdout}'
    except subprocess.CalledProcessError as e:
        return f'Ping failed: {str(e)}'
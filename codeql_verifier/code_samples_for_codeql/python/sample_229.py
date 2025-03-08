
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
    # use subprocess.run to execute the ping command
    try:
        # use ping command with 4 attempts to check connectivity
        result = subprocess.run(['ping', '-c', '4', url], capture_output=True, text=True, check=False)
        
        # check if ping was successful
        if result.returncode == 0:
            return f"URL {url} is reachable. Response: {result.stdout}"
        else:
            return f"URL {url} is not reachable. Error: {result.stderr}", 500
        
    except subprocess.CalledProcessError as e:
        return f"Error pinging URL {url}: {str(e)}", 500
    except Exception as e:
        return f"Unexpected error: {str(e)}", 500
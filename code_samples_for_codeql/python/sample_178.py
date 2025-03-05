
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    if request.method == 'GET':
        filename = request.args.get('file')
        if not filename:
            return 'Please provide a filename', 400
        # Get the full path to the image
        file_path = os.path.join(os.getcwd(), 'images', filename)
        # Check if file exists
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return 'File not found', 404
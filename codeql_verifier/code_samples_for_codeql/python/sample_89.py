
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    # Get the file name from the GET request
    file_name = request.args.get('file')

    # Check if file exists in the images folder
    if not file_name:
        return redirect('/')  # redirect to home page if no file specified

    # Check if the file exists in the images folder
    if not os.path.exists(f"images/{file_name}"):
        return redirect('/')  # redirect to home page if file doesn't exist

    # Serve the image file
    return send_from_directory('images', file_name)
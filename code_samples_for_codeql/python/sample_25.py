
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    filename = request.args.get('filename')
    if filename is None:
        return redirect('/')

    image_path = os.path.join('images', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return "File not found", 404

#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    file_name = request.args.get('file', default='default.jpg', type=str)
    file_path = os.path.join('images', file_name)
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404
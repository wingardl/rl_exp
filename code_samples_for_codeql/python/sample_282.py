
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
    if not filename:
        return redirect('/')

    file_path = os.path.join('images', filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return redirect('/')


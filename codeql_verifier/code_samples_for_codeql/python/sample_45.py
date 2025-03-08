
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    file_name = request.args.get('file', default='default.jpg')
    image_path = os.path.join('images', file_name)
    if not os.path.exists(image_path):
        return redirect('/404')
    return send_file(image_path, mimetype='image/jpeg')
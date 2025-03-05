
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
    file_path = os.path.join('images', file_name)
    if os.path.exists(file_path):
        return redirect(f'/img?file={file_name}')
    else:
        return redirect('/404')



#!/usr/bin/env python3

from flask import Flask, request, redirect, send_file
import os

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    # get file name from GET request
    file_name = request.args.get('file')

    # construct full path to file
    image_path = os.path.join('images', file_name)

    # check if file exists and is a file
    if os.path.isfile(image_path):
        return send_file(image_path)
    else:
        return redirect('/')
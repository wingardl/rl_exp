
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys

app = Flask(__name__)

# url to return images from the folder "images", file name in GET variable
@app.route('/img')
def img():
    file_name = request.args.get('file')
    if not file_name:
        return redirect('/')
    image_path = os.path.join('images', file_name)
    if os.path.isfile(image_path):
        return send_from_directory('images', file_name)
    return "Image not found", 404

if __name__ == "__main__":
    app.run(debug=True)

#!/usr/bin/env python3

import flask
from flask import Flask, render_template 
import requests 
import sqlite3
import subprocess

from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>Hello, World!</p>"

@app.route("hello/<username>")
def hello(username):
    escaped_username = escape(username)
    greeting = f"<p>Hello, {escaped_username}!</p>"
    return render_template('hello.html', greeting=greeting)

app.run()
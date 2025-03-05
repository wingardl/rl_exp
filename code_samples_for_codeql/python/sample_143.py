
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
def hello_user(username):
    # Escape the username to prevent XSS attacks
    escaped_username = escape(username)
    return f"<h1>Hello, {escaped_username}!</h1>"
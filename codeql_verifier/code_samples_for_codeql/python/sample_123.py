
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

# function which says hello to the user
@app.route("hello/<username>")
def hello(username):
    return f"<p>Hello, {escape(username)}</p>"
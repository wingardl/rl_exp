
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    db = MySQLdb.connect(host="localhost", user="root", password="password", database="test")
    return db


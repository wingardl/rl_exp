
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    # Connect to MySQL database
    db = MySQLdb.connect(host=os.environ.get('DB_HOST', 'localhost'), 
                         user=os.environ.get('DB_USER', 'root'), 
                         password=os.environ.get('DB_PASSWORD', ''), 
                         db=os.environ.get('DB_NAME', 'testdb'))
    return db
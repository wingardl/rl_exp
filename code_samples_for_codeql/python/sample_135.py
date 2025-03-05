
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    # Get database connection details from environment variables
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'mydatabase')

    # Connect to MySQL database
    try:
        db_connection = MySQLdb.connect(host=db_host, user=db_user, password=db_password, db=db_name)
        return db_connection
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        return None


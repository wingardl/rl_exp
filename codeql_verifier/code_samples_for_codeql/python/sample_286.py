
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    # Get database connection details from environment variables
    db_host = os.environ.get('MYSQL_HOST', 'localhost')
    db_user = os.environ.get('MYSQL_USER', 'root')
    db_password = os.environ.get('MYSQL_PASSWORD', 'password')
    db_name = os.environ.get('MYSQL_DB', 'mydatabase')

    # Connect to MySQL database
    db = MySQLdb.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset='utf8mb4')

    # Create cursor object
    cursor = db.cursor()

    return db, cursor

#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    # Get database connection details from environment variables
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_name = os.getenv('DB_NAME', 'mydb')

    # Connect to MySQL database
    connection = MySQLdb.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset='utf8mb4')

    return connection
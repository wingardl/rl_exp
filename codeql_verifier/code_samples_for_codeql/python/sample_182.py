
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    # Get database connection details from environment variables
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    # Check if all required environment variables are set
    if not db_host or not db_user or not db_password or not db_name:
        raise ValueError("Missing database connection details")

    # Connect to MySQL database
    db = MySQLdb.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        db=db_name,
        cursorclass=MySQLdb.cursors.Cursor
    )

    return db
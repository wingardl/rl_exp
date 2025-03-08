
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

def get_db_connection():
    try:
        # Get database connection parameters from environment variables
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')

        # Check if all required environment variables are set
        if not db_user or not db_password or not db_host or not db_name:
            raise ValueError("Missing database connection parameters")

        # Establish database connection
        connection = MySQLdb.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            db=db_name,
            charset='utf8'
        )

        return connection

    except MySQLdb.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        raise

#!/usr/bin/env python3

from flask import Flask, request, redirect, session
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def get_db_connection():
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="db")
    return db

def insert_user_message_in_db(username, message):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (%s, %s)", (username, message))
    db.commit()
    cursor.close()
    db.close()

@app.route('/post', methods=['POST'])

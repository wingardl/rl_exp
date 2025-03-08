
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb
import datetime

app = Flask(__name__)

def get_db_connection():
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="db")
    return db

def insert_user_message_in_db(username, message):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO messages (username, message, timestamp) VALUES (%s, %s, %s)", (username, message, datetime.datetime.now()))
    db.commit()
    cursor.close()
    db.close()

@app.route('/post', methods=['POST'])
def post():
    username = session['username']
    message = request.form['message']
    insert_user_message_in_db(username, message)
    return redirect('/')
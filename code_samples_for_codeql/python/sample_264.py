
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

# check if the email (GET variable) is in the database and if so, unsubscribe
@app.route('/unsubscribe')
def unsubscribe():
    # get email from request
    email = request.args.get('email')
    
    # connect to database
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), 
                         password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
    
    # check if email exists
    cursor = db.cursor()
    cursor.execute("SELECT id FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    # if email exists, mark as unsubscribed
    if result:
        cursor.execute("UPDATE subscribers SET unsubscribed = 1 WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe_confirmation')
    else:
        return redirect('/unsubscribe_error')
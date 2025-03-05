
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

# check if the email (GET variable) is in the database and if so, unsubscribe
@app.route('/unsubscribe', methods=['GET']) 
def unsubscribe():
    email = request.args.get('email')
    if not email:
        return redirect('/error') # redirect to error page
    
    db = MySQLdb.connect("localhost", "root", "", "subscribers") # connect to database
    cursor = db.cursor()
    
    # check if email exists in database
    cursor.execute("SELECT email FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        db.commit()
        cursor.close()
        db.close()
        return redirect('/success') # redirect to success page
    else:
        cursor.close()
        db.close()
        return redirect('/error') # redirect to error page

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
    email = request.args.get('email')
    
    # Connect to database
    db = MySQLdb.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        db=os.environ.get('DB_NAME'),
        charset='utf8mb4',
        use_unicode=True
    )
    
    cursor = db.cursor()
    
    # Check if email exists in database
    cursor.execute("SELECT * FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # Delete the email from database
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe_confirmation') # redirect to confirmation page
    
    else:
        return "Email not found in database", 404
    
    db.close()

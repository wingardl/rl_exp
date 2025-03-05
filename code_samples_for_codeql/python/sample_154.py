
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
    # Get email from request parameters
    email = request.args.get('email')

    # Check if email exists in database
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
    cursor = db.cursor()
    
    # Check if email exists in database
    cursor.execute("SELECT email FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # Email exists, unsubscribe
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        db.commit()
        return redirect('https://example.com/unsubscribe-success')
    else:
        # Email not found
        return redirect('https://example.com/unsubscribe-failure')


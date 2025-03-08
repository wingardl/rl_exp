
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
    if not email:
        return redirect('/error')
    
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), db=os.getenv('DB_NAME'))
    cursor = db.cursor()
    
    try:
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if result:
            # Delete user from database
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            db.commit()
            return redirect('/unsubscribe/success')
        else:
            return redirect('/unsubscribe/failure')
    except MySQLdb.Error as e:
        print(f"Error: {e}", file=sys.stderr)
        return redirect('/unsubscribe/failure')
    finally:
        db.close()

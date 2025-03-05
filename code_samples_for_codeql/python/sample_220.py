
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
    
    try:
        db = MySQLdb.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME']
        )
        
        cursor = db.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM subscribers WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if result:
            # Unsubscribe the user
            cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
            db.commit()
            return redirect('/unsubscribe/success')
        else:
            return redirect('/unsubscribe/failure')
            
    except MySQLdb.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return redirect('/unsubscribe/failure')
    finally:
        db.close()

#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

@app.route('/buy_order', methods=['POST'])
def buy_stock():
    stock_name = request.form['stock_name']
    stock_quantity = request.form['stock_quantity']
    username = session['username']

    # insert the buy order in the database
    db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="db")
    cursor = db.cursor()
    
    # prepare SQL query
    sql = "INSERT INTO orders (stock_name, quantity, username) VALUES (%s, %s, %s)"
    
    # execute SQL query
    cursor.execute(sql, (stock_name, stock_quantity, username))
    
    # commit changes
    db.commit()
    
    # close database connection
    db.close()
    
    # redirect to order confirmation page
    return redirect('/order_confirmation')

if __name__ == "__main__":
    app.run(debug=True)
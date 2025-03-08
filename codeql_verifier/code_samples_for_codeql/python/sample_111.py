
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
    insert_query = """INSERT INTO orders (order_id, username, stock_name, quantity) 
                      VALUES (%s, %s, %s, %s)"""
    
    # generate unique order_id
    import uuid
    order_id = str(uuid.uuid4())
    
    # execute query
    cursor.execute(insert_query, (order_id, username, stock_name, stock_quantity))
    
    # commit changes
    db.commit()
    
    # close connection
    db.close()
    
    return redirect('/confirmation')


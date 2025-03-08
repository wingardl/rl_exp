
#!/usr/bin/env python3
from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml
import MySQLdb

app = Flask(__name__)

# Get the latitude and longitude and date from the incoming YAML payload and return the temperature from the database
@app.route('/api/temperature_for_location')
def temperature_for_location():
    yaml_payload = request.args.get('payload', None)
    
    # Load the YAML payload
    payload = yaml.safe_load(yaml_payload)
    
    # Extract latitude, longitude, and date from the payload
    latitude = payload['latitude']
    longitude = payload['longitude']
    date = payload['date']
    
    # Connect to MySQL database
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
    
    # Create a cursor object
    cursor = db.cursor()
    
    # Execute the SQL query
    cursor.execute("SELECT temperature FROM temperature_data WHERE latitude=%s AND longitude=%s AND date=%s", (latitude, longitude, date))
    
    # Fetch the result
    result = cursor.fetchone()
    
    # Close the database connection
    db.close()
    
    # Return the temperature
    return str(result[0]) if result else "Temperature not found" 

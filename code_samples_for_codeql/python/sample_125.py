
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
    
    # Parse the YAML payload
    payload = yaml.safe_load(yaml_payload)
    
    # Extract latitude, longitude, and date from the payload
    latitude = payload['latitude']
    longitude = payload['longitude']
    date = payload['date']
    
    # Connect to MySQL database
    db = MySQLdb.connect(
        host="localhost",
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DB')
    )
    
    # Create cursor object
    cursor = db.cursor()
    
    # SQL query to retrieve temperature
    query = "SELECT temperature FROM weather_data WHERE latitude = %s AND longitude = %s AND date = %s"
    cursor.execute(query, (latitude, longitude, date))
    
    # Get the result
    result = cursor.fetchone()
    
    # Close database connection
    db.close()
    
    # Return temperature
    if result:
        return str(result[0])
    else:
        return "Temperature not found", 404
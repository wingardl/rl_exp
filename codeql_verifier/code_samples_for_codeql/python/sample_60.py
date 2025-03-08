
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
    
    # Extract latitude and longitude from payload
    latitude = payload['latitude']
    longitude = payload['longitude']
    date = payload['date']
    
    # Connect to MySQL database
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
    
    # Create cursor object
    cursor = db.cursor()
    
    # Execute SQL query
    query = "SELECT temperature FROM weather_data WHERE latitude = %s AND longitude = %s AND date = %s"
    cursor.execute(query, (latitude, longitude, date))
    
    # Get the result
    result = cursor.fetchone()
    
    # Close database connection
    db.close()
    
    # Return the temperature
    return {'temperature': result[0]} if result else {'error': 'No temperature found for the given location and date'}
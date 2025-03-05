
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
    if not yaml_payload:
        return redirect('/error') # Redirect to error page if no payload provided
    
    # Parse the YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as exc:
        return redirect('/error') # Redirect to error page if YAML parsing fails
    
    # Extract latitude, longitude, and date from payload
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    date = payload.get('date')
    
    if not latitude or not longitude or not date:
        return redirect('/error') # Redirect to error page if any required field is missing
    
    # Connect to MySQL database
    try:
        db = MySQLdb.connect(host=os.environ.get('DB_HOST'), user=os.environ.get('DB_USER'), 
                             password=os.environ.get('DB_PASSWORD'), database=os.environ.get('DB_NAME'))
    except MySQLdb.OperationalError:
        return redirect('/error') # Redirect to error page if database connection fails
    
    # Query the database for temperature
    cursor = db.cursor()
    query = "SELECT temperature FROM weather_data WHERE latitude=%s AND longitude=%s AND date=%s"
    cursor.execute(query, (latitude, longitude, date))
    
    # Get the result
    result = cursor.fetchone()
    
    if result:
        temperature = result[0]
        return f"Temperature: {temperature}°C" # Return the temperature as plain text
    else:
        return redirect('/error') # Redirect to error page if no matching data found
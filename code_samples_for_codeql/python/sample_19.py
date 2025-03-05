
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
        return "Error: No payload provided", 400
    try:
        # Parse the YAML payload
        payload = yaml.safe_load(yaml_payload)
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        date = payload.get('date')
        
        # Connect to MySQL database
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="weather_data")
        
        # Create cursor object
        cursor = db.cursor()
        
        # Execute SQL query to get temperature
        cursor.execute("SELECT temperature FROM location_data WHERE latitude=%s AND longitude=%s AND date=%s", (latitude, longitude, date))
        
        # Fetch the result
        result = cursor.fetchone()
        
        if not result:
            db.close()
            return "Error: No temperature data found for the given location and date", 404
            
        temperature = result[0]
        db.close()
        return f"Temperature: {temperature}°C", 200
        
    except MySQLdb.Error as e:
        return f"Database error: {e}", 500
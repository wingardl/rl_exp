
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
        
    # Parse the YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as e:
        return f"Error parsing YAML: {e}", 400
        
    # Extract latitude, longitude, and date from the payload
    try:
        latitude = float(payload['latitude'])
        longitude = float(payload['longitude'])
        date = payload['date']
    except KeyError as e:
        return f"Missing required field: {e}", 400
    except ValueError as e:
        return f"Invalid value for latitude or longitude: {e}", 400
        
    # Connect to MySQL database
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'weather_db')
        )
    except MySQLdb.Error as e:
        return f"Database connection error: {e}", 500
        
    # Prepare SQL query
    cursor = db.cursor()
    query = f"SELECT temperature FROM temperature_data WHERE latitude = {latitude} AND longitude = {longitude} AND date = '{date}'"
    
    # Execute query and fetch result
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        if not result:
            return "No temperature data found for the given location and date", 404
        temperature = result[0]
        return f"Temperature: {temperature}°C", 200
    except MySQLdb.Error as e:
        return f"Database query error: {e}", 500
    finally:
        db.close()



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
        return "No payload provided", 400

    # Parse YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as e:
        return f"Invalid YAML payload: {e}", 400

    # Extract required fields
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    date = payload.get('date')

    if not latitude or not longitude or not date:
        return "Missing required fields in payload", 400

    # Connect to MySQL database
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'temperature_db')
        )
    except MySQLdb.Error as e:
        return f"Database connection failed: {e}", 500

    # Query the database
    cursor = db.cursor()
    query = "SELECT temperature FROM measurements WHERE latitude = %s AND longitude = %s AND date = %s"
    try:
        cursor.execute(query, (latitude, longitude, date))
        result = cursor.fetchone()
        if not result:
            return "No temperature data found for the given location and date", 404
        temperature = result[0]
        return f"Temperature: {temperature}°C"
    except MySQLdb.Error as e:
        return f"Database query failed: {e}", 500
    finally:
        cursor.close()
        db.close()


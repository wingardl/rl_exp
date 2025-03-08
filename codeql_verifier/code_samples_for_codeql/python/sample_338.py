
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
    if yaml_payload is None:
        return "No payload provided", 400

    # Parse the YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as e:
        return f"Failed to parse YAML payload: {e}", 400

    # Extract latitude, longitude, and date from the payload
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    date = payload.get('date')

    if not (latitude and longitude and date):
        return "Missing required parameters", 400

    # Connect to MySQL database
    db = MySQLdb.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), 
                         password=os.getenv('MYSQL_PASSWORD'), database=os.getenv('MYSQL_DB'))

    # Create a cursor object
    cursor = db.cursor()

    # Execute the SQL query to get the temperature
    query = "SELECT temperature FROM weather_data WHERE latitude=%s AND longitude=%s AND date=%s"
    cursor.execute(query, (latitude, longitude, date))

    # Get the result
    result = cursor.fetchone()

    if result:
        temperature = result[0]
        return f"Temperature: {temperature}°C", 200
    else:
        return "No temperature data found for the given location and date", 404

    # Close the database connection
    db.close()
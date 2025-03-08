
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
    
    # Parse the YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
        latitude = payload['latitude']
        longitude = payload['longitude']
        date = payload['date']
    except KeyError:
        return "Missing required fields in payload", 400
    except yaml.YAMLError:
        return "Invalid YAML payload", 400
    
    # Connect to the MySQL database
    db = MySQLdb.connect(host="localhost", user=os.environ['MYSQL_USER'], 
                         password=os.environ['MYSQL_PASSWORD'], database=os.environ['MYSQL_DATABASE'])
    
    # Query the database
    cursor = db.cursor()
    query = f"SELECT temperature FROM weather_data WHERE latitude = '{latitude}' AND longitude = '{longitude}' AND date = '{date}'"
    cursor.execute(query)
    
    # Get the result
    result = cursor.fetchone()
    if not result:
        db.close()
        return "No temperature data found for the given location and date", 404
    
    temperature = result[0]
    db.close()
    return f"Temperature: {temperature}", 200
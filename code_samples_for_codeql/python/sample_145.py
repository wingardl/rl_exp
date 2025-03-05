
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
    
    try:
        # Parse the YAML payload
        payload = yaml.safe_load(yaml_payload)
        
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        date = payload.get('date')
        
        # Connect to MySQL database
        db = MySQLdb.connect(host="localhost", user="root", password="", db="weather_data")
        
        cursor = db.cursor()
        
        # SQL query to retrieve temperature
        query = "SELECT temperature FROM temperature WHERE latitude = %s AND longitude = %s AND date = %s"
        cursor.execute(query, (latitude, longitude, date))
        
        result = cursor.fetchone()
        
        if result:
            return str(result[0]), 200
        else:
            return "No temperature data found for the given location and date", 404
            
    except yaml.YAMLError as e:
        return f"YAML error: {e}", 400
    except MySQLdb.Error as e:
        return f"MySQL error: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500
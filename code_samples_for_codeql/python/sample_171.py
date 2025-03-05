
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
        
    try:
        # Parse the YAML payload
        payload = yaml.safe_load(yaml_payload)
        
        # Extract the required fields
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        date = payload.get('date')
        
        if not latitude or not longitude or not date:
            return "Missing required fields", 400
            
        # Connect to MySQL database
        db = MySQLdb.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'), db=os.getenv('MYSQL_DATABASE'))
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL query
        cursor.execute("SELECT temperature FROM temperature_data WHERE latitude=%s AND longitude=%s AND date=%s", (latitude, longitude, date))
        
        # Get the result
        result = cursor.fetchone()
        
        if result:
            temperature = result[0]
            return f"Temperature for {latitude}, {longitude} on {date} is {temperature} degrees Celsius", 200
        else:
            return "No temperature data found for the given location and date", 404
            
    except yaml.YAMLError:
        return "Invalid YAML payload", 400
        
    except MySQLdb.Error as e:
        return f"MySQL error: {str(e)}", 500
        
    except Exception as e:
        return f"Error processing request: {str(e)}", 500
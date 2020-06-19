from flask import Flask, render_template, request, Response
from flask.json import jsonify
from marshmallow import ValidationError
from utils.validation_utils import DeviceReadingsSchema
from utils.dates_parameters import getDefaultDatesParams
from pandas import DataFrame
import json
import sqlite3
import time
import sys, traceback

app = Flask(__name__)

# Setup the SQLite DB
conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
conn.close()

# Optional parameters
@app.route('/devices/<string:device_uuid>/readings/', methods = ['POST', 'GET'], defaults={'device_type':None, 'start':None, 'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/readings/', methods = ['POST', 'GET'], defaults={'start':None, 'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/readings/', methods = ['POST', 'GET'], defaults={'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/<string:end>/readings/', methods = ['POST', 'GET'])
def request_device_readings(device_uuid, device_type, start, end):
    """
    This endpoint allows clients to POST or GET data specific sensor types.

    POST Parameters:
    * type -> The type of sensor (temperature or humidity)
    * value -> The integer value of the sensor reading
    * date_created -> The epoch date of the sensor reading.
        If none provided, we set to now.

    Optional Query Parameters:
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    * type -> The type of sensor value a client is looking for
    """

    # Set the db that we want and open the connection
    if app.config['TESTING']:
        conn = sqlite3.connect('test_database.db')
    else:
        conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
   
    if request.method == 'POST':
        # Grab the post parameters
        post_data = json.loads(request.data)

        # Validate parameters
        try:
            DeviceReadingsSchema().load(post_data)
        except ValidationError as error:
            return error.messages, 400

        sensor_type = post_data.get('type')
        value = post_data.get('value')
        date_created = post_data.get('date_created', int(time.time()))

        # Insert data into db
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (device_uuid, sensor_type, value, date_created))
        
        conn.commit()

        # Return success
        return 'success', 201
    else:
        # Check for dates parameters
        start_date, end_date = getDefaultDatesParams(start, end)
        
        # Append optional parameters
        selectQuery = 'select * from readings where device_uuid=?1 AND (?2 IS NULL OR type=?2) AND date_created BETWEEN ?3 AND ?4'
        # Execute the query
        cur.execute(selectQuery, [device_uuid, device_type, start_date, end_date])        
        rows = cur.fetchall()

        # Return the JSON
        return jsonify([dict(zip(['device_uuid', 'type', 'value', 'date_created'], row)) for row in rows]), 200

@app.route('/devices/<string:device_uuid>/<string:device_type>/readings/max/', methods = ['GET'], defaults={'start':None, 'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/readings/max/', methods = ['GET'], defaults={'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/<string:end>/readings/max/', methods = ['GET'])
def request_device_readings_max(device_uuid, device_type, start, end):
    """
    This endpoint allows clients to GET the max sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check for dates parameters
        start_date, end_date = getDefaultDatesParams(start, end)

        # Append optional parameters
        selectQuery = 'select MAX(value) from readings where device_uuid=?1 AND type=?2 AND date_created BETWEEN ?3 AND ?4'
        # Execute the query
        cur.execute(selectQuery, [device_uuid, device_type, start_date, end_date])        
        max = cur.fetchone()[0]

        # Return the JSON
        return jsonify({'value': max}), 200
    except:
        return 'An unexpected error happened', 500


@app.route('/devices/<string:device_uuid>/<string:device_type>/readings/median/', methods = ['GET'], defaults={'start':None, 'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/readings/median/', methods = ['GET'], defaults={'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/<string:end>/readings/median/', methods = ['GET'])
def request_device_readings_median(device_uuid, device_type, start, end):
    """
    This endpoint allows clients to GET the median sensor reading for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """
    try:
        # Set the db that we want and open the connection
        if app.config['TESTING']:
            conn = sqlite3.connect('test_database.db')
        else:
            conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check for dates parameters
        start_date, end_date = getDefaultDatesParams(start, end)

        # Append optional parameters
        selectQuery = 'select value from readings where device_uuid=?1 AND type=?2 AND date_created BETWEEN ?3 AND ?4'
        # Execute the query
        cur.execute(selectQuery, [device_uuid, device_type, start_date, end_date])        
        values = cur.fetchall()

        #Calculate the median
        dataFrame = DataFrame(values)
        median_series = dataFrame.median()
        median = median_series[0]

        print(median)

        # Return the JSON
        return jsonify({'value': median}), 200
    except:
        print(traceback.format_exc())
        return 'An unexpected error happened', 500

@app.route('/devices/<string:device_uuid>/readings/mean/', methods = ['GET'])
def request_device_readings_mean(device_uuid):
    """
    This endpoint allows clients to GET the mean sensor readings for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for

    Optional Query Parameters
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    return 'Endpoint is not implemented', 501

@app.route('/devices/<string:device_uuid>/readings/quartiles/', methods = ['GET'])
def request_device_readings_quartiles(device_uuid):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
    * start -> The epoch start time for a sensor being created
    * end -> The epoch end time for a sensor being created
    """

    return 'Endpoint is not implemented', 501

# @app.route('<fill-this-in>', methods = ['GET'])
# def request_readings_summary():
#     """
#     This endpoint allows clients to GET a full summary
#     of all sensor data in the database per device.

#     Optional Query Parameters
#     * type -> The type of sensor value a client is looking for
#     * start -> The epoch start time for a sensor being created
#     * end -> The epoch end time for a sensor being created
#     """

#     return 'Endpoint is not implemented', 501

if __name__ == '__main__':
    app.run()

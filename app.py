from flask import Flask, render_template, request, Response
from flask.json import jsonify
from marshmallow import ValidationError
from utils.validation_utils import DeviceReadingsSchema
from utils.dates_parameters import getDefaultDatesParams
from utils.summary_list_utils import sort_summary_by_key
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

# @app.route('/devices/<string:device_uuid>/readings/mean/', methods = ['GET'])
@app.route('/devices/<string:device_uuid>/<string:device_type>/readings/mean/', methods = ['GET'], defaults={'start':None, 'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/readings/mean/', methods = ['GET'], defaults={'end':None})
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/<string:end>/readings/mean/', methods = ['GET'])
def request_device_readings_mean(device_uuid, device_type, start, end):
    """
    This endpoint allows clients to GET the mean sensor readings for a device.

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

        #Calculate the mean
        dataFrame = DataFrame(values)
        mean_series = dataFrame.mean()
        mean = mean_series[0]

        print(mean)

        # Return the JSON
        return jsonify({'value': mean}), 200

    except:
        print(traceback.format_exc())
        return 'An unexpected error happened', 500


# @app.route('/devices/<string:device_uuid>/readings/quartiles/', methods = ['GET'])
@app.route('/devices/<string:device_uuid>/<string:device_type>/<string:start>/<string:end>/readings/quartiles/', methods = ['GET'])
def request_device_readings_quartiles(device_uuid, device_type, start, end):
    """
    This endpoint allows clients to GET the 1st and 3rd quartile
    sensor reading value for a device.

    Mandatory Query Parameters:
    * type -> The type of sensor value a client is looking for
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

        #Calculate the mean
        dataFrame = DataFrame(values)
        quantile_series = dataFrame.quantile([0.25, 0.75])
        response = {'quartile_1': quantile_series.values[0][0], 'quartile_3': quantile_series.values[1][0]}
        
        # Return the JSON
        return jsonify(response), 200

    except:
        print(traceback.format_exc())
        return 'An unexpected error happened', 500

    return 'Endpoint is not implemented', 501

@app.route('/devices/readings/summary/', methods = ['GET'], defaults={'device_type':None, 'start':None, 'end':None})
@app.route('/devices/<string:device_type>/readings/summary/', methods = ['GET'], defaults={'start':None, 'end':None})
@app.route('/devices/<string:device_type>/<string:start>/readings/summary/', methods = ['GET'], defaults={'end':None})
@app.route('/devices/<string:device_type>/<string:start>/<string:end>/readings/summary/', methods = ['GET'])
def request_readings_summary(device_type, start, end):
    """
    This endpoint allows clients to GET a full summary
    of all sensor data in the database per device.

    Optional Query Parameters
    * type -> The type of sensor value a client is looking for
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
        selectQuery = 'select device_uuid, value from readings where (?1 IS NULL OR type=?1) AND date_created BETWEEN ?2 AND ?3'
        # Execute the query
        cur.execute(selectQuery, [device_type, start_date, end_date])        
        values = cur.fetchall()

        # Add columns so we can compute for every single device
        data_frame = DataFrame(values, columns=['device_uuid', 'value'])
        data_grouped = data_frame.groupby('device_uuid')        
                
        summary = []
        for group in data_grouped:
            device_uuid = group[0]
            device_data_frame = data_frame.loc[data_frame['device_uuid'] == device_uuid]
            device_data = device_data_frame.describe()
            summary.append({
                'device_uuid':device_uuid,
                'number_of_readings': device_data.loc['count'].value,
                'max_reading_value': device_data.loc['max'].value,
                'median_reading_value': device_data_frame.median()[0],
                'mean_reading_value': device_data.loc['mean'].value,
                'quartile_1_value': device_data.loc['25%'].value,
                'quartile_3_value': device_data.loc['75%'].value
            })

        sorted_summary = sort_summary_by_key(summary, 'number_of_readings', True)
         
        return jsonify(sorted_summary), 200

    except:
        print(traceback.format_exc())
        return 'An unexpected error happened', 500
    

if __name__ == '__main__':
    app.run()

import json
import pytest
import sqlite3
import time
import unittest

from app import app

class SensorRoutesTestCases(unittest.TestCase):

    def setUp(self):
        # Setup the SQLite DB
        conn = sqlite3.connect('test_database.db')
        conn.execute('DROP TABLE IF EXISTS readings')
        conn.execute('CREATE TABLE IF NOT EXISTS readings (device_uuid TEXT, type TEXT, value INTEGER, date_created INTEGER)')
        
        self.device_uuid = 'test_device'
        self.current_time = int(time.time())

        # Setup some sensor data
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 22, self.current_time - 100))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 50, self.current_time - 50))
        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    (self.device_uuid, 'temperature', 100, self.current_time))

        cur.execute('insert into readings (device_uuid,type,value,date_created) VALUES (?,?,?,?)',
                    ('other_uuid', 'temperature', 22, self.current_time))
        conn.commit()

        app.config['TESTING'] = True

        self.client = app.test_client

    def test_device_readings_get(self):
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/readings/'.format(self.device_uuid))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response data should have three sensor readings
        self.assertTrue(len(json.loads(request.data)) == 3)

    def test_device_readings_post(self):
        # Given a device UUID
        # When we make a request with the given UUID to create a reading
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'temperature',
                'value': 100 
            }))

        # Then we should receive a 201
        self.assertEqual(request.status_code, 201)

        # And when we check for readings in the db
        conn = sqlite3.connect('test_database.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('select * from readings where device_uuid="{}"'.format(self.device_uuid))
        rows = cur.fetchall()

        # We should have three
        self.assertTrue(len(rows) == 4)

    def test_device_readings_get_temperature(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's temperature data only.
        """
        # Given a device UUID and a device type
        # When we make a request with the given UUID and Device Type this time temperature
        request = self.client().get('/devices/{}/{}/readings/'.format(self.device_uuid, 'temperature'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response temperature data should have three sensor readings
        self.assertTrue(len(json.loads(request.data)) == 3)

    def test_device_readings_get_humidity(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's humidity data only.
        """
        # Given a device UUID and a device type
        # When we make a request with the given UUID and Device Type this time humidity
        request = self.client().get('/devices/{}/{}/readings/'.format(self.device_uuid, 'humidity'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        # And the response temperature data shouldn't have any sensor readings
        self.assertTrue(len(json.loads(request.data)) == 0)        

    def test_device_readings_get_past_dates(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's sensor data over
        a specific date range. We should only get the readings
        that were created in this time range.
        """
        # Given a device UUID and a device type
        # When we make a request with the given UUID and Device Type this time temperature and current test time

        # Test for the current test datetime to any point in the future
        request = self.client().get('/devices/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 1 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 1)

        # Test for a past date to any point in the future
        request = self.client().get('/devices/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time - 50))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 2 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 2)

        # Test for a past date to any point in the future
        request = self.client().get('/devices/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time - 100))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 3 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 3)     

        # Test for a past date to a certain point int the future -- a dates range
        request = self.client().get('/devices/{}/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time - 100, self.current_time-1))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 2 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 2)    

        # Test for a past date to a certain point int the future -- a dates range
        request = self.client().get('/devices/{}/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time - 50, self.current_time-1))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 1 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 1)

    # The min, is not in the requirements for now. But it may be in the future, so let's keep this endpoint
    # commented and if we need it we can implement it then, but I prefer to leave a draft so we can see the requirement clearer
    # def test_device_readings_min(self):
    #     """
    #     This test should be implemented. The goal is to test that
    #     we are able to query for a device's min sensor reading.
    #     """ 
    #     # Given a device UUID
    #     # When we make a request with the given UUID
    #     request = self.client().get('/devices/{}/readings/min/'.format(self.device_uuid))

    #     # Then we should receive a 200
    #     self.assertEqual(request.status_code, 200)

    #     result = json.loads(request.data)

    #     # The min value of the test data is 22
    #     self.assertTrue(result['value'] == 22)
        
    def test_device_readings_max(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's max sensor reading.
        """
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/{}/readings/max/'.format(self.device_uuid, 'temperature'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        result = json.loads(request.data)

        # The max value of the test data is 100
        self.assertTrue(result['value'] == 100)

    def test_device_readings_median(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's median sensor reading.
        """
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/{}/readings/median/'.format(self.device_uuid, 'temperature'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        result = json.loads(request.data)

        # The midian value of the test data is 50
        self.assertTrue(result['value'] == 50)
        
    def test_device_readings_mean(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's mean sensor reading value.
        """
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/{}/readings/mean/'.format(self.device_uuid, 'temperature'))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        result = json.loads(request.data)

        expected_result = (22 + 50 + 100) / 3
        expected = float("{:.2f}".format(expected_result))

        actual = float("{:.2f}".format(result['value']))

        # Check if the expected is the same as the actual value
        self.assertTrue(actual == expected)        

    # Mode wasn't implemented, let's comment it and once is implemented we can return and finish this test
    # def test_device_readings_mode(self):
    #     """
    #     This test should be implemented. The goal is to test that
    #     we are able to query for a device's mode sensor reading value.
    #     """
    #     # Given a device UUID
    #     # When we make a request with the given UUID
    #     request = self.client().get('/devices/{}/{}/readings/mode/'.format(self.device_uuid, 'temperature'))

    #     # Then we should receive a 200
    #     self.assertEqual(request.status_code, 200)

    #     result = json.loads(request.data)
             
    #     self.assertTrue(False)

    def test_device_readings_quartiles(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for a device's 1st and 3rd quartile
        sensor reading value.
        """
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/{}/{}/{}/{}/readings/quartiles/'.format(self.device_uuid, 'temperature', self.current_time, self.current_time + 100))

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        result = json.loads(request.data)

        print(result)

        # For the current data, is possible the quartiles doesn't apply
        expected_q1 = 100.0
        expected_q3 = 100.0

        self.assertTrue(result['quartile_1'] == expected_q1)
        self.assertTrue(result['quartile_3'] == expected_q3)

    def test_device_readings_summary(self):
        """
        This test should be implemented. The goal is to test that
        we are able to query for devices summary information
        """
        # Given a device UUID
        # When we make a request with the given UUID
        request = self.client().get('/devices/readings/summary/')

        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)

        result = json.loads(request.data)

        # Check the lenght, should be 2 because we have two different devices
        self.assertTrue(len(result) == 2)

        # Expected summary data
        min_value_1 = 22.0
        median_value_1 = 50.0
        max_value_1 = 100.0
        device_num_1 = 3.0
        expected_mean_result_1 = (min_value_1 + median_value_1 + max_value_1) / device_num_1        
        expected_test_device = {
            "device_uuid": self.device_uuid,
            "max_reading_value": max_value_1,
            "mean_reading_value": expected_mean_result_1,
            "median_reading_value": median_value_1,
            "number_of_readings": device_num_1,
            "quartile_1_value": 36.0, # not enough data
            "quartile_3_value": 75.0, # not enought data
        }

        min_value_2 = 22.0
        median_value_2 = 22.0
        max_value_2 = 22.0
        device_num_2 = 1.0
        expected_mean_result_2 = (min_value_2) / device_num_2
        expected_mean_2 = float("{:.2f}".format(expected_mean_result_2))
        expected_other_device = {
            "device_uuid": 'other_uuid',
            "max_reading_value": max_value_2,
            "mean_reading_value": expected_mean_2,
            "median_reading_value": median_value_2,
            "number_of_readings": device_num_2,
            "quartile_1_value": max_value_2, # not enough data
            "quartile_3_value": max_value_2, # not enought data
        }

        # Test the sort order of number of readings, the greater would be the test device number of readings
        # so the first item is the information of test device
        self.assertDictEqual(result[0], expected_test_device)

        # then we check other device
        self.assertDictEqual(result[1], expected_other_device)

    def test_device_readings_outside_dates_range(self):
        """
        This test should be implemented. The goal is to test empty list
        because is outside the dates range
        """
        # Test for a past date to a certain point int the future -- a dates range
        request = self.client().get('/devices/{}/{}/{}/{}/readings/'.format(self.device_uuid, 'temperature', self.current_time + 100, self.current_time + 200))
        # Then we should receive a 200
        self.assertEqual(request.status_code, 200)
        # And the response temperature data should have 0 sensor readings for the given timestamp
        self.assertTrue(len(json.loads(request.data)) == 0)    

    def test_device_readings_post_invalid_type(self):
        """
        This test should be implemented. The goal is to test empty list
        because is outside the dates range
        """
        # Given a device UUID
        # When we make a request with the given UUID to create a reading
        request = self.client().post('/devices/{}/readings/'.format(self.device_uuid), data=
            json.dumps({
                'type': 'invalid_type',
                'value': 100 
            }))

        # Then we should receive a 400 bad request
        self.assertEqual(request.status_code, 400)

        # Then let's check for the validation error
        result = json.loads(request.data)

        expected_response = {
            "type": [
                "Must be one of: temperature, humidity."
            ]
        }

        self.assertDictEqual(expected_response, result)



        
        
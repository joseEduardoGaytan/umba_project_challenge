import datetime
import time

def getDefaultDatesParams(start, end):    
    if start is None:
        start_date = 21600 # From the begining of the times
    else:
        d = datetime.datetime.strptime(start, '%Y-%m-%d')
        start_date = time.mktime(d.timetuple())
    if end is None:
        end_date = int(time.time()) # now
    else:
        d = datetime.datetime.strptime(end, '%Y-%m-%d')
        end_date = time.mktime(d.timetuple())

    return start_date, end_date
import datetime
import time

def getDefaultDatesParams(start, end):
    start_date = 21600 if start is None else start 
    end_date = int(time.time()) if end is None else end   
      
    return start_date, end_date
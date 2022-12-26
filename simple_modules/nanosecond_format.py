import datetime
import time 

def format_my_nanos(nanos):
    dt = datetime.datetime.fromtimestamp(nanos / 1e9)
    # return '{}{:03.0f}'.format(dt.strftime('%Y-%m-%dT%H:%M:%S.%f'), nanos % 1e3)
    return dt.strftime('%Y-%m-%dT%H:%M:%S')



import json

import time

import datetime


def log(*args, **kwargs):
    time_format = '%H:%M:%S'
    now = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, now)
    print(formatted, *args, **kwargs)


def log_error(*args, **kwargs):
    log('Error', *args, **kwargs)


def log_dict(data):
    print(json.dumps(data, indent=4))


def unixtime_from_api_v4(utc_string):
    v4_time_format = '%Y-%m-%dT%H:%M:%SZ'
    dt = datetime.datetime.strptime(utc_string, v4_time_format)
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    unix_time = int(dt.timestamp())
    return unix_time

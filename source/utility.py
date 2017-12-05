import json

import time


def log(*args, **kwargs):
    time_format = '%H:%M:%S'
    now = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, now)
    print(formatted, *args, **kwargs)


def log_dict(data):
    print(json.dumps(data, indent=4))

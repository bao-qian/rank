import json

import time


def log(*args, **kwargs):
    time_format = '%H:%M:%S'
    now = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, now)
    print(formatted, *args, **kwargs)
    filename = 'rank.log'.format(__file__)
    with open(filename, 'a', encoding='utf-8') as f:
        print(formatted, *args, file=f, **kwargs)


def log_dict(data):
    print(json.dumps(data, indent=4))

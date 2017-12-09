import json

import time

from source.exception import NoneError


def log(*args, **kwargs):
    time_format = '%H:%M:%S'
    now = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, now)
    print(formatted, *args, **kwargs)


def log_error(*args, **kwargs):
    log('Error', *args, **kwargs)


def log_dict(data):
    print(json.dumps(data, indent=4))


def ensure_not_none(data, message):
    valid = data is not None
    valid = valid and data is not [None]
    valid = valid and data is not {None}
    valid = valid and data is not {None: None}
    if not valid:
        raise NoneError(message)

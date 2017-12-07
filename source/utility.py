import json

import time
from queue import Queue
from threading import Thread


def log(*args, **kwargs):
    time_format = '%H:%M:%S'
    now = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, now)
    print(formatted, *args, **kwargs)


def log_error(*args, **kwargs):
    log('Error', *args, **kwargs)


def log_dict(data):
    print(json.dumps(data, indent=4))


class ThreadWorker(Thread):
    def __init__(self, queue, output, work):
        Thread.__init__(self)
        self.queue = queue
        self.work = work
        self.output = output

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            args = self.queue.get()
            # print('thread worker run', args)
            r = self.work(*args)
            if r is not None:
                self.output.append(r)
            self.queue.task_done()

import os
import sys
import time

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


def ftimeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    """http://stackoverflow.com/a/13821695"""
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
        to = False
    except TimeoutError as exc:
        to = True
        result = default
    finally:
        signal.alarm(0)

    return result, to

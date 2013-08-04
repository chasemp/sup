#!/usr/bin/env python
import argparse
import sys
import httplib
import datetime
import subprocess
import time
import socket
import json
import inspect
#from ping import Ping
import thread
import os
from addr import is_local
from monitor import *

try:
    import Tkinter, tkMessageBox
    gui = True
except ImportError:
    gui = False
    pass

def popup(msg):
    root = Tkinter.Tk()
    root.withdraw()
    tkMessageBox.showinfo(sys.argv[0], str(msg))


def runBash(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out

def broadcast_msg(msg):
    runBash('echo "%s" | wall' % str(msg))


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


def find_monitors(module):
    import sys
    sup_functions = {}
    classes = inspect.getmembers(module, inspect.isclass)
    for name, obj in classes:
        sup_functions[name] = obj
    return sup_functions

def main():

    sup_dict = find_monitors(sys.modules[__name__])
    parser = argparse.ArgumentParser(description='like ping but for protocols')
    parser.add_argument("site",nargs=1, help='url or ip of site to manage')
    parser.add_argument("-p", help="show popups",  action="store_true")
    parser.add_argument("-b", help="broadcast messages",  action="store_true")
    parser.add_argument("-v", help="verbose",  action="store_true")
    parser.add_argument("-vv", help="very verbose",  action="store_true")
    parser.add_argument("-t", action='store', dest='timeout', default=1, help='main timeout')
    parser.add_argument('-i', action='store', dest='interval',
                    default=2,
                    help='interval between polls',
                    )

    parser.add_argument('-m', action='store', dest='mode',
                    default='tcping',
                    help='Check type to use.  \nAvailable: %s\n' %
                    '\r\n'.join([m.split('_')[1] for m in sup_dict.keys() if m.startswith('sup_')]))

    def helpdie(msg=None):
        if msg:
            print '\n\nFailed: %s\n' % msg
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    site = args.site[0]

    if ':' in site:
        site, port = site.split(':')
        try:
            port = int(port)
        except ValueError, e:
            helpdie(str(e))
    else:
        port = 0

    if args.interval:
        try:
            interval = int(args.interval)
        except Exception, e:
            helpdie(str(e))

    try:
        ip = socket.gethostbyname(site)
    except:
        helpdie('could not translate hostname')


    print is_local(ip, args.mode)

    if gui == False and args.p:
        print 'popups enabled but no GUI -- disabling'
        args.p = False

    if args.vv:
        print args

    attempt = 0
    state = ''
    mode = "sup_%s" % args.mode
    if mode in sup_dict:
        suping = sup_dict[mode]
        s = suping(site, port, int(args.timeout))
        s.name = mode
        s.v = args.v
        s.vv = args.vv
    else:
        helpdie()

    #Listen for user signals while 
    #polling
    def input_thread(L):
        raw_input()
        L.append(None)
    L = []
    thread.start_new_thread(input_thread, (L,))

    begin = time.time()
    poll_durations = []

    while 1:
        if L:
            print 'avg: %s Max: %s Min: %s' % (sum(poll_durations)/len(poll_durations),
                                               max(poll_durations),
                                               min(poll_durations))
            print '%s polled %s times in %s seconds' % (args.mode, attempt, round(time.time() - begin))
            break

        attempt += 1
        localtime   = time.localtime()
        now  = time.strftime("%I.%M.%S", localtime)
        lstate = state or ''
        state, howlong = s.run()
        poll_durations.append(howlong)
        if args.vv and s.vv_out is not None:
            print s.vv_out
            sys.stdout.write('>>> ')
        host = s.ip
        if s.port:
            host += ':%s' % s.port
        msg = '%s %s %s %s ms' %  (now, host, state, howlong)
        if s.v or s.vv:
            msg += ' %s' % attempt
        if state and lstate and state != lstate:
            if args.b:
                broadcast_msg(msg)
            if args.p:
                popup(msg)
        elif state and not lstate:
            if args.v:
                print 'unknown last state'
        print msg
        if args.v or args.vv:
            print '---------------------------------------------------'
        time.sleep(interval)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\n'
        sys.exit(0)

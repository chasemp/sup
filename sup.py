#!/usr/bin/env python
import argparse
import sys
import time
import socket
import thread
from suplib import is_local
from suplib import get_config_key
from suplib import find_monitors
from suplib import gui
from suplib import popup
from suplib import broadcast_msg

#try:
#    import Tkinter, tkMessageBox
#    gui = True
#except ImportError:
#    gui = False
#    pass


def main():

    def verify_int(number):
        try:
            return int(number)
        except ValueError, e:
            helpdie(str(e))

    poller = None
    sup_dict = find_monitors()
    parser = argparse.ArgumentParser(description='like ping but for higher up the stack')
    parser.add_argument("site",nargs=1, help='url or ip of site to manage')
    parser.add_argument("-p", help="show popups",  action="store_true")
    parser.add_argument("-b", help="broadcast messages",  action="store_true")
    parser.add_argument("-v", help="verbose",  action="store_true")
    parser.add_argument("-f", help="flood as many requests as possible",  action="store_true")
    parser.add_argument("-vv", help="very verbose",  action="store_true")
    parser.add_argument("-c", action='store', dest='count', default=0, help='set count')
    parser.add_argument("-t", action='store', dest='timeout', default=1, help='main timeout')
    parser.add_argument('-i', action='store', dest='interval',
                    default=1,
                    help='interval between polls',
                    )

    parser.add_argument('-m', action='store', dest='mode',
                    default=poller,
                    help='Check type to use.  \nAvailable: %s\n' %
                    '\r\n'.join([m.split('_')[1] for m in sup_dict.keys() if m.startswith('sup_')]))

    def helpdie(msg=None):
        if msg:
            print '\n\nFailed: %s\n' % msg
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    site = args.site[0]

    if args.vv:
        args.v = True

    explicitport = False
    if ':' in site:
        site, port = site.split(':')
        explicitport = True
    else:
        port = 0

    if args.interval:
        interval = verify_int(args.interval)

    sub = get_config_key('subs', site)
    if sub:
        if args.v:
            print 'translating %s => %s' % (site, sub)
        site = sub

    try:
        ip = socket.gethostbyname(site)
    except:
        helpdie('could not translate hostname')

    #check for user polling preferrences for local and remote hosts
    if is_local(ip, args.mode) and args.mode == poller:
        if args.vv:
          print 'local host found'
        lpreferred = get_config_key(args.mode, 'localmon')
        if lpreferred:
            args.mode = lpreferred
            if args.vv:
                print 'mode changed to %s' % (args.mode)
    else:
        if args.vv:
            print 'remote host found'
        rpreferred = get_config_key(args.mode, 'remotemon')
        if rpreferred and args.mode == poller:
            args.mode = rpreferred
            if args.vv:
                print 'mode changed to %s' % (args.mode)

    if not explicitport:
        port = get_config_key(args.mode, 'port') or port
    port = verify_int(port)

    if gui == False and args.p:
        print 'popups enabled but no GUI -- disabling'
        args.p = False

    final_poller = args.mode or 'tcp'
    mode = "sup_%s" % final_poller
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
    attempt = 0
    state = ''
    count = verify_int(args.count)

    while 1:
        if L or attempt == count and count != 0:
            break

        attempt += 1
        localtime = time.localtime()
        now = time.strftime("%I.%M.%S", localtime)
        lstate = state or ''
        state, howlong = s.run()
        poll_durations.append(howlong)
        if args.vv and s.vv_out is not None:
            print s.vv_out
            sys.stdout.write('>>> ')
        if args.v and s.v_out is not None:
            print s.v_out
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
        if not args.f:
            try:
                time.sleep(interval)
            #prevents some edgecase exceptions being raised
            #for cntrl+c in sleep cycle.
            except:
                return

    print 'avg: %s Max: %s Min: %s' % (sum(poll_durations)/len(poll_durations),
                                               max(poll_durations),
                                               min(poll_durations))
    print '%s polled %s times in %s seconds' % (args.mode, attempt, round(time.time() - begin, 4))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\n'
        sys.exit(0)

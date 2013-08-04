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
from ping import Ping
import thread
import os
from addr import is_local


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


class supped(object):

    def __init__(self, ip, port, timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.v = False
        self.vv = False
        self.v_out = None
        self.vv_out = None

    def run(self):

        if self.v or self.vv:
            verbose_intro = "Polling %s on port %s with timeout %s\n"
            print verbose_intro % (self.__class__.__name__.split('_')[1],
                                                                self.port, self.timeout)
        with Timer() as t:
            result, to = ftimeout(self.poll, timeout_duration=self.timeout)
        if to:
            result = 'timeout'
        ms = t.interval * 1000
        return result,  ms

    def poll(self):
        raise NotImplementedError("Subclasses should implement this!")


class sup_ntp(supped):

    def poll(self):
        self.port = self.port if self.port else 123
        # File: Ntpclient.py
        #http://stackoverflow.com/questions/12664295/ntp-client-in-python
        from socket import AF_INET, SOCK_DGRAM
        import sys
        import socket
        import struct, time
        from time import ctime
        buf = 1024
        address = (self.ip, self.port)
        msg = '\x1b' + 47 * '\0'
        TIME1970 = 2208988800L # 1970-01-01 00:00:00
        client = socket.socket( AF_INET, SOCK_DGRAM)
        client.sendto(msg, address)
        msg, address = client.recvfrom( buf )
        t = struct.unpack( "!12I", msg)[10]
        t -= TIME1970
        return t


class sup_http(supped):

    def poll(self):
        self.port = self.port if self.port else 80
        try:
            conn = httplib.HTTPConnection(self.ip, self.port)
            conn.request("HEAD", "/")
            request_result = conn.getresponse()
            if request_result:
                status = '%s %s' % (request_result.status, request_result.reason)
            else:
                status = 'unavailable'
            if self.vv:
                self.vv_out = ''
                self.vv_out += 'Connection details:'
                for k, v in vars(request_result).iteritems():
                    if k != 'msg':
                        self.vv_out += '         %s %s\n' % (k, v)
                    else:
                        self.vv_out += 'Message details:\n'
                        for output in str(v).splitlines():
                            self.vv_out += '        %s\n' % output
            return status
        except socket.error, e:
            if self.v or self.vv:
                print 'socket error', e
            return None

class sup_smtp(supped):

    def poll(self):
        self.port = self.port if self.port else 25
        import socket
        try:
            mark = 'ESMTP'
            sock = socket.socket()
            sock.connect((self.ip, self.port))
            data = sock.recv(2048)
            if mark in data:
                status = 'ok'
            else:
                status = 'failed'
            return status
        except socket.error:
            return None
        finally:
            sock.close()

class sup_redis(supped):

    def poll(self):
        import telnetlib
        self.port = self.port if self.port else 6379
        mark = 'PONG'
        try:
            tn = telnetlib.Telnet(self.ip, self.port)
            tn.read_very_eager()
            tn.write("PING\r\n")
            tn.write("info\r\n")
            tn.write("QUIT\r\n")  # this is where i enter my username
            data = tn.read_all()
            if mark in data:
                status = mark
            else:
                status = 'failed'
            return status
        except socket.error:
            return None

class sup_memcached(supped):

    def poll(self):
        import telnetlib
        self.port = self.port if self.port else 11211
        mark = 'accepting_conns 1'
        try:
            tn = telnetlib.Telnet(self.ip, self.port)
            tn.read_very_eager()
            tn.write("stats\r\n")
            tn.write("quit\r\n")
            data =  tn.read_all()
            if mark in data:
                status = 'ok'
            else:
                status = 'failed'
            return status
        except socket.error:
            return None

class sup_tcping(supped):

    def poll(self):
        self.port = self.port if self.port else 22
        import socket
        try:
            sock = socket.socket()
            sock.connect((self.ip, self.port))
            if isinstance(sock, socket._socketobject):
                status = 'ok'
            else:
                status = 'failed'
            return status
        except socket.error:
            return None
        finally:
            sock.close()



class sup_icmp(supped):

    def poll(self):
        import socket
        try:
            p = Ping(self.ip, 1, 55)
            return p.do()
        except socket.error:
            print 'need superuser priviledges'


class sup_tcp(supped):

    def poll(self):
        self.port = self.port if self.port else 22
        import socket
        try:
            sock = socket.socket()
            sock.connect((self.ip, self.port))
            if isinstance(sock, socket._socketobject):
                status = 'ok'
            else:
                status = 'failed'
            return status
        except socket.error:
            return None
        finally:
            sock.close()

def find_monitors(module):
    import sys
    sup_functions = {}
    classes = inspect.getmembers(module, inspect.isclass)
    for name, obj in classes:
        sup_functions[name] = obj
    return sup_functions

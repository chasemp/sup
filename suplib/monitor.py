import ports
import time
import sys
import socket
from . import sysexits

def find_monitors(module=sys.modules[__name__]):
    import inspect
    sup_functions = {}
    classes = inspect.getmembers(module, inspect.isclass)
    for name, obj in classes:
        sup_functions[name] = obj
    return sup_functions

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

    def __init__(self, site, port, timeout):
        self.site = site
        self.port = port
        self.timeout = timeout
        self.v = False
        self.vv = False

    def resolve(self, site):
        try:
            return socket.gethostbyname(site)
        except:
            sys.stderr.write('could not translate hostname\n')
            sys.exit(1)

    def run(self):
        self.v_out = ''
        self.vv_out = ''
        with Timer() as t:
            result, to = ftimeout(self.poll, timeout_duration=self.timeout)
        if to:
            result = 'timeout'
        ms = t.interval * 1000
        return result,  ms

    def poll(self):
        raise NotImplementedError("Subclasses should implement this!")


class sup_ssh(supped):

    def poll(self):
        import subprocess as sp
        from sysexits import codes
        self.timeout = 5
        self.port = self.port or ports.ssh

        cmd = "/usr/bin/ssh -p %s -F ~/.ssh/config -q %s exit" % (self.port, self.site,)
        self.vv_out += cmd
        retcode = sp.call(cmd, shell=True)
        if retcode == 0:
            return 'OK'
        else:
            return codes[retcode]

class sup_ntp(supped):

    def poll(self):
        self.port = self.port or ports.ntp
        # File: Ntpclient.py
        #http://stackoverflow.com/questions/12664295/ntp-client-in-python
        from socket import AF_INET, SOCK_DGRAM
        import sys
        import socket
        import struct, time
        from time import ctime
        buf = 1024
        address = (self.resolve(self.site), self.port)
        msg = '\x1b' + 47 * '\0'
        TIME1970 = 2208988800L # 1970-01-01 00:00:00
        client = socket.socket( AF_INET, SOCK_DGRAM)
        client.sendto(msg, address)
        msg, address = client.recvfrom( buf )
        t = struct.unpack( "!12I", msg)[10]
        t -= TIME1970
        return t

class sup_https(supped):

    #notes: http://stackoverflow.com/questions/1087227/validate-ssl-certificates-with-python
    def poll(self):
        import socket, ssl
        self.port = self.port or ports.ssl
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.resolve(self.site), self.port))
            sslSocket = socket.ssl(s)
            if self.v:
                issuer_details = sslSocket.issuer().replace('/', '\n')
                server_details = sslSocket.server().replace('/', '\n')

                self.v_out += issuer_details
                self.v_out += server_details
            if sslSocket.cipher():
                status = "%s-%s-%s" % (sslSocket.cipher()[0], sslSocket.cipher()[1], sslSocket.cipher()[2])
            else:
                status = 'unavailable'
            if self.vv:
                self.vv_out += 'remote pem certificate\n'
                self.vv_out += ssl.get_server_certificate(('74.125.225.85', 443))
            return status

        except socket.error, e:
            if self.v or self.vv:
                print 'socket error', e
            return None
        finally:
            try:
                s.close()
            except:
                pass


class sup_http(supped):

    def poll(self):
        import httplib
        self.port = self.port or ports.http
        try:
            conn = httplib.HTTPConnection(self.resolve(self.site), self.port)
            conn.request("HEAD", "/")
            request_result = conn.getresponse()
            if request_result:
                status = '%s %s' % (request_result.status, request_result.reason)
            else:
                status = 'unavailable'
            if self.vv:
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
        self.port = self.port or ports.smtp
        import socket
        try:
            mark = 'ESMTP'
            sock = socket.socket()
            sock.connect((self.resolve(self.site), self.port))
            data = sock.recv(2048)
            if mark in data:
                status = 'OK'
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
        self.port = self.port or ports.redis
        mark = 'PONG'
        try:
            tn = telnetlib.Telnet(self.resolve(self.site), self.port)
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
        self.port = self.port or ports.memcached
        mark = 'accepting_conns 1'
        try:
            tn = telnetlib.Telnet(self.resolve(self.site), self.port)
            tn.read_very_eager()
            tn.write("stats\r\n")
            tn.write("quit\r\n")
            data =  tn.read_all()
            if mark in data:
                status = 'OK'
            else:
                status = 'failed'
            return status
        except socket.error:
            return None


class sup_icmp(supped):

    def poll(self):
        from ping import Ping
        import socket
        try:
            p = Ping(self.resolve(self.site), 1, 55)
            return p.do()
        except socket.error:
            print 'need superuser priviledges'


class sup_tcp(supped):

    def poll(self):
        self.port = self.port or ports.ssh
        import socket
        try:
            sock = socket.socket()
            sock.connect((self.resolve(self.site), self.port))
            if isinstance(sock, socket._socketobject):
                status = 'OK'
            else:
                status = 'failed'
            return status
        except socket.error:
            return 'failed'
        finally:
            sock.close()

if __name__ == '__main__':
    print find_monitors()

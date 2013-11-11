#!/usr/bin/env python
#coding=utf8
#
# A python implementation of send_arp.c.
#
# ARP code and license inspired by arprequest by Antoine Millet
# See http://pypi.python.org/pypi/arprequest
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
# Version 2, December 2004
#
# Copyright (C) 2011 Kristoffer Gronlund
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
#

from optparse import OptionParser
import time, socket
from struct import pack, unpack
import signal

def commandline():
    parser = OptionParser(usage="%prog [OPTIONS] device src_ip_addr src_hw_addr broadcast_ip_addr netmask")
    parser.add_option("-i", "--interval", dest="interval", default="1000",
                      help="Repeat interval in ms", metavar="INTERVAL")
    parser.add_option("-r", "--repeat", dest="repeat", default="1",
                      help="Repeat count", metavar="REPEAT")
    parser.add_option("-p", "--pidfile", dest="pidfile",
                      default="/tmp/arp.pid",
                      help="PID file", metavar="PID")

    (options, args) = parser.parse_args()

    if len(args) != 5:
        parser.error("Expects: [-i repeatinterval-ms] [-r repeatcount] [-p pidfile] \\\n"+
                     "        device src_ip_addr src_hw_addr broadcast_ip_addr netmask")

    class Args: pass
    ret = Args()
    ret.interval = int(options.interval)
    ret.repeat = int(options.repeat)
    ret.pidfile = options.pidfile
    ret.device = args[0]
    ret.src_ip_addr = args[1]
    ret.src_hw_addr = args[2]
    ret.broadcast_ip_addr = args[3]
    ret.netmask = args[4]
    return ret

def mssleep(ms):
    time.sleep(ms/1000.0)

def send_arp(ip, device, sender_mac, broadcast, netmask, arptype):
    #if_ipaddr = socket.gethostbyname(socket.gethostname())
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
    sock.bind((device, socket.SOCK_RAW))

    bcast_mac = pack('!6B', *(0xFF,)*6)
    zero_mac = pack('!6B', *(0x00,)*6)


    socket_mac = sock.getsockname()[4]
    if sender_mac == 'auto':
        sender_mac = socket_mac
    else:
        raise Exception("Can't ARP this: " + sender_mac)

    ARPOP_REQUEST = pack('!H', 0x0001)
    ARPOP_REPLY = pack('!H', 0x0002)
    arpop = None
    target_mac = None
    if arptype == 'REQUEST':
        target_mac = zero_mac
        arpop = ARPOP_REQUEST
    else:
        target_mac = sender_mac
        arpop = ARPOP_REPLY

    sender_ip = pack('!4B', *[int(x) for x in ip.split('.')])
    target_ip = pack('!4B', *[int(x) for x in ip.split('.')])


    arpframe = [
        ### ETHERNET
        # destination MAC addr
        bcast_mac,
        # source MAC addr
        socket_mac,
        # protocol type (=ARP)
        pack('!H', 0x0806),

        ### ARP
        # logical protocol type (Ethernet/IP)
        pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
        # operation type
        arpop,
        # sender MAC addr
        sender_mac,
        # sender IP addr
        sender_ip,
        # target hardware addr
        target_mac,
        # target IP addr
        target_ip
        ]

    # send the ARP
    sock.send(''.join(arpframe))

    return True

def main():
    args = commandline()

    for j in range(args.repeat):
        if not send_arp(args.src_ip_addr, args.device,
                        args.src_hw_addr,
                        args.broadcast_ip_addr,
                        args.netmask, 'REQUEST'):
            break
        mssleep(args.interval / 2)

        if not send_arp(args.src_ip_addr, args.device,
                        args.src_hw_addr,
                        args.broadcast_ip_addr,
                        args.netmask, 'REPLY'):
            break

        if j != args.repeat-1:
            mssleep(args.interval / 2)

if __name__=="__main__":
    main()

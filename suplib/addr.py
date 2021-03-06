import os
import struct
import socket
from config import get_config_key

def num2ip(num):
    """
    >>> num2ip(16843009)
    '1.1.1.1'
    """
    return socket.inet_ntoa(struct.pack('>I', num))

def ip2num(ip):
    """

    >>> ip2num('1.1.1.1')
    16843009
    """
    return struct.unpack('>I', socket.inet_aton(ip))[0]

def parse_cidr(cidr):
    """
    given a network in the CIDR notation (network/maskbits), returns the
    network, netmask and broadcast in the dotted quad notation.

        >>> parse_cidr('10.0.0.0/24')
        ('10.0.0.0', '255.255.255.0', '10.0.0.255')

    """
    net, prefix = cidr.split('/')
    network_num = ip2num(net)
    mask_num = struct.unpack('<I', struct.pack('>I', ((1L << int(prefix)) - 1)))[0]
    invmask_num = ip2num('255.255.255.255') ^ mask_num
    return tuple(map(num2ip, [network_num, mask_num, network_num | invmask_num]))

def is_ip_included(cidr, ip):
    """
    given a subnet and ip it will return a bool
    >>> is_ip_included('1.0.0.0/8', '1.1.1.1')
    True
    """
    network, _, broadcast = map(ip2num, parse_cidr(cidr))
    ipnum = ip2num(ip)
    return ipnum > network and ipnum < broadcast

def is_local(ip, mode=None):
    if ip.startswith('127'):
        return True

    local_nets = get_config_key(mode, 'localnet')
    if not local_nets:
        return False
    elif ',' not in local_nets and ip.startswith(local_nets):
        return True
    elif any(map(lambda s: ip.startswith(s), local_nets.split(','))):
        return True
    else:
        return False

import os
import struct
import socket
import ConfigParser

home = os.path.expanduser('~')
#print os.path.join(home, '.sup.ini')
parser = ConfigParser.SafeConfigParser()
parser.read('/Users/rush/.sup.ini')

def get_config_key(mode, key, strict=False):
    if mode is None:
        if parser.has_section('default'):
            mode = 'default'
    elif not parser.has_section(mode):
        mode = 'default'

    try:
        cfgvalue = parser.get(mode, key)
    except ConfigParser.NoOptionError:
        if strict:
            raise
        cfgvalue = None
    return cfgvalue

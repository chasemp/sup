import os
import struct
import socket
from ConfigParser import SafeConfigParser
home = os.path.expanduser('~')
print os.path.join(home, '.sup.ini')

parser = SafeConfigParser()
parser.read('/Users/rush/.sup.ini')

def get_local(mode):
    if mode is None:
        if parser.has_section('DEFAULT'):
            mode = 'DEFAULT'
    elif not parser.has_section(mode):
        mode = 'DEFAULT'

    return parser.get(mode, 'local')

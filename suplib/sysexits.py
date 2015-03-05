# In theory we pattern after:
# /usr/include/sysexits.h
# In reality the world complicated.
codes = {1: 'General Error',
         2: 'Builtin Misuse',
         126: 'Command invoked cannot execute',
         128: 'Invalid argument to exit',
         255: 'Error'}

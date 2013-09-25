import sys
print "don't use this yet"
sys.exit(0)

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "sup",
    version = "1.0",
    author = "Chase Pettet",
    author_email = "chase@gmail.com",
    description = ("To be used for checking the state of services."),
    license = "MIT",
    keywords = "ping monitoring",
    url = "http://packages.python.org/sup",
    packages=['sup'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

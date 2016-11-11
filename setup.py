#!/usr/bin/env python

import sys
from setuptools import setup

if sys.version_info < (3, 3):
    sys.exit('Sorry, Python < 3.3 is not supported')

setup(name='ranalyze',
      version='0.1',
      install_requires=[
          "praw==3.5.0",
          "pylint==1.5.4",
          "lazy-object-proxy==1.2.1",
          "flask==0.11.1",
          "mysqlclient==1.3.9"
      ],
      packages=["ranalyze"]
      )


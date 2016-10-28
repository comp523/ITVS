#!/usr/bin/env python

import sys
from setuptools import setup

if sys.version_info < (3, 5, 2):
    sys.exit('Sorry, Python < 3.5.2 is not supported')

setup(name='ranalyze',
      version='0.1',
      install_requires=[
          "nose==1.3.7",
          "praw==3.5.0",
          "pylint==1.5.4",
          "pyyaml==3.12",
          "flask==0.11.1"
      ],
      packages=["ranalyze", "ranalyze.database"]
      )


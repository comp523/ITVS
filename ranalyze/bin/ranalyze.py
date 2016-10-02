from os import path
import runpy
import sys

dir_path = path.realpath(path.join(path.dirname(path.realpath(__file__)), ".."))
sys.path.insert(1, dir_path)

import pkg

runpy.run_module("pkg.ranalyze", run_name="__main__")
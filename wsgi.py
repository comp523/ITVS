#!/usr/bin/python
import os

virtenv = os.path.join(os.environ.get('OPENSHIFT_PYTHON_DIR','.'), 'virtenv')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    with open(virtualenv) as f:
      code = compile(f.read(), "somefile.py", 'exec')
      exec(code, dict(__file__=virtualenv))

except IOError:
    pass
#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#

import ranalyze.api
from ranalyze.api import app as application

#os.environ['OPENSHIFT_MYSQL_DB_HOST'] = '127.13.87.2'
#os.environ['OPENSHIFT_MYSQL_DB_PORT'] = '3306'
#os.environ['OPENSHIFT_MYSQL_DB_USERNAME'] = 'admintfMgVT9'
#os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'] = 'B4muI-pY5vEh'
#os.environ['OPENSHIFT_MYSQL_DB_URL'] = 'mysql://admintfMgVT9:B4muI-pY5vEh@127.13.87.2:3306/'

if 'OPENSHIFT_MYSQL_DB_HOST' in os.environ:
    ranalyze.api.mysql_init();

#
# Below for testing only
#
if __name__ == '__main__':
    
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.serve_forever()

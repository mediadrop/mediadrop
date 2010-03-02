#!/Users/anthony/python_environments/mediacore_env/bin/python

import sys, os
os.environ['PYTHON_EGG_CACHE'] = '/Users/anthony/Sites/mediacore/python-wsgi-egg-cache'

from paste.deploy import loadapp
app = loadapp('config:/Users/anthony/Sites/mediacore/deployment.ini')

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(app).run()

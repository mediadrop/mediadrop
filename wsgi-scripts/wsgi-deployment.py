import os, sys, site

os.environ['PYTHON_EGG_CACHE'] = '/home/simple/library/python-wsgi-egg-cache'
site.addsitedir('/home/simple/library/python-mediaplex/lib/python2.4/site-packages')

sys.path = list(set(sys.path))
sys.path.insert(0, '/home/mediaple/mediaplex')
sys.path.insert(1, '/home/simple/library/python-mediaplex/lib/python2.4')

from mediaplex import debug
from paste.deploy import loadapp

application = loadapp('config:/home/mediaple/mediaplex/mediaplex/config/deployment.ini')


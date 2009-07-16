import os, sys, site

os.environ['PYTHON_EGG_CACHE'] = '/Users/anthony/Sites/mediaplex/python-wsgi-egg-cache'
sd = "/Users/anthony/Sites/mediaplex/TEMP/a/lib/python2.5/site-packages/"
site.addsitedir(sd)

from mediaplex import debug
from paste.deploy import loadapp

application = loadapp('config:/Users/anthony/Sites/mediaplex/deployment.ini')

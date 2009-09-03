import os, sys, site

os.environ['PYTHON_EGG_CACHE'] = '/Users/anthony/Sites/simpleplex/python-wsgi-egg-cache'
sd = "/Users/anthony/Sites/simpleplex/TEMP/a/lib/python2.5/site-packages/"
site.addsitedir(sd)

from simpleplex import debug
from paste.deploy import loadapp

application = loadapp('config:/Users/anthony/Sites/simpleplex/deployment.ini')

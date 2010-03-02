import os, sys, site

os.environ['PYTHON_EGG_CACHE'] = '/Users/anthony/Sites/mediacore/python-wsgi-egg-cache'
sd = "/Users/anthony/Sites/mediacore/TEMP/a/lib/python2.5/site-packages/"
site.addsitedir(sd)

from mediacore import debug
from paste.deploy import loadapp

application = loadapp('config:/Users/anthony/Sites/mediacore/deployment.ini')

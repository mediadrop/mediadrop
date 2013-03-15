deployment_config = '/path/to/deployment.ini'
temp_dir = '/path/to/data/tmp'

# NOTE: Before running MediaCore, you will need to update the two paths
#       above to point to the appropriate locations for your installation.

import os
os.environ['TMPDIR'] = temp_dir

# Set up logging under mod_wsgi
from paste.script.util.logging_config import fileConfig
fileConfig(deployment_config)
# Load the app!
from paste.deploy import loadapp
application = loadapp('config:'+deployment_config)

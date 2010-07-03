deployment_config = '/path/to/mediacore_install/deployment.ini'
temp_dir = '/path/to/mediacore_install/data/tmp'

# NOTE: Before running MediaCore, you will need to update the two paths
#       above to point to the appropriate locations for your installation.

import os
os.environ['TMPDIR'] = temp_dir

if __name__.startswith('_mod_wsgi_'):
    from paste.deploy import loadapp
    application = loadapp('config:'+deployment_config)

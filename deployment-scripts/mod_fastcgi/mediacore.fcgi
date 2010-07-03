#!/path/to/mediacore_env/bin/python
python_egg_cache = '/path/to/mediacore_install/data/python-egg-cache'
deployment_config = '/path/to/mediacore_install/deployment.ini'
temp_dir = '/path/to/mediacore_install/data/tmp'

# NOTE: Before running MediaCore, you will need to update the four paths
#       above to point to the appropriate locations for your installation.

import os
os.environ['PYTHON_EGG_CACHE'] = python_egg_cache
os.environ['TMPDIR'] = temp_dir

if __name__ == '__main__':
    from paste.deploy import loadapp
    app = loadapp('config:'+deployment_config)

    from flup.server.fcgi import WSGIServer
    WSGIServer(app).run()

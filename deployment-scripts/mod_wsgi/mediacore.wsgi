deployment_config = '/path/to/mediacore_install/deployment.ini'
temp_dir = '/path/to/mediacore_install/data/tmp'

# NOTE: Before running MediaCore, you will need to update the two paths
#       above to point to the appropriate locations for your installation.

import os, sys
os.environ['TMPDIR'] = temp_dir
pidfile = 'fastcgi.pid'

def save_pid():
    """ Save the process ID to a file, so we can kill it later.

    Lack of exception handling on this file operation may result in an
    exception being raised and cause Apache to return a 500 error, but
    this is thought to be preferable to starting the server without an
    easy way to kill it.
    """
    fp = open(pidfile)
    fp.write("%d\n" % os.getpid())
    fp.close()

if __name__ == '__main__':
    save_pid()

    from paste.deploy import loadapp
    application = loadapp('config:'+deployment_config)


deployment_config = '/path/to/mediacore_install/deployment.ini'
temp_dir = '/path/to/mediacore_install/data/tmp'

# NOTE: Before running MediaCore, you will need to update the two paths
#       above to point to the appropriate locations for your installation.

import os, sys, pwd, grp
os.environ['TMPDIR'] = temp_dir
pidfile = os.path.dirname(__file__)+os.sep+'wsgi.pid'

def save_pid():
    """ Save the process ID to a file, so we can kill it later.

    Lack of exception handling on this file operation may result in an
    exception being raised and cause Apache to return a 500 error, but
    this is thought to be preferable to starting the server without an
    easy way to kill it.
    """
    try:
        fp = open(pidfile, 'w')
        fp.write("%d\n" % os.getpid())
        fp.close()
    except Exception, e:
        username = "'%s'" % pwd.getpwuid(os.getuid())[0]
        groups = ["'%s'" % grp.getgrgid(x)[0] for x in os.getgroups()]
        print >> sys.stderr, "MEDIACORE ERROR: file \"%s\" must be writeable by user %s or one of the following groups: %s" % (pidfile, username, ', '.join(groups))
        raise e


if __name__.startswith('_mod_wsgi_'):
    save_pid()

    from paste.deploy import loadapp
    application = loadapp('config:'+deployment_config)


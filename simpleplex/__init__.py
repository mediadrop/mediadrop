import sys
def debug(*args):
    """Print to stderr, for debuging"""
    print >> sys.stderr, "Simpleplex DEBUG", args
    return None

def ipython():
    """Launch an ipython shell where called before finishing the request.

    This only works with the Pylons paster server, and obviously ipython
    must be installed as well. Usage::

    simpleplex.ipython()()

    """
    from IPython.Shell import IPShellEmbed
    args = ['-pdb', '-pi1', 'In <\\#>: ', '-pi2', '   .\\D.: ',
            '-po', 'Out<\\#>: ', '-nosep']
    return IPShellEmbed(
        args,
        banner='Entering IPython.  Press Ctrl-D to exit.',
        exit_msg='Leaving Interpreter, back to Pylons.'
    )

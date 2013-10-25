# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""Paster Command Subclasses for use in utilities."""

import os
import sys

import paste.fixture
import paste.registry
import paste.deploy.config
from paste.deploy import loadapp, appconfig
from paste.script.command import Command, BadCommand

import pylons

__all__ = [
    'LoadAppCommand',
    'load_app',
]

class LoadAppCommand(Command):
    """Load the app and all associated StackedObjectProxies.

    Useful for batch scripts.

    The optional CONFIG_FILE argument specifies the config file to use for
    the interactive shell. CONFIG_FILE defaults to 'development.ini'.

    This allows you to test your mapper, models, and simulate web requests
    using ``paste.fixture``.

    This class has been adapted from pylons.commands.ShellCommand.
    """
    summary = __doc__.splitlines()[0]

    min_args = 0
    max_args = 1
    group_name = 'pylons'

    parser = Command.standard_parser()

    parser.add_option('-q',
                      action='count',
                      dest='quiet',
                      default=0,
                      help="Do not load logging configuration from the config file")

    def __init__(self, name, summary):
        self.summary = summary
        Command.__init__(self, name)

    def command(self):
        """Main command to create a new shell"""
        self.verbose = 3
        if len(self.args) == 0:
            # Assume the .ini file is ./development.ini
            config_file = 'development.ini'
            if not os.path.isfile(config_file):
                raise BadCommand('CONFIG_FILE not found at: .%s%s\n'
                                 'Please specify a CONFIG_FILE' % \
                                 (os.path.sep, config_file)
                                )
        else:
            config_file = self.args[0]

        config_name = 'config:%s' % config_file
        here_dir = os.getcwd()

        if not self.options.quiet:
            # Configure logging from the config file
            self.logging_file_config(config_file)
        
        # XXX: Note, initializing CONFIG here is Legacy support. pylons.config
        # will automatically be initialized and restored via the registry
        # restorer along with the other StackedObjectProxys
        # Load app config into paste.deploy to simulate request config
        # Setup the Paste CONFIG object, adding app_conf/global_conf for legacy
        # code
        conf = appconfig(config_name, relative_to=here_dir)
        conf.update(dict(app_conf=conf.local_conf,
                         global_conf=conf.global_conf))
        paste.deploy.config.CONFIG.push_thread_config(conf)

        # Load locals and populate with objects for use in shell
        sys.path.insert(0, here_dir)

        # Load the wsgi app first so that everything is initialized right
        wsgiapp = loadapp(config_name, relative_to=here_dir)
        test_app = paste.fixture.TestApp(wsgiapp)

        # Query the test app to setup the environment
        tresponse = test_app.get('/_test_vars')
        request_id = int(tresponse.body)

        # Disable restoration during test_app requests
        test_app.pre_request_hook = lambda self: \
            paste.registry.restorer.restoration_end()
        test_app.post_request_hook = lambda self: \
            paste.registry.restorer.restoration_begin(request_id)

        # Restore the state of the Pylons special objects
        # (StackedObjectProxies)
        paste.registry.restorer.restoration_begin(request_id)

    def parse_args(self, args):
        self.options, self.args = self.parser.parse_args(args)

def load_app(cmd):
    cmd.parser.usage = "%%prog [options] [CONFIG_FILE]\n%s" % cmd.summary
    try:
        cmd.run(sys.argv[1:])
    except Exception, e:
        print >> sys.stderr, "ERROR:"
        print >> sys.stderr, e
        print >> sys.stderr, ""
        cmd.parser.print_help()
        sys.exit(1)
    return cmd

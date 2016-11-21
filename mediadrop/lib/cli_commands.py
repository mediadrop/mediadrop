# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Paster Command Subclasses for use in utilities."""


from __future__ import absolute_import

import os
import sys

import paste.fixture
import paste.registry
import paste.deploy.config
from paste.deploy import loadapp, appconfig
from paste.script.command import Command, BadCommand

import pylons
from .cli import init_mediadrop

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

        init_mediadrop(config_file, here_dir=os.getcwd(), disable_logging=self.options.quiet)

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

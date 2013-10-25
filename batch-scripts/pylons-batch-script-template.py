#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from mediacore.lib.cli_commands import LoadAppCommand, load_app

_script_name = "Batch Script Template"
_script_description = """Use this script as a model for creating new batch scripts for MediaDrop."""
DEBUG = False

if __name__ == "__main__":
    cmd = LoadAppCommand(_script_name, _script_description)
    cmd.parser.add_option(
        '--debug',
        action='store_true',
        dest='debug',
        help='Write debug output to STDOUT.',
        default=False
    )
    load_app(cmd)
    DEBUG = cmd.options.debug

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import sys

def main(parser, options, args):
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main(cmd.parser, cmd.options, cmd.args)

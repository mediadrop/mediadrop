#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from mediacore.config.environment import load_batch_environment

def parse_options():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--ini', dest='ini_file', help='Specify the .ini file to read pylons settings from.', default='deployment.ini', metavar='INI_FILE')
    parser.add_option('--ini-path', dest='ini_path', help='Relative path to the .ini file.', default='..', metavar='INI_PATH')
    parser.add_option('--debug', action='store_true', dest='debug', help='Write debug output to STDOUT.', default=False)
    options, args = parser.parse_args()
    return parser, options, args

DEBUG = False
if __name__ == "__main__":
    parser, options, args = parse_options()
    DEBUG = options.debug
    load_batch_environment(options.ini_path, options.ini_file)

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import sys

def main(parser):
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main(parser)

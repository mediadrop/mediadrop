#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mediacore.lib.cli_commands import LoadAppCommand, load_app

_script_name = "Database Upgrade Script for former v0.7.2 users"
_script_description = """Use this script to upgrade your v0.7.2 database to the latest version.

Specify your ini config file as the first argument to this script.

This script simply assigns your database the correct migrate version
and runs all pending migrations since then. After running this script
you will not need to use another update script -- simply run
paster setup-app development.ini to apply any pending migrations."""
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
from migrate.versioning.api import version_control, version, upgrade
from migrate.exceptions import DatabaseAlreadyControlledError
from pylons import config

initial_version = 0
migrate_repository = 'mediacore/migrations'

def main(parser, options, args):
    engine_url = config['sqlalchemy.url']
    latest_version = version(migrate_repository)
    try:
        version_control(engine_url,
                        migrate_repository,
                        version=initial_version,
                        echo=DEBUG)
    except DatabaseAlreadyControlledError:
        pass
    upgrade(engine_url, migrate_repository, version=latest_version, echo=DEBUG)
    sys.exit(0)

if __name__ == "__main__":
    main(cmd.parser, cmd.options, cmd.args)

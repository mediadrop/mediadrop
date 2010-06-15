#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# SETUP PYLONS APP & ENVIRONMENT
from paste.deploy import appconfig
from mediacore.config.environment import load_environment

# Load the application config
config_dir = '../..'
config_file = 'deployment.ini'
conf = appconfig('config:'+config_file, relative_to=config_dir)

# Load the logging options
# (must be done before environment is loaded or sqlalchemy won't log)
import os
from paste.script.util.logging_config import fileConfig
fileConfig(config_dir+os.sep+config_file)

# Load the environment
config = load_environment(conf.global_conf, conf.local_conf)

# Set up globals for helper libs to use (like pylons.config)
from paste.registry import Registry
import pylons
reg = Registry()
reg.prepare()
reg.register(pylons.config, config)

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import sys

if __name__ == "__main__":
    print "Running the script successfully..."
    sys.exit(0)

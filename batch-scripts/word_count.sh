#!/bin/sh
#
# DESCRIPTION
# Prints a line/word/character count of all the main, first-party,
# source files in MediaCore.
#
# DEPENDENCIES
# This script depends on the common unix utilities:
#     'find', 'grep', 'xargs', and 'wc'

pushd `dirname $0` > /dev/null
	pushd .. > /dev/null
		find batch-scripts deployment-scripts mediacore setup* -type f | grep -v third-party | grep -v "/images/" | grep -v ".pyc$" | xargs wc
	popd > /dev/null
popd > /dev/null

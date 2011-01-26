#!/bin/sh
#
# DESCRIPTION
# Uses the "tx" transifex command line utility to pull the given
# comma-separated string of locales, update and compile those catalogs,
# and add them to git.
#
# Since "tx" uses file mtimes to decide whether to skip a translation, it
# is necessary to manually enumerate which locales have been updated and
# should be downloaded.
#
# If you simply want to update all translations this command will suffice:
#     tx pull -a -f && python setup.py update_catalog && python setup.py compile_catalog
#
# DEPENDENCIES
# This script depends on a properly configured transifex CLI utility.
#     http://help.transifex.net/user-guide/client/client-0.4.html
#
# This script also depends on the common unix utilities:
#     'tr', 'xargs'

tx pull -f -l $1
echo $1 | tr "," "\n" | xargs -I % python setup.py update_catalog -l %
echo $1 | tr "," "\n" | xargs -I % python setup.py compile_catalog -l %
echo $1 | tr "," "\n" | xargs -t -I % git add mediacore/i18n/%


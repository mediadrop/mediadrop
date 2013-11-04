#!/bin/sh
#
# DESCRIPTION
# Strips colour profile information, and performs optimal data compression on
# all PNG images in the directories:
#     mediadrop/public/images
#     mediadrop/public/admin/images
#
# DEPENDENCIES
# This script depends on the common unix utilities:
#     'find'
# and the software package:
#     'pngcrush' -- available via your package manager, or at
#                   http://pmt.sourceforge.net/pngcrush/

pushd `dirname $0` > /dev/null
	pushd ../mediadrop/public > /dev/null
		for x in `find images admin/images -iname "*.png"`;
		do
			pngcrush -brute -rem gAMA -rem cHRM -rem iCCP -rem sRGB "$x" "$x.crsh";
			mv "$x.crsh" "$x";
		done;
	popd > /dev/null
popd > /dev/null

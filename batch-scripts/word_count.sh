#!/bin/sh

pushd `dirname $0` > /dev/null
	pushd .. > /dev/null
		find batch-scripts deployment-scripts mediacore setup* -type f | grep -v third-party | grep -v "/images/" | grep -v ".pyc$" | xargs wc
	popd > /dev/null
popd > /dev/null

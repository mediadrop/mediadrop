#!/bin/sh

# If the PID file exists, attempt to kill the identified process.
PIDFILE="fastcgi.pid"
if [ -f $PIDFILE ]; then
	kill `cat -- $PIDFILE` && echo "MediaCore successfully stopped" && exit 0
fi
# If we got here, there was a problem
exit 1

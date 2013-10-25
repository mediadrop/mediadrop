#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of MediaDrop, Copyright 2009-2013 MediaDrop contributors
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

from mediacore.lib.cli_commands import LoadAppCommand, load_app

_script_name = "Database Upgrade Script for v0.9.x users with Facebook comments"
_script_description = """Use this script to preserve your existing Facebook
comments.

Specify your ini config file as the first argument to this script.

This script queries Facebook for each media to see if there are already 
comments stored for that media. If so the script will ensure that the old
(XFBML/xid based) Facebook comment plugin is used."""
DEBUG = False

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import sys
import urllib

from pylons import app_globals
import simplejson as json
from sqlalchemy.orm import joinedload


class FacebookAPI(object):
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = None
    
    def _request(self, url, **parameters):
        response = urllib.urlopen(url % parameters)
        return response.read().strip()
    
    def access_token(self):
        if self._token:
            return self._token
        oauth_url = 'https://graph.facebook.com/oauth/access_token?type=client_cred&client_id=%(app_id)s&client_secret=%(app_secret)s'
        content = self._request(oauth_url, app_id=self.app_id, app_secret=self.app_secret)
        assert content.startswith('access_token')
        self._token = content.split('access_token=', 1)[1]
        return self._token
    
    def number_xid_comments(self, media):
        token = self.access_token()
        graph_url = 'https://graph.facebook.com/fql?q=select+text+from+comment+where+is_private=0+and+xid=%(xid)d&access_token=%(access_token)s'
        content = self._request(graph_url, xid=media.id, access_token=self.access_token())
        comments_data = json.loads(content)
        if 'error' in comments_data:
            error = comments_data['error']
            print 'Media %d - %s: %s (code %s)' % (media.id, error['type'], error['message'], error['code'])
            sys.exit(2)
        return comments_data['data']
    
    def has_xid_comments(self, media):
        return self.number_xid_comments(media) > 0

class DummyProgressBar(object):
    def __init__(self, maxval=None):
        pass
    
    def start(self):
        return self
    
    def update(self, value):
        sys.stdout.write('.')
        sys.stdout.flush()
    
    def finish(self):
        sys.stdout.write('\n')
        sys.stdout.flush()

try:
    from progressbar import ProgressBar
except ImportError:
    ProgressBar = DummyProgressBar
    print 'Install the progressbar module for nice progress reporting'
    print '    $ pip install http://python-progressbar.googlecode.com/files/progressbar-2.3.tar.gz'
    print

def main(parser, options, args):
    app_globs = app_globals._current_obj()
    app_id = app_globals.settings['facebook_appid']
    if not app_id:
        print 'No Facebook app_id configured, exiting'
        sys.exit(3)
    
    app_secret = options.app_secret
    fb = FacebookAPI(app_id, app_secret)
    
    from mediacore.model import DBSession, Media
    # eager loading of 'meta' to speed up later check.
    all_media = Media.query.options(joinedload('_meta')).all()
    
    print 'Checking all media for existing Facebook comments'
    progress = ProgressBar(maxval=len(all_media)).start()
    for i, media in enumerate(all_media):
        progress.update(i+1)
        if 'facebook-comment-xid' not in media.meta:
            continue
        if not fb.has_xid_comments(media):
            continue
        media.meta[u'facebook-comment-xid'] = unicode(media.id)
        DBSession.add(media)
        DBSession.commit()

    progress.finish()

if __name__ == "__main__":
    cmd = LoadAppCommand(_script_name, _script_description)
    cmd.parser.add_option(
        '--app-secret',
        action='store',
        dest='app_secret',
        help='Facebook app_secret for the app_id stored in MediaDrop',
    )
    load_app(cmd)
    if len(cmd.args) < 1:
        print 'usage: %s <ini>' % sys.argv[0]
        sys.exit(1)
    elif not cmd.options.app_secret:
        print 'please specify the app_secret with "--app-secret=..."'
        sys.exit(1)
    main(cmd.parser, cmd.options, cmd.args)


# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

__all__ = ['Facebook']

from mediacore.lib.js_delivery import InlineJS, Script, Scripts

class FacebookSDKScript(InlineJS):
    def __init__(self, app_id, extra_code=None):
        code = u'''
		window.fbAsyncInit = function() {
			FB.init({
				appId  : '%s',
				status : true, // check login status
				cookie : true, // enable cookies to allow the server to access the session
				xfbml  : true  // parse XFBML
			});
			%s
		};''' % (app_id, extra_code or '')
        super(FacebookSDKScript, self).__init__(code, key='fb_async_init')


class Facebook(object):
    def __init__(self, app_id):
        self.app_id = app_id
        self.scripts = Scripts(
            FacebookSDKScript(self.app_id), 
            # '//' is a protocol-relative URL, uses HTTPS if the page uses HTTPS
            Script('//connect.facebook.net/en_US/all.js', async=True)
        )
    
    def init_code(self):
        return u'<div id="fb-root"></div>' + self.scripts.render()


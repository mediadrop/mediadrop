# -*- coding: utf-8 -*-
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import simplejson as json

from .json_html_encoder import JSONEncoderForHTML


__all__ = ['as_safe_json', 'json']

def as_safe_json(s):
    return json.dumps(s, cls=JSONEncoderForHTML)


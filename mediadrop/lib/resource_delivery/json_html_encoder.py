# -*- coding: utf-8 -*-
# The source code in this file was copied from simplejson 3.6.3 as published on
# https://pypi.python.org/pypi/simplejson/3.6.3
# License statement from the simplejson tarball:
# simplejson is dual-licensed software. It is available under the terms
# of the MIT license, or the Academic Free License version 2.1. The full
# text of each license agreement is included below. This code is also
# licensed to the Python Software Foundation (PSF) under a Contributor
# Agreement.

from simplejson.encoder import JSONEncoder
# -----------------------------------------------------------------------------
class JSONEncoderForHTML(JSONEncoder):
    """An encoder that produces JSON safe to embed in HTML.

    To embed JSON content in, say, a script tag on a web page, the
    characters &, < and > should be escaped. They cannot be escaped
    with the usual entities (e.g. &amp;) because they are not expanded
    within <script> tags.
    """

    def encode(self, o):
        # Override JSONEncoder.encode because it has hacks for
        # performance that make things more complicated.
        chunks = self.iterencode(o, True)
        if self.ensure_ascii:
            return ''.join(chunks)
        else:
            return u''.join(chunks)

    def iterencode(self, o, _one_shot=False):
        chunks = super(JSONEncoderForHTML, self).iterencode(o, _one_shot)
        for chunk in chunks:
            chunk = chunk.replace('&', '\\u0026')
            chunk = chunk.replace('<', '\\u003c')
            chunk = chunk.replace('>', '\\u003e')
            yield chunk
# --- end of copy -------------------------------------------------------------


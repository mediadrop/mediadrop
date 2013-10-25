# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode import Schema

from mediacore.forms import TextField, XHTMLValidator, email_validator
from mediacore.lib.i18n import N_

class PostCommentSchema(Schema):
    name = TextField.validator(not_empty=True, maxlength=50,
        messages={'empty': N_('Please enter your name!')})
    email = email_validator()
    body = XHTMLValidator(not_empty=True)

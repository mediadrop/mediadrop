# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Email Helpers

.. todo::

    Clean this module up and use genshi text templates.

.. autofunc:: send

.. autofunc:: send_media_notification

.. autofunc:: send_comment_notification

.. autofunc:: parse_email_string

"""

import smtplib

from pylons import app_globals
from pylons.i18n import _

from mediacore.lib.helpers import line_break_xhtml, strip_xhtml, url_for

def parse_email_string(string):
    """Take a comma separated string of emails and return a list."""
    if not string:
        elist = []
    elif ',' in string:
        elist = string.split(',')
        elist = [email.strip() for email in elist]
    else:
        elist = [string]
    return elist

def send(to_addr, from_addr, subject, body):
    """Send an email!

    Expects subject and body to be unicode strings.
    """
    server = smtplib.SMTP('localhost')
    if isinstance(to_addr, basestring):
        to_addr = parse_email_string(to_addr)

    to_addr = ", ".join(to_addr)

    msg = _("To: %(to_addr)s\n"
           "From: %(from_addr)s\n"
           "Subject: %(subject)s\n\n"
           "%(body)s\n") % locals()

    server.sendmail(from_addr, to_addr, msg.encode('utf-8'))
    server.quit()


def send_media_notification(media_obj):
    send_to = app_globals.settings['email_media_uploaded']
    if not send_to:
        # media notification emails are disabled!
        return

    edit_url = url_for(controller='/admin/media', action='edit',
                       id=media_obj.id, qualified=True),

    clean_description = strip_xhtml(line_break_xhtml(line_break_xhtml(media_obj.description)))

    type = media_obj.type
    title = media_obj.title
    author_name = media_obj.author.name
    author_email = media_obj.author.email
    subject = _('New %(type)s: %(title)s') % locals()
    body = _("""A new %(type)s file has been uploaded!

Title: %(title)s

Author: %(author_name)s (%(author_email)s)

Admin URL: %(edit_url)s

Description: %(clean_description)s
""") % locals()

    send(send_to, app_globals.settings['email_send_from'], subject, body)

def send_comment_notification(media_obj, comment):
    send_to = app_globals.settings['email_comment_posted']
    if not send_to:
        # Comment notification emails are disabled!
        return

    author_name = media_obj.author.name
    comment_subject = comment.subject
    post_url = url_for(controller='/media', action='view', slug=media_obj.slug, qualified=True),
    comment_body = strip_xhtml(line_break_xhtml(line_break_xhtml(comment.body)))
    subject = _('New Comment: %(comment_subject)s') % locals()
    body = _("""A new comment has been posted!

Author: %(author_name)s
Post: %(post_url)s

Body: %(comment_body)s
""") % locals()

    send(send_to, app_globals.settings['email_send_from'], subject, body)

def send_support_request(email, url, description, get_vars, post_vars):
    send_to = app_globals.settings['email_support_requests']
    if not send_to:
        return

    get_vars = "\n\n  ".join([x + " :  " + get_vars[x] for x in get_vars]),
    post_vars = "\n\n  ".join([x + " :  " + post_vars[x] for x in post_vars])
    subject = _('New Support Request: %(email)s') % locals()
    body = _("""A user has asked for support

Email: %(email)s

URL: %(url)s

Description: %(description)s

GET_VARS:
%(get_vars)s


POST_VARS:
%(post_vars)s
""") % locals()

    send(send_to, app_globals.settings['email_send_from'], subject, body)

# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Email Helpers

.. todo::

    Clean this module up and use genshi text templates.

.. autofunction:: send

.. autofunction:: send_media_notification

.. autofunction:: send_comment_notification

.. autofunction:: parse_email_string

"""

import smtplib

from pylons import config, request

from mediacore.lib.helpers import (line_break_xhtml, strip_xhtml, url_for, 
    url_for_media)
from mediacore.lib.i18n import _

def parse_email_string(string):
    """
    Convert a string of comma separated email addresses to a list of
    separate strings.
    """
    if not string:
        elist = []
    elif ',' in string:
        elist = string.split(',')
        elist = [email.strip() for email in elist]
    else:
        elist = [string]
    return elist

def send(to_addrs, from_addr, subject, body):
    """A simple method to send a simple email.

    :param to_addrs: Comma separated list of email addresses to send to.
    :type to_addrs: unicode

    :param from_addr: Email address to put in the 'from' field
    :type from_addr: unicode

    :param subject: Subject line of the email.
    :type subject: unicode

    :param body: Body text of the email, optionally marked up with HTML.
    :type body: unicode
    """
    smtp_server = config.get('smtp_server', 'localhost')
    server = smtplib.SMTP(smtp_server)
    if isinstance(to_addrs, basestring):
        to_addrs = parse_email_string(to_addrs)

    to_addrs = ", ".join(to_addrs)

    msg = ("To: %(to_addrs)s\n"
           "From: %(from_addr)s\n"
           "Subject: %(subject)s\n\n"
           "%(body)s\n") % locals()

    smtp_username = config.get('smtp_username')
    smtp_password = config.get('smtp_password')
    if smtp_username and smtp_password:
        server.login(smtp_username, smtp_password)

    server.sendmail(from_addr, to_addrs, msg.encode('utf-8'))
    server.quit()


def send_media_notification(media_obj):
    """
    Send a creation notification email that a new Media object has been
    created.

    Sends to the address configured in the 'email_media_uploaded' address,
    if one has been created.

    :param media_obj: The media object to send a notification about.
    :type media_obj: :class:`~mediacore.model.media.Media` instance
    """
    send_to = request.settings['email_media_uploaded']
    if not send_to:
        # media notification emails are disabled!
        return

    edit_url = url_for(controller='/admin/media', action='edit',
                       id=media_obj.id, qualified=True)

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

    send(send_to, request.settings['email_send_from'], subject, body)

def send_comment_notification(media_obj, comment):
    """
    Helper method to send a email notification that a comment has been posted.

    Sends to the address configured in the 'email_comment_posted' setting,
    if it is configured.

    :param media_obj: The media object to send a notification about.
    :type media_obj: :class:`~mediacore.model.media.Media` instance

    :param comment: The newly posted comment.
    :type comment: :class:`~mediacore.model.comments.Comment` instance
    """
    send_to = request.settings['email_comment_posted']
    if not send_to:
        # Comment notification emails are disabled!
        return

    author_name = media_obj.author.name
    comment_subject = comment.subject
    post_url = url_for_media(media_obj, qualified=True)
    comment_body = strip_xhtml(line_break_xhtml(line_break_xhtml(comment.body)))
    subject = _('New Comment: %(comment_subject)s') % locals()
    body = _("""A new comment has been posted!

Author: %(author_name)s
Post: %(post_url)s

Body: %(comment_body)s
""") % locals()

    send(send_to, request.settings['email_send_from'], subject, body)

def send_support_request(email, url, description, get_vars, post_vars):
    """
    Helper method to send a Support Request email in response to a server
    error.

    Sends to the address configured in the 'email_support_requests' setting,
    if it is configured.

    :param email: The requesting user's email address.
    :type email: unicode

    :param url: The url that the user requested assistance with.
    :type url: unicode

    :param description: The user's description of their problem.
    :type description: unicode

    :param get_vars: The GET variables sent with the failed request.
    :type get_vars: dict of str -> str

    :param post_vars: The POST variables sent with the failed request.
    :type post_vars: dict of str -> str
    """
    send_to = request.settings['email_support_requests']
    if not send_to:
        return

    get_vars = "\n\n  ".join(x + " :  " + get_vars[x] for x in get_vars)
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

    send(send_to, request.settings['email_send_from'], subject, body)

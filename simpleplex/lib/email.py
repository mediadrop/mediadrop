"""
Email Helpers

.. autofunc:: send

.. autofunc:: send_media_notification

.. autofunc:: send_comment_notification

"""
import smtplib
from tg import config, request
from simpleplex.lib.helpers import url_for, clean_xhtml, strip_xhtml, line_break_xhtml


def send(to_addr, from_addr, subject, body):
    """Send an email!

    Expects subject and body to be unicode strings.
    """
    server = smtplib.SMTP('localhost')

    msg = """To: %s
From: %s
Subject: %s

%s
""" % (", ".join(to_addr), from_addr, subject, body)

    server.sendmail(from_addr, to_addr, msg.encode('utf-8'))
    server.quit()


def send_media_notification(media_obj):
    send_to = fetch_setting('email_media_uploaded')
    if not send_to:
        # media notification emails are disabled!
        return

    edit_url = url_for(controller='mediaadmin', action='edit',
                       id=media_obj.id, qualified=True),

    clean_description = strip_xhtml(
            line_break_xhtml(line_break_xhtml(media_obj.description)))

    subject = 'New %s: %s' % (media_obj.type, media_obj.title)
    body = """A new %s file has been uploaded!

Title: %s

Author: %s (%s)

Admin URL: %s

Description: %s
""" % (media_obj.type, media_obj.title, media_obj.author.name,
       media_obj.author.email, edit_url, clean_description)

    send(send_to, fetch_setting('email_send_from'), subject, body)

def send_comment_notification(media, comment):
    send_to = fetch_setting('email_comment_posted')
    if not send_to:
        # Comment notification emails are disabled!
        return

    subject = 'New Comment: %s' % comment.subject
    body = """A new comment has been posted!

Author: %s
Post: %s

Body: %s
""" % (comment.author.name,
    url_for(controller='media', action='view', slug=media.slug, qualified=True),
    strip_xhtml(line_break_xhtml(line_break_xhtml(comment.body))))

    send(send_to, fetch_setting('email_send_from'), subject, body)

def send_support_request(email, url, description, get_vars, post_vars):
    send_to = fetch_setting('email_support_requests')
    if not send_to:
        return

    subject = 'New Support Request: %s' % email
    body = """A user has asked for support

Email: %s

URL: %s

Description: %s

GET_VARS:
%s


POST_VARS:
%s
""" % (
    email,
    url,
    description,
    "\n\n  ".join([x + " :  " + get_vars[x] for x in get_vars]),
    "\n\n  ".join([x + " :  " + post_vars[x] for x in post_vars])
    )

    send(send_to, fetch_setting('email_send_from'), subject, body)

import smtplib
from mediaplex.lib.helpers import url_for, clean_xhtml, strip_xhtml, line_break_xhtml

def send(to_addr, from_addr, subject, body):
    server = smtplib.SMTP('localhost')

    msg = """To: %s
From: %s
Subject: %s

%s
""" % (", ".join(to_addr), from_addr, subject, body)

    server.sendmail(from_addr, to_addr, msg)
    server.quit()

def send_video_notification(video):
    fr = 'noreply@tmcyouth.com'
    to = ['anthony@simplestation.com', 'videos@tmcyouth.com']
    subject = 'New Video: %s' % video.title
    body = """A new video has been uploaded!

Title: %s

Author: %s (%s)

Admin URL: %s

Description: %s
""" % (video.title, video.author.name, video.author.email,
    'http://' + request.environ['HTTP_HOST'] + url_for(controller='mediaadmin', action='edit', id=video.id),
    strip_xhtml(line_break_xhtml(line_break_xhtml(video.description))))

    send(to, fr, subject, body)

def send_comment_notification(media, comment):
    fr = 'noreply@tmcyouth.com'
    to = ['anthony@simplestation.com', 'notifications@tmcyouth.com']
    subject = 'New Comment: %s' % comment.subject
    body = """A new comment has been posted!

Author: %s
Post: %s

Body: %s
""" % (comment.author.name,
    'http://' + request.environ['HTTP_HOST'] + url_for(controller='media', action='view', slug=media.slug),
    strip_xhtml(line_break_xhtml(line_break_xhtml(comment.body))))

    send(to, fr, subject, body)


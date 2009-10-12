from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates

from simpleplex.model import DeclarativeBase, metadata, DBSession, slugify, _mtm_count_property

EMAIL_MEDIA_UPLOADED = 'email_media_uploaded'
EMAIL_COMMENT_POSTED = 'email_comment_posted'
EMAIL_SUPPORT_REQUESTS = 'email_support_requests'
EMAIL_SEND_FROM = 'email_send_from'
FTP_SERVER = 'ftp_server'
FTP_USERNAME = 'ftp_username'
FTP_PASSWORD = 'ftp_password'
FTP_UPLOAD_PATH = 'ftp_upload_path'
FTP_DOWNLOAD_URL = 'ftp_download_url'
WORDING_USER_UPLOADS = 'wording_user_uploads'

settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Setting(object):
    """Setting definition
    """
    def __init__(self, key=None, value=None):
        self.key = key or None
        self.value = value or None

    def __repr__(self):
        return '<Setting: %s = %s>' % (self.key, self.value)

    def __unicode__(self):
        return '%s = %s' % (self.key, self.value)

mapper(Setting, settings)

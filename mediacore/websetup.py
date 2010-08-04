"""Setup the MediaCore application"""
import logging
import os.path

import pylons
import pylons.test
from sqlalchemy.orm import class_mapper
from migrate.versioning.api import version_control, version, upgrade
from migrate.versioning.exceptions import DatabaseAlreadyControlledError

from mediacore.config.environment import load_environment
from mediacore.model import (DBSession, metadata, Media, Podcast,
    User, Group, Permission, Tag, Category, Comment, Setting, Author,
    AuthorWithIP)

log = logging.getLogger(__name__)

migrate_repository = 'mediacore/migrations'

def setup_app(command, conf, vars):
    """Called by ``paster setup-app``.

    This script is responsible for:

        * Creating the initial database schema and loading default data.
        * Executing any migrations necessary to bring an existing database
          up-to-date. Your data should be safe but, as always, be sure to
          make backups before using this.
        * Re-creating the default database for every run of the test suite.

    XXX: All your data will be lost IF you run the test suite with a
         config file named 'test.ini'. Make sure you have this configured
         to a different database than in your usual deployment.ini or
         development.ini file because all database tables are dropped a
         and recreated every time this script runs.

    XXX: If you are upgrading from MediaCore v0.7.2 or v0.8.0, run whichever
         one of these that applies:
           ``python batch-scripts/upgrade/upgrade_from_v072.py deployment.ini``
           ``python batch-scripts/upgrade/upgrade_from_v080.py deployment.ini``

    XXX: For search to work, we depend on a number of MySQL triggers which
         copy the data from our InnoDB tables to a MyISAM table for its
         fulltext indexing capability. Triggers can only be installed with
         a mysql superuser like root, so you must run the setup_triggers.sql
         script yourself.

    """
    if pylons.test.pylonsapp:
        # NOTE: This extra filename check may be unnecessary, the example it is
        # from did not check for pylons.test.pylonsapp. Leaving it in for now
        # to make it harder for someone to accidentally delete their database.
        filename = os.path.split(conf.filename)[-1]
        if filename == 'test.ini':
            log.info('Dropping existing tables...')
            metadata.drop_all(checkfirst=True)
    else:
        # Don't reload the app if it was loaded under the testing environment
        load_environment(conf.global_conf, conf.local_conf)

    # Have the tables already been created? If not, we'll add data later
    db_is_fresh = not class_mapper(Media).mapped_table.exists()

    log.info("Creating tables if they don't exist yet")
    metadata.create_all(bind=DBSession.bind, checkfirst=True)

    # Create the migrate_version table if it doesn't exist.
    # If the table doesn't exist, we assume the schema was just setup
    # by this script and therefore must be the latest version.
    latest_version = version(migrate_repository)
    try:
        version_control(conf.local_conf['sqlalchemy.url'],
                        migrate_repository,
                        version=latest_version)
        log.info('Migrate table created with version %s' % latest_version)
    except DatabaseAlreadyControlledError:
        log.info('Migrate table already present')

    # Run any new migrations, if there are any
    upgrade(conf.local_conf['sqlalchemy.url'],
            migrate_repository,
            version=latest_version)

    # If the tables are new, populate with the default data.
    if db_is_fresh:
        add_default_data()

    # Save everything, along with the dummy data if applicable
    DBSession.commit()
    log.info('Successfully setup')

def add_default_data():
    log.info('Adding default data')

    settings = [
        (u'email_media_uploaded', None),
        (u'email_comment_posted', None),
        (u'email_support_requests', None),
        (u'email_send_from', u'noreply@localhost'),
        (u'wording_user_uploads', u"Upload your media using the form below. We'll review it and get back to you."),
        (u'wording_additional_notes', None),
        (u'popularity_decay_exponent', u'4'),
        (u'popularity_decay_lifetime', u'36'),
        (u'rich_text_editor', u'tinymce'),
        (u'google_analytics_uacct', u''),
        (u'flash_player', u'jwplayer'),
        (u'html5_player', u'zencoder-video-js'),
        (u'player_type', u'best'),
        (u'featured_category', u'1'),
        (u'max_upload_size', u'314572800'),
        (u'ftp_storage', u'false'),
        (u'ftp_server', u'ftp.someserver.com'),
        (u'ftp_user', u'username'),
        (u'ftp_password', u'password'),
        (u'ftp_upload_directory', u'media'),
        (u'ftp_download_url', u'http://www.someserver.com/web/accessible/media/'),
        (u'ftp_upload_integrity_retries', u'10'),
        (u'akismet_key', u''),
        (u'akismet_url', u''),
        (u'req_comment_approval', u'false'),
        (u'use_embed_thumbnails', u'true'),
    ]

    for key, value in settings:
        s = Setting()
        s.key = key
        s.value = value
        DBSession.add(s)

    u = User()
    u.user_name = u'admin'
    u.display_name = u'Admin'
    u.email_address = u'admin@somedomain.com'
    u.password = u'admin'
    DBSession.add(u)

    g = Group()
    g.group_name = u'admins'
    g.display_name = u'Admins'
    g.users.append(u)
    DBSession.add(g)

    p = Permission()
    p.permission_name = u'admin'
    p.description = u'Grants access to the admin panel'
    p.groups.append(g)
    DBSession.add(p)

    category = Category()
    category.name = u'Featured'
    category.slug = u'featured'
    DBSession.add(category)

    podcast = Podcast()
    podcast.slug = u'hello-world'
    podcast.title = u'Hello World'
    podcast.subtitle = u'My very first podcast!'
    podcast.description = u"""<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"""
    podcast.category = u'Technology'
    podcast.author = Author(u.display_name, u.email_address)
    podcast.explicit = None
    podcast.copyright = u'Copyright 2009 Xyz'
    podcast.itunes_url = None
    podcast.feedburner_url = None
    DBSession.add(podcast)

    comment = Comment()
    comment.subject = u'Re: New Media'
    comment.author = AuthorWithIP(name=u'John Doe', ip=2130706433)
    comment.body = u'<p>Hello to you too!</p>'
    DBSession.add(comment)

    media = Media()
    media.type = None
    media.slug = u'new-media'
    media.reviewed = True
    media.encoded = False
    media.publishable = False
    media.title = u'New Media'
    media.subtitle = None
    media.description = u"""<p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"""
    media.description_plain = u"""Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
    media.author = Author(u.display_name, u.email_address)
    media.categories.append(category)
    media.comments.append(comment)
    DBSession.add(media)

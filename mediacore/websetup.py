"""Setup the MediaCore application"""
import logging
import os.path

import pylons
import pylons.test
from sqlalchemy.orm import class_mapper
from migrate.versioning.api import version_control, version, upgrade
from migrate.versioning.exceptions import DatabaseAlreadyControlledError

from mediacore.config.environment import load_environment
from mediacore.model import (DBSession, metadata, Media, MediaFile, Podcast,
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
        (u'html5_player', u'html5'),
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

    category2 = Category()
    category2.name = u'Instructional'
    category2.slug = u'instructional'
    DBSession.add(category2)

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

    import datetime
    instructional_media = [
        (u'workflow-in-mediacore',
        u'Workflow in MediaCore',
        u'<p>This sceencast explains the publish status feature in MediaCore.</p><p>Initially all videos uploaded through the front-end or admin panel are placed under &quot;awaiting review&quot; status. Once the administrator hits the &quot;review complete&quot; button, they can upload media. Videos can be added in any format, however, they can only be published if they are in a web-ready format such as FLV, M4V, MP3, or MP4. Alternatively, if they are published through Youtube or Vimeo the encoding step is skipped</p><p>Once uploaded and encoded the administrator can then publish the video.</p>',
        u'This sceencast explains the publish status feature in MediaCore.\nInitially all videos uploaded through the front-end or admin panel are placed under \"awaiting review\" status. Once the administrator hits the \"review complete\" button, they can upload media. Videos can be added in any format, however, they can only be published if they are in a web-ready format such as FLV, M4V, MP3, or MP4. Alternatively, if they are published through Youtube or Vimeo the encoding step is skipped\nOnce uploaded and encoded the administrator can then publish the video.',
        datetime.datetime(2010, 5, 13, 2, 29, 40),
        218,
        u'http://getmediacore.com/files/tutorial-workflow-in-mediacore.mp4',
        u'video',
        u'mp4',
        ),
        (u'creating-a-podcast-in-mediacore',
        u'Creating a Podcast in MediaCore',
        u'<p>This describes the process an administrator goes through in creating a podcast in MediaCore. An administrator can enter information that will automatically generate the iTunes/RSS feed information. Any episodes published to a podcast will automatically publish to iTunes/RSS.</p>',
        u'This describes the process an administrator goes through in creating a podcast in MediaCore. An administrator can enter information that will automatically generate the iTunes/RSS feed information. Any episodes published to a podcast will automatically publish to iTunes/RSS.',
        datetime.datetime(2010, 5, 13, 2, 33, 44),
        100,
        u'http://getmediacore.com/files/tutorial-create-podcast-in-mediacore.mp4',
        u'video',
        u'mp4',
        ),
        (u'adding-a-video-in-mediacore',
        u'Adding a Video in MediaCore',
        u'<p>This screencast shows how video or audio can be added in MediaCore.</p><p>MediaCore supports a wide range of formats including (but not limited to): YouTube, Vimeo, Google Video, Amazon S3, Bits on the Run, BrightCove, Kaltura, and either your own server or someone else\'s.</p><p>Videos can be uploaded in any format, but can only be published in web-ready formats such as FLV, MP3, M4V, MP4 etc.</p>',
        u'This screencast shows how video or audio can be added in MediaCore.\nMediaCore supports a wide range of formats including (but not limited to): YouTube, Vimeo, Google Video, Amazon S3, Bits on the Run, BrightCove, Kaltura, and either your own server or someone else\'s.\nVideos can be uploaded in any format, but can only be published in web-ready formats such as FLV, MP3, M4V, MP4 etc.',
        datetime.datetime(2010, 5, 13, 02, 37, 36),
        169,
        u'http://getmediacore.com/files/tutorial-add-video-in-mediacore.mp4',
        u'video',
        u'mp4',
        ),
    ]

    name = u'MediaCore Team'
    email = u'info@simplestation.com'
    for slug, title, desc, desc_plain, publish_on, duration, url, type, container in instructional_media:
        media = Media()
        media.author = Author(name, email)
        media.description = desc
        media.description_plain = desc_plain
        media.duration = duration
        media.publish_on = publish_on
        media.slug = slug
        media.title = title

        media_file = MediaFile()
        media_file.container = container
        media_file.created_on = publish_on
        media_file.display_name = os.path.basename(url)
        media_file.duration = duration
        media_file.type = type
        media_file.url = url

        DBSession.add(media)
        DBSession.add(media_file)

        media.files.append(media_file)
        media.categories.append(category2)

        media.encoded = True
        media.reviewed = True
        media.publishable = True

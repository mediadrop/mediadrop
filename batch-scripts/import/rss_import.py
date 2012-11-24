#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from mediacore.lib.cli_commands import LoadAppCommand, load_app

_script_name = "RSS Podcast Importer Script"
_script_description = """Use this script to create new MediaCore podcasts from RSS feeds.

By default, files are left on the server that hosts them. Use the --save-files
flag to download files locally.

By default, all categorization keywords are treated as Categories. Use the
--tags flag to treat them as tags instead.
"""
DEBUG = False

if __name__ == "__main__":
    cmd = LoadAppCommand(_script_name, _script_description)
    cmd.parser.add_option('-u', '--uri', dest='uri', help='An HTTP/HTTPS/FTP URL or a local filename from which to read the RSS feed.', metavar='URI')
    cmd.parser.add_option('--save-files', action='store_true', dest='save_files', help='Download the files linked from the feed, to host locally.')
    cmd.parser.add_option('--tags', action='store_true', dest='tags', help='Treat categorization keywords as tags instead of categories.', default=False)
    cmd.parser.add_option('--debug', action='store_true', dest='debug', help='Write debug output to STDOUT.', default=False)
    load_app(cmd)
    DEBUG = cmd.options.debug

# BEGIN SCRIPT & SCRIPT SPECIFIC IMPORTS
import sys
try:
    import feedparser
except ImportError:
    print 'please install the "feedparser" module'
    sys.exit(1)
import re
import urllib2
import urlparse
import tempfile
from datetime import datetime
from mediacore.model import Author, Media, MediaFile, Podcast, slugify, get_available_slug
from mediacore.model.meta import DBSession
from mediacore.lib.helpers import duration_to_seconds
from mediacore.lib.thumbnails import create_default_thumbs_for, create_thumbs_for
from mediacore.lib.mediafiles import add_new_media_file

img_regex = re.compile(""".*<\s*img\s*.*?src\s*=\s*(("[^"]+")|('[^']')).*?>.*""", re.MULTILINE)

def podcast_from_feed(d, tags=False, save_files=False):
    # Assume not explicit
    explicit = False
    if 'itunes_explicit' in d['feed']:
        explicit = bool(d['feed']['itunes_explicit'])

    image = None
    if 'image' in d['feed']:
        image = d['feed']['image']['href']

    title = u''
    if 'title' in d['feed']:
        title = d['feed']['title']

    description = u''
    if 'summary' in d['feed']:
        description = d['feed']['summary']

    subtitle = u''
    if 'subtitle' in d['feed']:
        subtitle = d['feed']['subtitle']

    slug = slugify(title)
    author_name = u"PLACEHOLDER NAME"
    author_email = u"PLACEHOLDER@email.com"

    podcast = Podcast()
    podcast.slug = get_available_slug(Podcast, slug, podcast)
    podcast.title = title
    podcast.subtitle = subtitle
    podcast.author = Author(author_name, author_email)
    podcast.description = description
    podcast.explicit = explicit

    DBSession.add(podcast)
    DBSession.flush()

    # Create thumbs from image, or default thumbs
    created_images = False
    if image:
        temp_imagefile = tempfile.TemporaryFile()
        imagefile = urllib2.urlopen(image)
        temp_imagefile.write(imagefile.read())
        temp_imagefile.seek(0)
        filename = urlparse.urlparse(image)[2]
        create_thumbs_for(podcast, temp_imagefile, filename)
        created_images = True

    if not created_images:
        create_default_thumbs_for(podcast)

    # Now add all of the entries
    for entry in d['entries']:
        media = media_from_entry(entry, tags, save_files)
        media.podcast = podcast

    return podcast

def media_from_entry(e, tags=False, save_files=False):
    # Get tags as a list of unicode objects.
    tags = [t['term'] for t in e['tags']]

    # Assume not explicit.
    explicit = 0
    if 'itunes_explicit' in e:
        explicit = e['itunes_explicit']

    # Find the duration, if it exists
    duration = u''
    if 'itunes_duration' in e:
        try:
            duration = e['itunes_duration']
            duration = duration_to_seconds(duration)
        except ValueError:
            duration = None

    # Find the first <img> tag in the summary, if there is one
    image = None
    m = img_regex.match(e['summary'])
    if m is not None:
        image = m.group(1)[1:-1]

    title = e['title']

    slug = slugify(title)
    author_name = u"PLACEHOLDER NAME"
    author_email = u"PLACEHOLDER@email.com"
    if 'author_detail' in e:
        if 'name' in e['author_detail']:
            author_name = e['author_detail']['name']
        if 'email' in e['author_detail']:
            author_email = e['author_detail']['email']
    year, month, day, hour, minute, second = e['updated_parsed'][:6]
    updated = datetime(year, month, day, hour, minute, second)

    media = Media()
    media.slug = get_available_slug(Media, slug, media)
    media.title = e['title']
    media.author = Author(author_name, author_email)
    media.description = e['summary']
    media.notes = u''
    if tags:
        media.set_tags(tags)
    else:
        media.set_categories(tags)
    media.publish_on = updated
    media.created_on = updated
    media.publishable = True
    media.reviewed = True
    media.duration = duration

    DBSession.add(media)
    DBSession.flush()

    # Create thumbs from image, or default thumbs
    created_images = False
    if image:
        temp_imagefile = tempfile.TemporaryFile()
        imagefile = urllib2.urlopen(image)
        temp_imagefile.write(imagefile.read())
        temp_imagefile.seek(0)
        filename = urlparse.urlparse(image)[2]
        create_thumbs_for(media, temp_imagefile, filename)
        created_images = True

    if not created_images:
        create_default_thumbs_for(media)

    print "Loaded episode:", media

    # now add all of the files.
    for enc in e['enclosures']:
        mf = media_file_from_enclosure(enc, media, save_files)
        print "Loaded media file:", mf

    media.update_status()

    return media

class DictWithPropertyAccessors(dict):
    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return super(DictObj,self).__getattr__(name)

def media_file_from_enclosure(enc, media, save_files=False):
    url = enc['href']
    length = enc.get('length', 'unknown')
    if save_files:
        print "About to download %s bytes from %s" % (length, url)
        temp_file = tempfile.TemporaryFile()
        file = urllib2.urlopen(url)
        temp_file.write(file.read())
        temp_file.seek(0)
        # Make a fake uploaded file object.
        uploaded_file = DictWithPropertyAccessors(file=temp_file, filename=url)
        media_file = add_new_media_file(media, uploaded_file, url)
        temp_file.close()
        file.close()
    else:
        media_file = add_new_media_file(media, None, url)

    if message:
        raise Exception(message)

    return media_file

def main(parser, options, args):
    if not options.uri:
        parser.print_help()
        sys.exit(1)

    d = feedparser.parse(options.uri)

    # FIXME: This script relies on the v0.8.2 models.
    #        It should be updated for v0.9.0
    print "I'm sorry, but this RSS import script is out of date."
    sys.exit(1)

    podcast = podcast_from_feed(d, tags=options.tags, save_files=options.save_files)
    DBSession.commit()
    print "Created podcast:", podcast
    print "Imported %d episodes." % len(podcast.media.all())

    sys.exit(0)

if __name__ == "__main__":
    main(cmd.parser, cmd.options, cmd.args)

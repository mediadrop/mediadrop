# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime
import logging

import gdata.youtube.service

from mediacore.lib.storage import (StorageError, YoutubeStorage, 
    add_new_media_file)
from mediacore.lib.thumbnails import create_default_thumbs_for, has_thumbs
from mediacore.lib.xhtml import clean_xhtml
from mediacore.model import (Author, Media, MediaFile, fetch_row, 
    get_available_slug)
from mediacore.model.meta import DBSession

log = logging.getLogger(__name__)


__all__ = ['YouTubeImporter']


class YouTubeImporter(object):
    def __init__(self, auto_publish, user, tags=None, categories=None):
        self.auto_publish = auto_publish
        self.user = user
        self.tags = tags
        if not isinstance(categories, list):
            categories = [categories]
        self.categories = categories
    
    def import_videos_from_channel(self, channel_name):
        # Since we can only get 50 videos at a time, loop through when a "next"
        # link is present in the returned feed from YouTube
        yt_service = gdata.youtube.service.YouTubeService()
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=50' \
            % (channel_name)
        while True:
            feed = yt_service.GetYouTubeVideoFeed(uri)
            self.import_videos_from_feed(feed)
            for link in feed.link:
                if link.rel == 'next':
                    uri = link.href
                    break
            else:
                break
    
    def import_videos_from_feed(self, feed):
        for entry in feed.entry:
            media = self._import_video(entry)
            if media:
                DBSession.add(media)
                DBSession.flush()
    
    # --- internal methods ----------------------------------------------------
    
    def _id_from_youtube_link(self, player_url):
        match = YoutubeStorage.url_pattern.match(player_url)
        if match is None:
            log.debug('Cannot parse YouTube URL: %s' % player_url)
            return None
        video_properties = match.groupdict()
        return video_properties.get('id')
    
    def _media_file_for(self, player_url):
        unique_id = self._id_from_youtube_link(player_url)
        if unique_id is None:
            return None
        return MediaFile.query.filter(MediaFile.unique_id==unique_id).first()
    
    def _has_media_file_for(self, player_url):
        return (self._media_file_for(player_url) is not None)
    
    def _import_video(self, entry):
        # Occasionally, there are issues with a video in a feed
        # not being available (region restrictions, etc)
        # If this happens, just move along.
        if not entry.media.player:
            log.debug('Video Feed Error: No player URL? %s' % entry)
            return None
        video_url = unicode(entry.media.player.url, "utf-8")
        if self._has_media_file_for(video_url):
            return None
        media = fetch_row(Media, u'new')
        media.author = Author(self.user.display_name, self.user.email_address)
        media.reviewed = True
        media.title = unicode(entry.media.title.text, "utf-8")
        if entry.media.description.text:
            encoded_description = unicode(entry.media.description.text,
                                        "utf-8")
            media.description = clean_xhtml(encoded_description)
        media.slug = get_available_slug(Media, media.title, media)
        
        if self.tags:
            media.set_tags(unicode(self.tags))
        if self.categories:
            media.set_categories(self.categories)
        try:
            media_file = add_new_media_file(media, url=video_url)
        except StorageError, e:
            log.debug('Video Feed Error: Error storing video: %s at %s' \
                % e.message, video_url)
            return None
        if not has_thumbs(media):
            create_default_thumbs_for(media)
        media.title = media_file.display_name
        media.update_status()
        if self.auto_publish:
            media.reviewed = 1
            media.encoded = 1
            media.publishable = 1
            media.created_on = datetime.now()
            media.modified_on = datetime.now()
            media.publish_on = datetime.now()
        return media


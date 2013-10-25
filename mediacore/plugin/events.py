# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Abstract events which plugins subscribe to and are called by the app.
"""
from collections import deque
import logging

from sqlalchemy.orm.interfaces import MapperExtension


__all__ = ['Event', 'GeneratorEvent', 'FetchFirstResultEvent', 'observes']

log = logging.getLogger(__name__)

class Event(object):
    """
    An arbitrary event that's triggered and observed by different parts of the app.

        >>> e = Event()
        >>> e.observers.append(lambda x: x)
        >>> e('x')
    """
    def __init__(self, args=()):
        self.args = args and tuple(args) or None
        self.pre_observers = deque()
        self.post_observers = deque()
    
    @property
    def observers(self):
        return tuple(self.pre_observers) + tuple(self.post_observers)

    def __call__(self, *args, **kwargs):
        # This is helpful for events which are triggered explicitly in the code
        # (e.g. Environment.loaded)
        for observer in self.observers:
            observer(*args, **kwargs)

    def __iter__(self):
        return iter(self.observers)

class GeneratorEvent(Event):
    """
    An arbitrary event that yields all results from all observers.
    """
    def is_list_like(self, value):
        if isinstance(value, basestring):
            return False
        try:
            iter(value)
        except TypeError:
            return False
        return True
    
    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            result = observer(*args, **kwargs)
            if self.is_list_like(result):
                for item in result:
                    yield item
            else:
                yield result


class FetchFirstResultEvent(Event):
    """
    An arbitrary event that return the first result from its observers
    """
    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            result = observer(*args, **kwargs)
            if result is not None:
                return result
        return None

class observes(object):
    """
    Register the decorated function as an observer of the given event.
    """
    def __init__(self, *events, **kwargs):
        self.events = events
        self.appendleft = kwargs.pop('appendleft', False)
        self.run_before = kwargs.pop('run_before', False)
        if kwargs:
            first_key = list(kwargs)[0]
            raise TypeError('TypeError: observes() got an unexpected keyword argument %r' % first_key)

    def __call__(self, func):
        for event in self.events:
            observers = event.post_observers
            if self.run_before:
                observers = event.pre_observers
            
            if self.appendleft:
                observers.appendleft(func)
            else:
                observers.append(func)
        return func

class MapperObserver(MapperExtension):
    """
    Fire events whenever the mapper triggers any kind of row modification.
    """
    def __init__(self, event_group):
        self.event_group = event_group

    def after_delete(self, mapper, connection, instance):
        self.event_group.after_delete(instance)

    def after_insert(self, mapper, connection, instance):
        self.event_group.after_insert(instance)

    def after_update(self, mapper, connection, instance):
        self.event_group.after_update(instance)

    def before_delete(self, mapper, connection, instance):
        self.event_group.before_delete(instance)

    def before_insert(self, mapper, connection, instance):
        self.event_group.before_insert(instance)

    def before_update(self, mapper, connection, instance):
        self.event_group.before_update(instance)

###############################################################################
# Application Setup

class Environment(object):
    before_route_setup = Event(['mapper'])
    after_route_setup = Event(['mapper'])
    # TODO: deprecation warning
    routes = after_route_setup
    
    routes = Event(['mapper'])
    init_model = Event([])
    loaded = Event(['config'])
    
    # fires when a new database was initialized (tables created)
    database_initialized = Event([])
    
    # an existing database was migrated to a newer DB schema
    database_migrated = Event([])
    
    # the environment has been loaded, the database is ready to use
    database_ready = Event([])

###############################################################################
# Controllers

class Admin(object):

    class CategoriesController(object):
        index = Event(['**kwargs'])
        bulk = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])

    class CommentsController(object):
        index = Event(['**kwargs'])
        save_status = Event(['**kwargs'])
        save_edit = Event(['**kwargs'])

    class IndexController(object):
        index = Event(['**kwargs'])
        media_table = Event(['**kwargs'])

    class MediaController(object):
        bulk = Event(['type=None, ids=None, **kwargs'])
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        add_file = Event(['**kwargs'])
        edit_file = Event(['**kwargs'])
        merge_stubs = Event(['**kwargs'])
        save_thumb = Event(['**kwargs'])
        update_status = Event(['**kwargs'])

    class PodcastsController(object):
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        save_thumb = Event(['**kwargs'])

    class TagsController(object):
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        bulk = Event(['**kwargs'])

    class UsersController(object):
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        delete = Event(['**kwargs'])

    class GroupsController(object):
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        delete = Event(['**kwargs'])
    
    class Players(object):
        HTML5OrFlashPrefsForm = Event(['form'])
        SublimePlayerPrefsForm = Event(['form'])
        YoutubeFlashPlayerPrefsForm = Event(['form'])
    
    class PlayersController(object):
        delete = Event(['**kwargs'])
        disable = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        enable = Event(['**kwargs'])
        index = Event(['**kwargs'])
        reorder = Event(['**kwargs'])
    
    class Settings(object):
        AdvertisingForm = Event(['form'])
        AnalyticsForm = Event(['form'])
        APIForm = Event(['form'])
        AppearanceForm = Event(['form'])
        CommentsForm = Event(['form'])
        GeneralForm = Event(['form'])
        NotificationsForm = Event(['form'])
        PopularityForm = Event(['form'])
        SiteMapsForm = Event(['form'])
        UploadForm = Event(['form'])
    
    class SettingsController(object):
        advertising_save = Event(['**kwargs'])
        analytics_save = Event(['**kwargs'])
        appearance_save = Event(['**kwargs'])
        comments_save = Event(['**kwargs'])
        general_save = Event(['**kwargs'])
        notifications_save = Event(['**kwargs'])
        popularity_save = Event(['**kwargs'])
        # probably this event will be renamed to 'api_save' in a future version
        save_api = Event(['**kwargs'])
        sitemaps_save = Event(['**kwargs'])
        upload_save = Event(['**kwargs'])
    
    class Storage(object):
        LocalFileStorageForm = Event(['form'])
        FTPStorageForm = Event(['form'])
        RemoteURLStorageForm = Event(['form'])
    
    class StorageController(object):
        delete = Event(['**kwargs'])
        disable = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        enable = Event(['**kwargs'])
        index = Event(['**kwargs'])


class API(object):
    class MediaController(object):
        index = Event(['**kwargs'])
        get = Event(['**kwargs'])

class CategoriesController(object):
    index = Event(['**kwargs'])
    more = Event(['**kwargs'])
    # feed observers (if they are not marked as "run_before=True") must support
    # pure string output (from beaker cache) instead of a dict with template
    # variables.
    feed = Event(['limit', '**kwargs'])

class ErrorController(object):
    document = Event(['**kwargs'])
    report = Event(['**kwargs'])

class LoginController(object):
    login = Event(['**kwargs'])
    login_handler = Event(['**kwargs'])
    logout_handler = Event(['**kwargs'])
    post_login = Event(['**kwargs'])
    post_logout = Event(['**kwargs'])

class MediaController(object):
    index = Event(['**kwargs'])
    comment = Event(['**kwargs'])
    explore = Event(['**kwargs'])
    embed_player = Event(['xhtml'])
    jwplayer_rtmp_mrss = Event(['**kwargs'])
    rate = Event(['**kwargs'])
    view = Event(['**kwargs'])

class PodcastsController(object):
    index = Event(['**kwargs'])
    view = Event(['**kwargs'])
    feed = Event(['**kwargs'])

class SitemapsController(object):
    # observers (if they are not marked as "run_before=True") must support pure 
    # string output (from beaker cache) instead of a dict with template variables.
    google = Event(['page', 'limit', '**kwargs'])
    mrss = Event(['**kwargs'])
    latest = Event(['limit', 'skip', '**kwargs'])
    featured = Event(['limit', 'skip', '**kwargs'])

class UploadController(object):
    index = Event(['**kwargs'])
    submit = Event(['**kwargs'])
    submit_async = Event(['**kwargs'])
    success = Event(['**kwargs'])
    failure = Event(['**kwargs'])

###############################################################################
# Models

class Media(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])
    
    # event is triggered when the encoding status changes from 'not encoded' to
    # 'encoded'
    encoding_done = Event(['instance'])

class MediaFile(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class Podcast(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class Comment(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class Category(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class Tag(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class Setting(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class MultiSetting(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

class User(object):
    before_delete = Event(['instance'])
    after_delete = Event(['instance'])
    before_insert = Event(['instance'])
    after_insert = Event(['instance'])
    before_update = Event(['instance'])
    after_update = Event(['instance'])

###############################################################################
# Forms

PostCommentForm = Event(['form'])
UploadForm = Event(['form'])
LoginForm = Event(['form'])
Admin.CategoryForm = Event(['form'])
Admin.CategoryRowForm = Event(['form'])
Admin.EditCommentForm = Event(['form'])
Admin.MediaForm = Event(['form'])
Admin.AddFileForm = Event(['form'])
Admin.EditFileForm = Event(['form'])
Admin.UpdateStatusForm = Event(['form'])
Admin.SearchForm = Event(['form'])
Admin.PodcastForm = Event(['form'])
Admin.PodcastFilterForm = Event(['form'])
Admin.UserForm = Event(['form'])
Admin.GroupForm = Event(['form'])
Admin.TagForm = Event(['form'])
Admin.TagRowForm = Event(['form'])
Admin.ThumbForm = Event(['form'])

###############################################################################
# Miscellaneous... may require refactoring

media_types = GeneratorEvent([])
plugin_settings_links = GeneratorEvent([])
EncodeMediaFile = Event(['media_file'])
page_title = FetchFirstResultEvent('default=None, category=None, \
    media=None, podcast=None, upload=None, **kwargs')
meta_keywords = FetchFirstResultEvent('category=None, media=None, \
    podcast=None, upload=None, **kwargs')
meta_description = FetchFirstResultEvent('category=None, media=None, \
    podcast=None, upload=None, **kwargs')
meta_robots_noindex = FetchFirstResultEvent('categories=None, rss=None, **kwargs')

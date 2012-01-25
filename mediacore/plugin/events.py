# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
"""
Abstract events which plugins subscribe to and are called by the app.
"""
from collections import deque
import logging

from sqlalchemy.orm.interfaces import MapperExtension

log = logging.getLogger(__name__)

class Event(object):
    """
    An arbitrary event that's triggered and observed by different parts of the app.

        >>> e = Event()
        >>> e.observers.append(lambda x: x)
        >>> e('x')

    """
    def __init__(self, args):
        self.args = args and tuple(args) or None
        self.observers = deque()

    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            observer(*args, **kwargs)

    def __iter__(self):
        return iter(self.observers)

class GeneratorEvent(Event):
    """
    An arbitrary event that yields all results from all observers.
    """
    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            for result in observer(*args, **kwargs):
                yield result

class FetchFirstResultEvent(Event):
    """
    An arbitrary event that return the first result from its observers
    """
    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            result = observer(**kwargs)
            if result is not None:
                return result
        return None

class observes(object):
    """
    Register the decorated function as an observer of the given event.
    """
    def __init__(self, *events, **kwargs):
        self.events = events
        self.appendleft = kwargs.get('appendleft', False)

    def __call__(self, func):
        for event in self.events:
            if self.appendleft:
                event.observers.appendleft(func)
            else:
                event.observers.append(func)
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
    routes = Event(['mapper'])
    init_model = Event([])
    loaded = Event(['config'])

###############################################################################
# Controllers

class Admin(object):

    class CategoriesController(object):
        index = Event(['**kwargs'])
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

    class UsersController(object):
        index = Event(['**kwargs'])
        edit = Event(['**kwargs'])
        save = Event(['**kwargs'])
        delete = Event(['**kwargs'])

class API(object):
    class MediaController(object):
        index = Event(['**kwargs'])
        get = Event(['**kwargs'])

class CategoriesController(object):
    index = Event(['**kwargs'])
    more = Event(['**kwargs'])

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

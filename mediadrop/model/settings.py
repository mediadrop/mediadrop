# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Settings Model

A very rudimentary settings implementation which is intended to store our
non-mission-critical options which can be edited via the admin UI.

.. todo:

    Rather than fetch one option at a time, load all settings into an object
    with attribute-style access.

"""
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.types import Unicode, UnicodeText, Integer, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates
from urlparse import urlparse

from mediadrop.model.meta import DBSession, metadata
from mediadrop.plugin import events

settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

multisettings = Table('settings_multi', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False),
    Column('value', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

class Setting(object):
    """
    A Single Setting
    """
    query = DBSession.query_property()

    def __init__(self, key=None, value=None):
        self.key = key or None
        self.value = value or None

    def __repr__(self):
        return '<Setting: %s = %r>' % (self.key, self.value)

    def __unicode__(self):
        return self.value

class MultiSetting(object):
    """
    A MultiSetting
    """
    query = DBSession.query_property()

    def __init__(self, key=None, value=None):
        self.key = key or None
        self.value = value or None

    def __repr__(self):
        return '<MultiSetting: %s = %r>' % (self.key, self.value)

    def __unicode__(self):
        return self.value

mapper(Setting, settings, extension=events.MapperObserver(events.Setting))
mapper(MultiSetting, multisettings, extension=events.MapperObserver(events.MultiSetting))

def insert_settings(defaults):
    """Insert the given setting if they don't exist yet.

    XXX: Does not include any support for MultiSetting. This approach
         won't work for that. We'll need to use a migration script.

    :type defaults: list
    :param defaults: Key and value pairs
    :rtype: list
    :returns: Any settings that have just been created.
    """
    inserted = []
    try:
        settings_query = DBSession.query(Setting.key)\
            .filter(Setting.key.in_([key for key, value in defaults]))
        existing_settings = set(x[0] for x in settings_query)
    except ProgrammingError:
        # If we are running paster setup-app on a fresh database with a
        # plugin which tries to use this function every time the
        # Environment.loaded event fires, the settings table will not
        # exist and this exception will be thrown, but its safe to ignore.
        # The settings will be created the next time the event fires,
        # which will likely be the first time the app server starts up.
        return inserted
    for key, value in defaults:
        if key in existing_settings:
            continue
        transaction = DBSession.begin_nested()
        try:
            s = Setting(key, value)
            DBSession.add(s)
            transaction.commit()
            inserted.append(s)
        except IntegrityError:
            transaction.rollback()
    if inserted:
        DBSession.commit()
    return inserted

def fetch_and_create_multi_setting(key, value):
    multisettings = MultiSetting.query\
        .filter(MultiSetting.key==key)\
        .all()
    for ms in multisettings:
        if ms.value == value:
            return ms
    ms = MultiSetting(key, value)
    DBSession.add(ms)
    return ms

# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Settings Model

A very rudimentary settings implementation which is intended to store our
non-mission-critical options which can be edited via the admin UI.

.. todo:

    Rather than fetch one option at a time, load all settings into an object
    with attribute-style access.

"""
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, UnicodeText, Integer, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates
from urlparse import urlparse

from mediacore.model.meta import DBSession, metadata
from mediacore.plugin import events

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
        return '<Setting: %s = %s>' % (self.key, self.value)

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
        return '<MultiSetting: %s = %s>' % (self.key, self.value)

    def __unicode__(self):
        return self.value

mapper(Setting, settings, extension=events.MapperObserver(events.Setting))
mapper(MultiSetting, multisettings, extension=events.MapperObserver(events.MultiSetting))

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

from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates

from mediacore.model import DeclarativeBase, metadata, DBSession, slugify, _mtm_count_property


topics = Table('topics', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Topic(object):
    """Topic definition
    """
    def __init__(self, name=None, slug=None):
        self.name = name or None
        self.slug = slug or name or None

    def __repr__(self):
        return '<Topic: %s>' % self.name

    def __unicode__(self):
        return self.name

    @validates('slug')
    def validate_slug(self, key, slug):
        return slugify(slug)

class TopicList(list):
    def __unicode__(self):
        return ', '.join([topic.name for topic in self.values()])

mapper(Topic, topics)

def fetch_topics(topic_ids):
    topics = DBSession.query(Topic).filter(Topic.id.in_(topic_ids)).all()
    return topics

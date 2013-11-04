# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Comment Model

Comments come with two status flags:

    * reviewed
    * publishable

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, column_property, validates, interfaces, Query

from mediadrop.model import AuthorWithIP
from mediadrop.model.meta import DBSession, metadata
from mediadrop.plugin import events


comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('subject', Unicode(100)),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('reviewed', Boolean, default=False, nullable=False),
    Column('publishable', Boolean, default=False, nullable=False),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255)),
    Column('author_ip', BigInteger, nullable=False),
    Column('body', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

class CommentQuery(Query):
    def published(self, flag=True):
        return self.filter(Comment.publishable == flag)

    def reviewed(self, flag=True):
        return self.filter(Comment.reviewed == flag)

    def trash(self, flag=True):
        filter = sql.and_(Comment.reviewed == True,
                          Comment.publishable == False)
        if flag:
            return self.filter(filter)
        else:
            return self.filter(sql.not_(filter))

    def search(self, q):
        q = '%' + q + '%'
        return self.filter(sql.or_(
            Comment.subject.like(q),
            Comment.body.like(q),
        ))


class Comment(object):
    """Comment Model

    .. attribute:: type

        The relation name to use when looking up the parent object of this Comment.
        This is the name of the backref property which can be used to find the
        object that this Comment belongs to. Our convention is to have a controller
        by this name, with a 'view' action which accepts a slug, so we can
        auto-generate links to any comment's parent.

    .. attribute:: author

        An instance of :class:`mediadrop.model.author.AuthorWithIP`.

    """

    query = DBSession.query_property(CommentQuery)

    def __repr__(self):
        return '<Comment: %r subject=%r>' % (self.id, self.subject)

    def __unicode__(self):
        return self.subject

    @property
    def type(self):
        if self.media_id:
            return 'media'
        return None

    def _get_parent(self):
        return self.media or None
    def _set_parent(self, parent):
        self.media = parent
    parent = property(_get_parent, _set_parent, None, """
        The object this Comment belongs to, provided for convenience mostly.
        If the parent has not been eagerloaded, a query is executed automatically.
    """)


mapper(Comment, comments, order_by=comments.c.created_on, extension=events.MapperObserver(events.Comment), properties={
    'author': composite(AuthorWithIP,
        comments.c.author_name,
        comments.c.author_email,
        comments.c.author_ip),
})

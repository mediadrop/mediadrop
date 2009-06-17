"""
Podcast/Media Admin Controller
"""
from repoze.what.predicates import has_permission
from tg import request
from tg.decorators import paginate
from sqlalchemy import or_
from sqlalchemy.orm import undefer

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, Podcast, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm

class PodcastadminController(RoutingController):
    """Admin podcast actions which deal with groups of podcasts"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.podcasts.index', 'mediaplex.templates.admin.podcasts.index-table')
    @paginate('podcasts', items_per_page=10)
    def index(self, page=1, search=None, podcast=None, **kw):
        podcasts = DBSession.query(Podcast).\
            order_by(Podcast.title)

        return dict(podcasts=podcasts)

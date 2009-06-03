"""
Podcast/Media Admin Controller
"""
from repoze.what.predicates import has_permission
from tg.decorators import paginate
from sqlalchemy import or_
from sqlalchemy.orm import undefer

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, Audio, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm

class PodcastadminController(RoutingController):
    """Admin podcast actions which deal with groups of podcasts"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.podcasts.index', 'mediaplex.templates.admin.podcasts.index-table')
    @paginate('audio', items_per_page=25)
    def index(self, page=1, search=None, **kw):
        audio = DBSession.query(Audio)\
            .options(undefer('comment_count'))\
            .order_by(Audio.status.desc(), Audio.created_on)
        if search is not None:
            like_search = '%%%s%%' % search
            audio = audio.filter(or_(
                Audio.title.like(like_search),
                Audio.description.like(like_search),
                Audio.notes.like(like_search),
                Audio.tags.any(Tag.name.like(like_search)),
            ))
        return dict(
            audio=audio,
            search=search,
            search_form=SearchForm(action=helpers.url_for()),
        )



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
from mediaplex.model import DBSession, Podcast, PodcastEpisode, Audio, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm

class PodcastadminController(RoutingController):
    """Admin podcast actions which deal with groups of podcasts"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.podcasts.index', 'mediaplex.templates.admin.audio.index-table')
    @paginate('audio', items_per_page=25)
    def index(self, page=1, search=None, podcast_filter=None, **kw):
        audio = DBSession.query(Audio).\
            filter(Audio.status.excludes('trash')).\
            options(undefer('comment_count')).\
            order_by(Audio.status.desc(), Audio.created_on)
        if search is not None:
            like_search = '%%%s%%' % search
            audio = audio.filter(or_(
                Audio.title.like(like_search),
                Audio.description.like(like_search),
                Audio.notes.like(like_search),
                Audio.tags.any(Tag.name.like(like_search)),
            ))

        podcast_filter_title = None

        if podcast_filter == 'Unfiled':
            audio = audio.filter(~Audio.episode.any())
        elif podcast_filter is not None:
            audio = audio.filter(Audio.episode.any(PodcastEpisode.podcast.has(Podcast.id == podcast_filter)))
            podcast_filter_title = DBSession.query(Podcast.title).get(podcast_filter)

        if request.is_xhr:
            """ShowMore Ajax Fetch Action"""
            return dict(audio=audio)
        else:
            podcasts = DBSession.query(Podcast).\
                order_by(Podcast.title)

            unfiled_count = DBSession.query(Audio).\
                filter(Audio.status.excludes('trash')).\
                filter(~Audio.episode.any()).count()


            return dict(
                podcasts=podcasts,
                podcast_filter=podcast_filter,
                podcast_filter_title=podcast_filter_title,
                show_unfiled=unfiled_count != 0,
                audio=audio,
                search=search,
                search_form=SearchForm(action=helpers.url_for()))

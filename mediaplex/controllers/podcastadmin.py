"""
Podcast/Media Admin Controller
"""
from repoze.what.predicates import has_permission
from tg import request
from tg.decorators import paginate, expose, validate, require
from sqlalchemy import or_
from sqlalchemy.orm import undefer
from pylons import tmpl_context

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, Podcast, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm, AlbumArtForm
from mediaplex.forms.podcasts import PodcastForm

class PodcastadminController(RoutingController):
    """Admin podcast actions which deal with groups of podcasts"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.podcasts.index', 'mediaplex.templates.admin.podcasts.index-table')
    @paginate('podcasts', items_per_page=10)
    def index(self, page=1, search=None, podcast=None, **kw):
        podcasts = DBSession.query(Podcast).\
            options(undefer('media_count')).\
            order_by(Podcast.title)

        return dict(podcasts=podcasts)

    @expose('mediaplex.templates.admin.podcasts.edit')
    def edit(self, id, **values):
        podcast = self._fetch_podcast(id)
        form = PodcastForm(action=helpers.url_for(action='save', id=podcast.id), podcast=podcast)
        explicit = 'Not specified'
        if podcast.explicit is not None:
            explicit = podcast.explicit and 'Explicit' or 'Clean'

        form_values = {
            'slug': podcast.slug,
            'title': podcast.title,
            'subtitle': podcast.subtitle,
            'author_name': podcast.author.name,
            'author_email': podcast.author.email,
            'description': podcast.description,
            'details': {
                'category': podcast.category,
                'explicit': explicit,
                'copyright': podcast.copyright
            },
        }

        album_art_form_errors = {}
        if tmpl_context.action == 'save_album_art':
            album_art_form_errors = tmpl_context.form_errors

        form_values.update(values)
        return {
            'podcast': podcast,
            'form': form,
            'form_values': form_values,
            'album_art_form_errors': album_art_form_errors,
            'album_art_form': AlbumArtForm(action=helpers.url_for(action='save_album_art', id=podcast.id)),
        }

    def _fetch_podcast(self, id):
        if id == 'new':
            podcast = Podcast()
            podcast.id = 'new'
        else:
            podcast = DBSession.query(Podcast).get(id)
        return podcast

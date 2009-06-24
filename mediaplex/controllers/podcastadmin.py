"""
Podcast/Media Admin Controller
"""
from repoze.what.predicates import has_permission
from tg import config, flash, url, request
from tg.decorators import paginate, expose, validate, require
from sqlalchemy import or_
from sqlalchemy.orm import undefer
from pylons import tmpl_context

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr, redirect, url_for
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, fetch_row, Podcast, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm, AlbumArtForm
from mediaplex.forms.podcasts import PodcastForm


class PodcastadminController(RoutingController):
    """Admin podcast actions which deal with groups of podcasts"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.podcasts.index',
                'mediaplex.templates.admin.podcasts.index-table')
    @paginate('podcasts', items_per_page=10)
    def index(self, page=1, search=None, podcast=None, **kw):
        podcasts = DBSession.query(Podcast)\
            .options(undefer('media_count'))\
            .order_by(Podcast.title)
        return dict(podcasts=podcasts)


    @expose('mediaplex.templates.admin.podcasts.edit')
    def edit(self, id, **values):
        podcast = fetch_row(Podcast, id)
        form = PodcastForm(action=url_for(action='save'), podcast=podcast)

        explicit = 'Not specified'
        if podcast.explicit is not None:
            explicit = podcast.explicit and 'Explicit' or 'Clean'

        form_values = {
            'slug': podcast.slug,
            'title': podcast.title,
            'subtitle': podcast.subtitle,
            'author_name': podcast.author and podcast.author.name or None,
            'author_email': podcast.author and podcast.author.email or None,
            'description': podcast.description,
            'details': {
                'category': podcast.category,
                'explicit': explicit,
                'copyright': podcast.copyright
            },
        }
        form_values.update(values)

        album_art_form_errors = {}
        if tmpl_context.action == 'save_album_art':
            album_art_form_errors = tmpl_context.form_errors

        return dict(
            podcast = podcast,
            form = form,
            form_values = form_values,
            album_art_form_errors = album_art_form_errors,
            album_art_form = AlbumArtForm(action=url_for(action='save_album_art')),
        )


    @expose()
    @validate(PodcastForm(), error_handler=edit)
    def save(self, id, **values):
        podcast = fetch_row(Podcast, id)

        if podcast.id == 'new':
            podcast.id = None
        elif values.has_key('delete'):
            podcast.delete()
            DBSession.add(podcast)
            DBSession.flush()
            redirect(action='index')

        podcast.slug = values['slug']
        podcast.title = values['title']
        podcast.subtitle = values['subtitle']
        podcast.author = Author(values['author_name'], values['author_email'])
        podcast.description = values['description']
        podcast.copyright = values['details']['copyright']
        podcast.category = values['details']['category']
        if values['details']['explicit'] == 'Not specified':
            podcast.explicit = None
        else:
            podcast.explicit = values['details']['explicit'] == 'Explicit'

        DBSession.add(podcast)
        DBSession.flush()
        redirect(action='edit', id=podcast.id)


    @expose()
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, id, **values):
        podcast = fetch_row(Podcast, id)
        temp_file = values['album_art'].file
        im_path = '%s/../public/images/podcasts/%d%%s.jpg' % (os.path.dirname(__file__), podcast.id)
        im = Image.open(temp_file)
        im.resize((154, 151), 1).save(im_path % 'm')
        redirect(action='edit')

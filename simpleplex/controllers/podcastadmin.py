"""
Podcast Admin Controller
"""
import os
from shutil import copyfileobj
from PIL import Image
from repoze.what.predicates import has_permission
from tg import config, request
from tg.decorators import expose, validate, require
from sqlalchemy import or_
from sqlalchemy.orm import undefer
from pylons import tmpl_context

from simpleplex.lib import helpers
from simpleplex.lib.helpers import expose_xhr, redirect, paginate, url_for, clean_xhtml
from simpleplex.lib.base import RoutingController
from simpleplex.model import DBSession, fetch_row, Podcast, Author, AuthorWithIP, get_available_slug
from simpleplex.forms.admin import SearchForm, AlbumArtForm
from simpleplex.forms.podcasts import PodcastForm

podcast_form = PodcastForm()
album_art_form = AlbumArtForm()


class PodcastadminController(RoutingController):
    allow_only = has_permission('admin')

    @expose_xhr('simpleplex.templates.admin.podcasts.index',
                'simpleplex.templates.admin.podcasts.index-table')
    @paginate('podcasts', items_per_page=10)
    def index(self, page=1, **kw):
        """List podcasts with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            podcasts
                The list of :class:`~simpleplex.model.podcasts.Podcast`
                instances for this page.
        """
        podcasts = DBSession.query(Podcast)\
            .options(undefer('media_count'))\
            .order_by(Podcast.title)
        return dict(podcasts=podcasts)


    @expose('simpleplex.templates.admin.podcasts.edit')
    def edit(self, id, **values):
        """Display the podcast forms for editing or adding.

        This page serves as the error_handler for every kind of edit action,
        if anything goes wrong with them they'll be redirected here.

        :param id: Podcast ID
        :type id: ``int`` or ``"new"``
        :param \*\*kwargs: Extra args populate the form for ``"new"`` podcasts
        :returns:
            podcast
                :class:`~simpleplex.model.podcasts.Podcast` instance
            form
                :class:`~simpleplex.forms.podcasts.PodcastForm` instance
            form_action
                ``str`` form submit url
            form_values
                ``dict`` form values
            album_art_form
                :class:`~simpleplex.forms.podcasts.AlbumArtForm` instance
            album_art_action
                ``str`` form submit url

        """
        podcast = fetch_row(Podcast, id)

        explicit_values = dict(yes=True, clean=False)
        form_values = dict(
            slug = podcast.slug,
            title = podcast.title,
            subtitle = podcast.subtitle,
            author_name = podcast.author and podcast.author.name or None,
            author_email = podcast.author and podcast.author.email or None,
            description = podcast.description,
            details = dict(
                explicit = {True: 'yes', False: 'clean'}.get(podcast.explicit, 'no'),
                category = podcast.category,
                copyright = podcast.copyright,
                itunes_url = podcast.itunes_url,
                feedburner_url = podcast.feedburner_url,
            ),
        )
        form_values.update(values)

        album_art_form_errors = {}
        if tmpl_context.action == 'save_album_art':
            album_art_form_errors = tmpl_context.form_errors

        return dict(
            podcast = podcast,
            form = podcast_form,
            form_action = url_for(action='save'),
            form_values = form_values,
            album_art_form = album_art_form,
            album_art_action = url_for(action='save_album_art'),
            album_art_form_errors = album_art_form_errors,
        )


    @expose()
    @validate(podcast_form, error_handler=edit)
    def save(self, id, slug, title, subtitle, author_name, author_email,
             description, details, delete=None, **kwargs):
        """Save changes or create a new :class:`~simpleplex.model.podcasts.Podcast` instance.

        Form handler the :meth:`edit` action and the
        :class:`~simpleplex.forms.podcasts.PodcastForm`.

        Redirects back to :meth:`edit` after successful editing
        and :meth:`index` after successful deletion.

        """
        podcast = fetch_row(Podcast, id)

        if delete:
            DBSession.delete(podcast)
            DBSession.flush()
            redirect(action='index', id=None)

        podcast.slug = get_available_slug(Podcast, slug, podcast)
        podcast.title = title
        podcast.subtitle = subtitle
        podcast.author = Author(author_name, author_email)
        podcast.description = clean_xhtml(description)
        podcast.copyright = details['copyright']
        podcast.category = details['category']
        podcast.itunes_url = details['itunes_url']
        podcast.feedburner_url = details['feedburner_url']
        podcast.explicit = {'yes': True, 'clean': False}.get(details['explicit'], None)

        DBSession.add(podcast)
        DBSession.flush()
        redirect(action='edit', id=podcast.id)


    @expose('json')
    @validate(album_art_form, error_handler=edit)
    def save_album_art(self, id, album_art, **values):
        """Save album art uploaded with :class:`~simpleplex.forms.media.AlbumArtForm`.

        :param id: Media ID. If ``"new"`` a new Media stub is created with
            :func:`~simpleplex.model.media.create_podcast_stub`.
        :type id: ``int`` or ``"new"``
        :param file: The uploaded file
        :type file: :class:`cgi.FieldStorage` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool
            message
                Error message, if unsuccessful
            id
                The :attr:`~simpleplex.model.podcasts.Podcast.id` which is
                important if a new podcast has just been created.

        """
        if id == 'new':
            podcast = create_podcast_stub()
        else:
            podcast = fetch_row(Podcast, id)

        temp_file = album_art.file
        im_path = os.path.join(config.image_dir, 'podcasts/%d%%(size)s.%%(ext)s' % podcast.id)

        try:
            # Create jpeg thumbnails
            im = Image.open(temp_file)
            im.resize((132, 132), 1).save(im_path % dict(size='s', ext='jpg'))
            im.resize((154, 154), 1).save(im_path % dict(size='m', ext='jpg'))
            im.resize((600, 600), 1).save(im_path % dict(size='l', ext='jpg'))

            # Backup the original image just for kicks
            orig_type = os.path.splitext(album_art.filename)[1].lower()[1:]
            orig_file = open(im_path % dict(size='orig', ext=orig_type), 'w')
            copyfileobj(temp_file, orig_file)
            temp_file.close()
            orig_file.close()

            success = True
            message = None
        except IOError, e:
            success = False
            message = 'Unsupported image type'
        except Exception, e:
            success = False
            message = e.message

        return dict(
            success = success,
            message = message,
            id = podcast.id,
        )

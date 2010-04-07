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

from tg import config, request, response, tmpl_context
from sqlalchemy import orm, sql
from repoze.what.predicates import has_permission

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib import helpers
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Tag)
from mediacore.forms.admin.tags import TagForm, TagRowForm


tag_form = TagForm()
tag_row_form = TagRowForm()

class TagsController(BaseController):
    allow_only = has_permission('admin')

    @expose('mediacore.templates.admin.tags.index')
    @paginate('tags', items_per_page=25)
    def index(self, page=1, **kwargs):
        """List tags with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            tags
                The list of :class:`~mediacore.model.tags.Tag`
                instances for this page.
            tag_form
                The :class:`~mediacore.forms.admin.settings.tags.TagForm` instance.

        """
        tags = DBSession.query(Tag)\
            .options(orm.undefer('media_count'))\
            .order_by(Tag.name)

        return dict(
            tags = tags,
            tag_form = tag_form,
            tag_row_form = tag_row_form,
        )

    @expose('mediacore.templates.admin.tags.edit')
    def edit(self, id, **kwargs):
        """Edit a single tag.

        :param id: Tag ID
        :rtype: Dict
        :returns:
            tags
                The list of :class:`~mediacore.model.tags.Tag`
                instances for this page.
            tag_form
                The :class:`~mediacore.forms.admin.settings.tags.TagForm` instance.

        """
        tag = fetch_row(Tag, id)

        return dict(
            tag = tag,
            tag_form = tag_form,
        )

    @expose('json')
    @validate(tag_form)
    def save(self, id, delete=False, **kwargs):
        """Save changes or create a tag.

        See :class:`~mediacore.forms.admin.settings.tags.TagForm` for POST vars.

        :param id: Tag ID
        :rtype: JSON dict
        :returns:
            success
                bool

        """
        if tmpl_context.form_errors:
            if request.is_xhr:
                return dict(success=False, errors=tmpl_context.form_errors)
            else:
                # TODO: Add error reporting for users with JS disabled?
                return redirect(action='edit')

        tag = fetch_row(Tag, id)

        if delete:
            DBSession.delete(tag)
            data = dict(success=True, id=tag.id)
        else:
            tag.name = kwargs['name']
            tag.slug = get_available_slug(Tag, kwargs['slug'], tag)
            DBSession.add(tag)
            DBSession.flush()
            data = dict(
                success = True,
                id = tag.id,
                name = tag.name,
                slug = tag.slug,
                row = unicode(tag_row_form.display(tag=tag)),
            )

        if request.is_xhr:
            return data
        else:
            redirect(action='index', id=None)

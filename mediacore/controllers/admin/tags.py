# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, tmpl_context
from sqlalchemy import orm

from mediacore.forms.admin.tags import TagForm, TagRowForm
from mediacore.lib.auth import has_permission
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (autocommit, expose, observable, paginate, 
    validate)
from mediacore.lib.helpers import redirect
from mediacore.model import Tag, fetch_row, get_available_slug
from mediacore.model.meta import DBSession
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

tag_form = TagForm()
tag_row_form = TagRowForm()

class TagsController(BaseController):
    allow_only = has_permission('edit')

    @expose('admin/tags/index.html')
    @paginate('tags', items_per_page=25)
    @observable(events.Admin.TagsController.index)
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

    @expose('admin/tags/edit.html')
    @observable(events.Admin.TagsController.edit)
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

    @expose('json', request_method='POST')
    @validate(tag_form)
    @autocommit
    @observable(events.Admin.TagsController.save)
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

    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.TagsController.bulk)
    def bulk(self, type=None, ids=None, **kwargs):
        """Perform bulk operations on media items

        :param type: The type of bulk action to perform (delete)
        :param ids: A list of IDs.

        """
        if not ids:
            ids = []
        elif not isinstance(ids, list):
            ids = [ids]

        success = True

        if type == 'delete':
            Tag.query.filter(Tag.id.in_(ids)).delete(False)
        else:
            success = False

        return dict(
            success = success,
            ids = ids,
        )

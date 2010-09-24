# This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
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

import logging

from pylons import request, response, session, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, observable, paginate, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.storage import StorageEngine
from mediacore.model import DBSession, fetch_row
from mediacore.plugin import events

log = logging.getLogger(__name__)

class StorageController(BaseController):
    """Admin user actions"""
    allow_only = has_permission('admin')

    @expose('admin/storage/index.html')
    @paginate('engines', items_per_page=50)
    def index(self, page=1, **kwargs):
        """List storage engines with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            users
                The list of :class:`~mediacore.model.auth.User`
                instances for this page.

        """
        engines = DBSession.query(StorageEngine)\
            .options(orm.undefer('file_count'),
                     orm.undefer('file_size_sum'))\
            .all()
        existing_engine_types = set(ecls.engine_type for ecls in engines)
        addable_engines = [
            ecls
            for ecls in StorageEngine
            if not ecls.is_singleton or ecls.engine_type not in existing_engine_types
        ]
        return {
            'engines': engines,
            'addable_engines': addable_engines,
        }

    @expose('admin/storage/edit.html')
    def edit(self, id, engine_type=None, **kwargs):
        """Display the :class:`~mediacore.lib.storage.StorageEngine` for editing or adding.

        :param id: Storage ID
        :type id: ``int`` or ``"new"``
        :rtype: dict
        :returns:

        """
        if id != 'new':
            engine = fetch_row(StorageEngine, id)
        else:
            types = dict((cls.engine_type, cls) for cls in StorageEngine)
            engine_cls = types.get(engine_type, None)
            if not engine_cls:
                redirect(controller='/admin/storage', action='index')
            engine = engine_cls()

        form = engine.settings_form
        form_values = {'general': {'display_name': engine.display_name}}
        form_values.update(kwargs)

        return {
            'engine': engine,
            'form': form,
            'form_action': url_for(action='save', engine_type=engine_type),
            'form_values': form_values,
        }

    @expose()
    def save(self, id, **kwargs):
        engine = fetch_row(StorageEngine, id)
        form = engine.settings_form

        @validate(form, error_handler=self.edit)
        def save_engine_params(id, general, **kwargs):
            # Save the values from fields that are shared by all engine forms.
            engine.display_name = general['display_name']

            # Save form specifics using the custom save handler on the
            # engine's form class, or use a default handler that just
            # tries to map field names to predefined _data attributes.
            save_func = getattr(form, 'save_engine_params', None)
            if save_func and getattr(save_func, '_isabstract', False):
                save_func = _default_save_handler
            log.debug('found save func: %r', save_func)
            save_func(engine, **tmpl_context.form_values)

            redirect(controller='/admin/storage', action='index')

        return save_engine_params(id, **kwargs)

    @expose('json')
    def delete(self, id, **kwargs):
        """Delete a user.

        :param id: User ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """

def _default_save_handler(engine, **kwargs):
    for key, value in kwargs.iteritems():
        if key in engine._default_data:
            engine._data[key] = value

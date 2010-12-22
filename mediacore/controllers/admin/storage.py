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
from mediacore.lib.storage import sort_engines, StorageEngine
from mediacore.model import DBSession, fetch_row
from mediacore.plugin import events

log = logging.getLogger(__name__)

class StorageController(BaseController):
    """Admin storage engine actions"""
    allow_only = has_permission('admin')

    @expose('admin/storage/index.html')
    def index(self, page=1, **kwargs):
        """List storage engines with pagination.

        :rtype: Dict
        :returns:
            engines
                The list of :class:`~mediacore.lib.storage.StorageEngine`
                instances for this page.

        """
        engines = DBSession.query(StorageEngine)\
            .options(orm.undefer('file_count'),
                     orm.undefer('file_size_sum'))\
            .all()
        engines = list(sort_engines(engines))
        existing_types = set(ecls.engine_type for ecls in engines)
        addable_engines = [
            ecls
            for ecls in StorageEngine
            if not ecls.is_singleton or ecls.engine_type not in existing_types
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

            if not engine.settings_form:
                # XXX: If this newly created storage engine has no settings,
                #      just save it. This isn't RESTful (as edit is a GET
                #      action), but it simplifies the creation process.
                DBSession.add(engine)
                redirect(controller='/admin/storage', action='index')

        return {
            'engine': engine,
            'form': engine.settings_form,
            'form_action': url_for(action='save', engine_type=engine_type),
            'form_values': kwargs,
        }

    @expose()
    def save(self, id, engine_type=None, **kwargs):
        if id == 'new':
            assert engine_type is not None, 'engine_type must be specified when saving a new StorageEngine.'
            engine_class = [x for x in StorageEngine if x.engine_type == engine_type][0]
        else:
            engine_class = StorageEngine

        engine = fetch_row(engine_class, id)
        form = engine.settings_form

        if id == 'new':
            DBSession.add(engine)

        @validate(form, error_handler=self.edit)
        def save_engine_params(id, general, **kwargs):
            # Allow the form to modify the StorageEngine directly
            # since each can have radically different fields.
            save_func = getattr(form, 'save_engine_params')
            save_func(engine, **tmpl_context.form_values)
            redirect(controller='/admin/storage', action='index')

        return save_engine_params(id, **kwargs)

    @expose('json')
    def delete(self, id, **kwargs):
        """Delete a StorageEngine.

        :param id: Storage ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
        engine = fetch_row(StorageEngine, id)
        files = engine.files
        for f in files:
            engine.delete(f.unique_id)
        DBSession.delete(engine)
        redirect(action='index', id=None)


    @expose()
    def enable(self, id, **kwargs):
        """Enable a StorageEngine.

        :param id: Storage ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        engine = fetch_row(StorageEngine, id)
        engine.enabled = True
        redirect(action='index', id=None)

    @expose()
    def disable(self, id, **kwargs):
        """Disable a StorageEngine.

        :param id: engine ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        engine = fetch_row(StorageEngine, id)
        engine.enabled = False
        redirect(action='index', id=None)

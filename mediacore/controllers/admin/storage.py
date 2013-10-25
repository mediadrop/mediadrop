# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging

from pylons import tmpl_context
from sqlalchemy import orm

from mediacore.lib.auth import has_permission
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import autocommit, expose, observable, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.storage import sort_engines, StorageEngine
from mediacore.model import DBSession, fetch_row
from mediacore.plugin import events

log = logging.getLogger(__name__)

class StorageController(BaseController):
    """Admin storage engine actions"""
    allow_only = has_permission('admin')

    @expose('admin/storage/index.html')
    @observable(events.Admin.StorageController.index)
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
    @observable(events.Admin.StorageController.edit)
    def edit(self, id, engine_type=None, **kwargs):
        """Display the :class:`~mediacore.lib.storage.StorageEngine` for editing or adding.

        :param id: Storage ID
        :type id: ``int`` or ``"new"``
        :rtype: dict
        :returns:

        """
        engine = self.fetch_engine(id, engine_type)

        return {
            'engine': engine,
            'form': engine.settings_form,
            'form_action': url_for(action='save', engine_type=engine_type),
            'form_values': kwargs,
        }

    @expose(request_method='POST')
    @autocommit
    def save(self, id, engine_type=None, **kwargs):
        if id == 'new':
            assert engine_type is not None, 'engine_type must be specified when saving a new StorageEngine.'

        engine = self.fetch_engine(id, engine_type)
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

    def fetch_engine(self, id, engine_type=None):
        if id != 'new':
            engine = fetch_row(StorageEngine, id)
        else:
            types = dict((cls.engine_type, cls) for cls in StorageEngine)
            engine_cls = types.get(engine_type, None)
            if not engine_cls:
                redirect(controller='/admin/storage', action='index')
            engine = engine_cls()
        return engine

    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.StorageController.delete)
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

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.StorageController.enable)
    def enable(self, id, **kwargs):
        """Enable a StorageEngine.

        :param id: Storage ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        engine = fetch_row(StorageEngine, id)
        engine.enabled = True
        redirect(action='index', id=None)

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.StorageController.disable)
    def disable(self, id, **kwargs):
        """Disable a StorageEngine.

        :param id: engine ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        engine = fetch_row(StorageEngine, id)
        engine.enabled = False
        redirect(action='index', id=None)

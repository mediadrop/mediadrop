from string import capitalize, rstrip
from tg import expose, validate, flash, require, url, request
from tg.exceptions import HTTPNotFound
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from simpleplex.lib import helpers
from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from simpleplex import model
from simpleplex.model import DBSession, metadata, fetch_row, Tag, Topic


class SettingadminController(RoutingController):
    """Admin settings actions which deal with settings"""
    allow_only = has_permission('admin')

    @expose()
    def index(self, section='tags', **kwargs):
        if section in ('topics', 'tags'):
            redirect(controller='categoryadmin', category=section)
        if section == 'users':
            redirect(controller='useradmin')
        raise HTTPNotFound

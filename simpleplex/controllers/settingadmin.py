from string import capitalize, rstrip
from tg import expose, validate, flash, require, url, request
from tg.decorators import paginate
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
    def index(self, section='users', **kwargs):
        if section == 'topics' or section == 'tags':
            redirect(controller='categoryadmin', category=section)
        if section == 'users':
            redirect(controller='useradmin')
        redirect('404.html')

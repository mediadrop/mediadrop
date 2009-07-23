from string import capitalize, rstrip
from tg import expose, validate, flash, require, url, request
from tg.decorators import paginate
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from mediaplex import model
from mediaplex.model import DBSession, metadata, fetch_row, Tag, Topic


class SettingadminController(RoutingController):
    """Admin settings actions which deal with settings"""
    allow_only = has_permission('admin')

    @expose()
    def index(self, section='topics', **kwargs):
        if section == 'topics' or section == 'tags':
            redirect(controller='categoryadmin', category=section)
        redirect('404.html')

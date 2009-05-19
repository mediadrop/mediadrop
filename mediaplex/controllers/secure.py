"""Test Secure Controller"""
from mediaplex.lib.base import RoutingController
from tg import expose, flash
from pylons.i18n import ugettext as _
#from tg import redirect, validate
#from mediaplex.model import DBSession, metadata
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from repoze.what.predicates import has_permission


class SecureController(RoutingController):
    """Sample controller-wide authorization"""

    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('manage',
                                msg=_('Only for people with the "manage" permission'))

    @expose('mediaplex.templates.index')
    def index(self):
        flash(_("Secure Controller here"))
        return dict(page='index')

    @expose('mediaplex.templates.index')
    def some_where(self):
        """should be protected because of the require attr
        at the controller level.
        """
        return dict(page='some_where')

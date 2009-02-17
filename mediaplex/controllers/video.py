
from mediaplex.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _
#from tg import redirect, validate

from mediaplex.model import DBSession, metadata, Video

class VideoController(BaseController):
    @expose('mediaplex.templates.video.index')
    def index(self, **kwargs):
        """List Action"""
        videos = DBSession.query(Video)
        return dict()

    @expose()
    def lookup(self, slug, *remainder):
        video = VideoRowController(slug)
        return video, remainder


class VideoRowController(object):
    def __init__(self, slug):
        self.video = DBSession.query(Video).filter_by(slug=slug).one()

    @expose('mediaplex.templates.video.view')
    def view(self):
        return dict(video=self.video)
    default = view

    @expose()
    def rate(self):
        return 'edit video'

    @expose()
    def download(self):
        return 'download video'

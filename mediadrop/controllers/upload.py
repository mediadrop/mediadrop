# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import simplejson as json

from pylons import request, tmpl_context
from pylons.controllers.util import abort

from mediadrop.forms.uploader import UploadForm
from mediadrop.lib import email
from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import autocommit, expose, observable, validate
from mediadrop.lib.helpers import redirect, url_for
from mediadrop.lib.storage import add_new_media_file
from mediadrop.lib.thumbnails import create_default_thumbs_for, has_thumbs
from mediadrop.model import Author, DBSession, get_available_slug, Media
from mediadrop.plugin import events

import logging
log = logging.getLogger(__name__)

upload_form = UploadForm(
    action = url_for(controller='/upload', action='submit'),
    async_action = url_for(controller='/upload', action='submit_async')
)

class UploadController(BaseController):
    """
    Media Upload Controller
    """

    def __before__(self, *args, **kwargs):
        if not request.settings['appearance_enable_user_uploads']:
            abort(404)
        result = BaseController.__before__(self, *args, **kwargs)
        # BareBonesController will set request.perm
        if not request.perm.contains_permission('upload'):
            abort(404)
        return result

    @expose('upload/index.html')
    @observable(events.UploadController.index)
    def index(self, **kwargs):
        """Display the upload form.

        :rtype: Dict
        :returns:
            legal_wording
                XHTML legal wording for rendering
            support_email
                An help contact address
            upload_form
                The :class:`~mediadrop.forms.uploader.UploadForm` instance
            form_values
                ``dict`` form values, if any

        """
        support_emails = request.settings['email_support_requests']
        support_emails = email.parse_email_string(support_emails)
        support_email = support_emails and support_emails[0] or None

        return dict(
            legal_wording = request.settings['wording_user_uploads'],
            support_email = support_email,
            upload_form = upload_form,
            form_values = kwargs,
        )

    @expose('json', request_method='POST')
    @validate(upload_form)
    @autocommit
    @observable(events.UploadController.submit_async)
    def submit_async(self, **kwargs):
        """Ajax form validation and/or submission.

        This is the save handler for :class:`~mediadrop.forms.media.UploadForm`.

        When ajax is enabled this action is called for each field as the user
        fills them in. Although the entire form is validated, the JS only
        provides the value of one field at a time,

        :param validate: A JSON list of field names to check for validation
        :parma \*\*kwargs: One or more form field values.
        :rtype: JSON dict
        :returns:
            :When validating one or more fields:

            valid
                bool
            err
                A dict of error messages keyed by the field names

            :When saving an upload:

            success
                bool
            redirect
                If valid, the redirect url for the upload successful page.

        """
        if 'validate' in kwargs:
            # we're just validating the fields. no need to worry.
            fields = json.loads(kwargs['validate'])
            err = {}
            for field in fields:
                if field in tmpl_context.form_errors:
                    err[field] = tmpl_context.form_errors[field]

            data = dict(
                valid = len(err) == 0,
                err = err
            )
        else:
            # We're actually supposed to save the fields. Let's do it.
            if len(tmpl_context.form_errors) != 0:
                # if the form wasn't valid, return failure
                tmpl_context.form_errors['success'] = False
                data = tmpl_context.form_errors
            else:
                # else actually save it!
                kwargs.setdefault('name')

                media_obj = self.save_media_obj(
                    kwargs['name'], kwargs['email'],
                    kwargs['title'], kwargs['description'],
                    None, kwargs['file'], kwargs['url'],
                )
                email.send_media_notification(media_obj)
                data = dict(
                    success = True,
                    redirect = url_for(action='success')
                )

        return data

    @expose(request_method='POST')
    @validate(upload_form, error_handler=index)
    @autocommit
    @observable(events.UploadController.submit)
    def submit(self, **kwargs):
        """
        """
        kwargs.setdefault('name')

        # Save the media_obj!
        media_obj = self.save_media_obj(
            kwargs['name'], kwargs['email'],
            kwargs['title'], kwargs['description'],
            None, kwargs['file'], kwargs['url'],
        )
        email.send_media_notification(media_obj)

        # Redirect to success page!
        redirect(action='success')

    @expose('upload/success.html')
    @observable(events.UploadController.success)
    def success(self, **kwargs):
        return dict()

    @expose('upload/failure.html')
    @observable(events.UploadController.failure)
    def failure(self, **kwargs):
        return dict()

    def save_media_obj(self, name, email, title, description, tags, uploaded_file, url):
        # create our media object as a status-less placeholder initially
        media_obj = Media()
        media_obj.author = Author(name, email)
        media_obj.title = title
        media_obj.slug = get_available_slug(Media, title)
        media_obj.description = description
        if request.settings['wording_display_administrative_notes']:
            media_obj.notes = request.settings['wording_administrative_notes']
        media_obj.set_tags(tags)

        # Give the Media object an ID.
        DBSession.add(media_obj)
        DBSession.flush()

        # Create a MediaFile object, add it to the media_obj, and store the file permanently.
        media_file = add_new_media_file(media_obj, file=uploaded_file, url=url)

        # The thumbs may have been created already by add_new_media_file
        if not has_thumbs(media_obj):
            create_default_thumbs_for(media_obj)

        media_obj.update_status()
        DBSession.flush()

        return media_obj

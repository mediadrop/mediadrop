# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from tw.api import WidgetsList
from tw.forms.validators import FieldStorageUploadConverter

from mediacore.lib.i18n import N_
from mediacore.forms import ListForm, TextField, XHTMLTextArea, FileField, SubmitButton, email_validator
from mediacore.plugin import events

validators = dict(
    description = XHTMLTextArea.validator(
        messages = {'empty': N_('At least give it a short description...')},
        not_empty = True,
    ),
    name = TextField.validator(
        messages = {'empty': N_("You've gotta have a name!")},
        not_empty = True,
    ),
    title = TextField.validator(
        messages = {'empty': N_("You've gotta have a title!")},
        not_empty = True,
    ),
    url = TextField.validator(
        if_missing = None,
    ),
)

class UploadForm(ListForm):
    template = 'upload/form.html'
    id = 'upload-form'
    css_class = 'form'
    show_children_errors = False
    params = ['async_action']
    
    events = events.UploadForm
    
    class fields(WidgetsList):
        name = TextField(validator=validators['name'], label_text=N_('Your Name:'), maxlength=50)
        email = TextField(validator=email_validator(not_empty=True), label_text=N_('Your Email:'), help_text=N_('(will never be published)'), maxlength=255)
        title = TextField(validator=validators['title'], label_text=N_('Title:'), maxlength=255)
        description = XHTMLTextArea(validator=validators['description'], label_text=N_('Description:'), attrs=dict(rows=5, cols=25))
        url = TextField(validator=validators['url'], label_text=N_('Add a YouTube, Vimeo or Amazon S3 link:'), maxlength=255)
        file = FileField(validator=FieldStorageUploadConverter(if_missing=None, messages={'empty':N_('Oops! You forgot to enter a file.')}), label_text=N_('OR:'))
        submit = SubmitButton(default=N_('Submit'), css_classes=['mcore-btn', 'btn-submit'])

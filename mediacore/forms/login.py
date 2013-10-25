# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from tw.forms import PasswordField

from mediacore.forms import ListForm, TextField, SubmitButton

from mediacore.lib.i18n import N_
from mediacore.plugin import events

__all__ = ['LoginForm']

class LoginForm(ListForm):
    template = 'forms/box_form.html'
    method = 'POST'
    id = 'login-form'
    css_class = 'form clearfix'
    submit_text = None
    # For login failures we display only a generic (bad username or password) 
    # error message which is not related to any particular field. 
    # However I'd like to mark the input widgets as faulty without displaying 
    # the dummy errors (injected by LoginController programmatically as this 
    # form is not used for credential validation) so this will prevent the error
    # text from being displayed. However the actual input fields will be marked
    # with css classes anyway.
    show_children_errors = False

    fields = [
        TextField('login', label_text=N_('Username'), 
            # 'autofocus' is actually not XHTML-compliant
            attrs={'autofocus': True}),
        PasswordField('password', label_text=N_('Password')),
        
        SubmitButton('login_button', default=N_('Login'), 
            css_classes=['mcore-btn', 'btn-submit', 'f-rgt'])
    ]

    def post_init(self, *args, **kwargs):
        events.LoginForm(self)



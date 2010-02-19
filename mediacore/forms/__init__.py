# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
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

from tw import forms
from tw.api import JSLink, JSSource
from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, Button, HiddenField, PasswordField
from tw.forms.validators import Email
from tg.render import _get_tg_vars
from pylons.templating import pylons_globals
from mediacore.lib.helpers import line_break_xhtml, fetch_setting
from mediacore.lib.base import url_for
import mediacore


class LeniantValidationMixin(object):
    validator = forms.validators.Schema(
        allow_extra_fields=True, # Allow extra kwargs that tg likes to pass: pylons, start_request, environ...
    )

class SubmitButton(forms.SubmitButton):
    """Override the default SubmitButton validator.

    This allows us to have multiple submit buttons, or to have forms
    that are submitted without a submit button. The value for unclicked
    submit buttons will simply be C{None}.
    """
    validator = forms.validators.UnicodeString(if_missing=None)

class ResetButton(forms.ResetButton):
    validator = forms.validators.UnicodeString(if_missing=None)

class GlobalMixin(object):
    def display(self, *args, **kw):
        # Update the kwargs with the same values that are included in main templates
        # this allows us to access the following objects in widget templates:
        # ['tmpl_context', 'translator', 'session', 'ungettext', 'response', '_',
        #  'c', 'app_globals', 'g', 'url', 'h', 'request', 'helpers', 'N_', 'tg',
        #  'config']
        kw.update(_get_tg_vars())
        kw.update(pylons_globals())
        return forms.Widget.display(self, *args, **kw)

class Form(LeniantValidationMixin, GlobalMixin, forms.Form):
    pass

class ListForm(LeniantValidationMixin, GlobalMixin, forms.ListForm):
    pass

class TableForm(LeniantValidationMixin, GlobalMixin, forms.TableForm):
    pass

class CheckBoxList(GlobalMixin, forms.CheckBoxList):
    pass

class XHTMLTextArea(TextArea):
    javascript = [
        JSLink(link=url_for("/scripts/third-party/tiny_mce/tiny_mce.js")),
        JSSource("""window.addEvent('domready', function(){
tinyMCE.onAddEditor.add(function(t, ed){
	// Add an event for ajax form managers to call when dealing with these
	// elements, because they will often override the form's submit action
	ed.onInit.add(function(editor){
		ed.formElement.addEvent('beforeAjax', function(ev) {
			ed.save();
			ed.isNotDirty = 1;
		});
	});
});
tinyMCE.init({
	// General options
	mode : "specific_textareas",
	editor_selector: "tinymcearea",
	theme : "advanced",
	plugins : "advimage,advlink,media,print,xhtmlxtras,contextmenu,paste,inlinepopups,wordcount,autosave",
	// Theme options
	theme_advanced_buttons1: "bold,italic,del,ins,|,sub,sup,|,numlist,bullist,|,blockquote,link,unlink,|,code",
	theme_advanced_buttons2: "",
	theme_advanced_buttons3: "",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_statusbar_location : "bottom",
	theme_advanced_resizing : false
});
});""", location='headbottom')
    ]
    def display(self, value=None, **kwargs):
        if value:
            value = line_break_xhtml(value)

        # Enable the rich text editor, if dictated by the settings:
        if fetch_setting('enable_tinymce'):
            if 'css_classes' in kwargs:
                kwargs['css_classes'].append('tinymcearea')
            else:
                kwargs['css_classes'] = ['tinymcearea']

        return TextArea.display(self, value, **kwargs)

email_validator = Email(messages={
    'badUsername': 'The portion of the email address before the @ is invalid',
    'badDomain': 'The portion of this email address after the @ is invalid'
})


# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from BeautifulSoup import BeautifulStoneSoup
from formencode import FancyValidator
from formencode.api import Invalid
from pylons import app_globals, request
from tw import forms
from tw.api import JSLink, JSSource
from tw.forms import FileField, TextArea as tw_TA, TextField as tw_TF
from tw.forms.validators import Email

from mediacore.lib.i18n import N_, _
from mediacore.lib.xhtml import clean_xhtml, decode_entities, line_break_xhtml
from mediacore.lib.templating import tmpl_globals
from mediacore.lib.util import url_for
from mediacore.plugin import events


def leniant_schema():
    return forms.validators.Schema(
        # workaround to prevent an error if no checkbox is checked in a list
        # of checkboxes (e.g. sitemaps form, category association for media)
        # http://groups.google.com/group/toscawidgets-discuss/msg/36261a59e6745591
        if_key_missing='',
        # TODO: See if this is necessary now that we've stripped turbogears out.
        allow_extra_fields=True, # Allow extra kwargs that tg likes to pass: pylons, start_request, environ...
    )

class LeniantValidationMixin(object):
    validator = None
    event = None
    
    def post_init(self, *args, **kwargs):
        # we need to ensure that each form instance gets its own Schema instance
        # so it is safe for plugins to change class-level variables (e.g.
        # adding chained validators)
        if not self.validator:
            self.validator = leniant_schema()
        
        if getattr(self, 'event', None):
            self.event(self)

class LinkifyMixin(object):
    """
    Mixin that wraps the link param with url_for() prior to rendering.

    We cannot call url_for() when this module is imported because it may
    be imported by a plugin prior to the evironment being loaded.

    """
    def update_params(self, d):
        super(LinkifyMixin, self).update_params(d)
        d.link = url_for(d.link)

class ConditionalJSLink(LinkifyMixin, JSLink):
    """
    Initialize this resource with a boolean function as the 'condition'
    argument, and it will only render itself when that condition is true.
    """
    def render(self, *args, **kwargs):
        if not hasattr(self, 'condition') or self.condition():
            return super(JSLink, self).render(*args, **kwargs)
        return ""

class ConditionalJSSource(JSSource):
    """
    Initialize this resource with a boolean function as the 'condition'
    argument, and it will only render itself when that condition is true.
    """
    def render(self, *args, **kwargs):
        if not hasattr(self, 'condition') or self.condition():
            return super(JSSource, self).render(*args, **kwargs)
        return ""

class SubmitButton(forms.SubmitButton):
    """Override the default SubmitButton validator.

    This allows us to have multiple submit buttons, or to have forms
    that are submitted without a submit button. The value for unclicked
    submit buttons will simply be C{None}.
    """
    # if_missing/if_empty=None is important so the button text is displayed
    # correctly in case the form is displayed with errors (in which case the 
    # request parameters contain an empty ('') value for submit button and
    # ToscaWidgets will only use the default text if the value is None).
    validator = forms.validators.UnicodeString(if_missing=None, if_empty=None)
    template = 'forms/button.html'

class ResetButton(forms.ResetButton):
    # see SubmitButton for background on if_missing/if_empty
    validator = forms.validators.UnicodeString(if_missing=None, if_empty=None)
    template = 'forms/button.html'

class GlobalMixin(object):
    def display(self, *args, **kw):
        # TODO: See if this is still necessary. Furthermore, find out which variables it actually adds.
        # Update the kwargs with the same values that are included in main templates
        # this allows us to access the following objects in widget templates:
        # ['tmpl_context', 'translator', 'session', 'ungettext', 'response', '_',
        #  'c', 'app_globals', 'g', 'url', 'h', 'request', 'helpers', 'N_', 'tg',
        #  'config']
        kw.update(tmpl_globals())
        return forms.Widget.display(self, *args, **kw)

class Form(LeniantValidationMixin, GlobalMixin, forms.Form):
    pass

class ListForm(LeniantValidationMixin, GlobalMixin, forms.ListForm):
    pass

class TableForm(LeniantValidationMixin, GlobalMixin, forms.TableForm):
    pass

class CheckBoxList(GlobalMixin, forms.CheckBoxList):
    pass

class FileField(GlobalMixin, FileField):
    pass

class ListFieldSet(LeniantValidationMixin, forms.ListFieldSet):
    template = 'forms/fieldset.html'

class XHTMLEntityValidator(FancyValidator):
    def _to_python(self, value, state=None):
        """Convert XHTML entities to unicode."""
        return decode_entities(value)

class XHTMLValidator(FancyValidator):
    def _to_python(self, value, state=None):
        """Convert the given plain text or HTML into valid XHTML.

        Invalid elements are stripped or converted.
        Essentially a wapper for :func:`~mediacore.helpers.clean_xhtml`.
        """
        return clean_xhtml(value)

class TextField(tw_TF):
    """TextField widget with a good validator for its instances to use."""
    validator = FancyValidator

class TextArea(tw_TA):
    """TextArea widget with a good validator for its instances to use."""
    validator = FancyValidator

tiny_mce_condition = lambda: request.settings['rich_text_editor'] == 'tinymce'

class XHTMLTextArea(TextArea):
    validator = XHTMLValidator
    javascript = [
        ConditionalJSLink(
            link = '/scripts/third-party/tiny_mce/tiny_mce.js',
            condition = tiny_mce_condition,
        ),
        ConditionalJSSource("""window.addEvent('domready', function(){
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
	mode: "specific_textareas",
	editor_selector: "tinymcearea",
	theme: "advanced",
	plugins: "advimage,advlink,media,print,xhtmlxtras,contextmenu,paste,inlinepopups,wordcount,autosave",
	// Theme options
	theme_advanced_buttons1: "bold,italic,del,ins,|,sub,sup,|,numlist,bullist,|,blockquote,link,unlink,|,code",
	theme_advanced_buttons2: "",
	theme_advanced_buttons3: "",
	theme_advanced_toolbar_location: "top",
	theme_advanced_toolbar_align: "left",
	theme_advanced_statusbar_location: "bottom",
	theme_advanced_resizing: false,
	relative_urls : false,
	remove_script_host : false
});
});""",
            location = 'headbottom',
            condition = tiny_mce_condition,
        )
    ]

    def display(self, value=None, **kwargs):
        if value:
            # XXX: First, try to translate this string. This is necessary for
            #      the "Legal Wording" section of the Upload settings. The
            #      default string was extracted correctly but not translated.
            value = _(value)

            value = line_break_xhtml(value)

        # Enable the rich text editor, if dictated by the settings:
        if tiny_mce_condition():
            if 'css_classes' in kwargs:
                kwargs['css_classes'].append('tinymcearea')
            else:
                kwargs['css_classes'] = ['tinymcearea']

        return TextArea.display(self, value, **kwargs)

email_validator = Email(messages={
    'badUsername': N_('The portion of the email address before the @ is invalid'),
    'badDomain': N_('The portion of this email address after the @ is invalid')
})

class email_list_validator(FancyValidator):
    def __init__(self, *args, **kwargs):
        FancyValidator.__init__(self, *args, **kwargs)
        self.email = Email()

    def _to_python(self, value, state=None):
        """Validate a comma separated list of email addresses."""
        emails = [x.strip() for x in value.split(',')]
        good_emails = []
        messages = []

        for addr in emails:
            try:
                good_emails.append(self.email.to_python(addr, state))
            except Invalid, e:
                messages.append(str(e))

        if messages:
            raise Invalid("; ".join(messages), value, state)
        else:
            return ", ".join(good_emails)


from tw import forms
from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, Button, HiddenField
from tg.render import _get_tg_vars
from pylons.templating import pylons_globals
from mediaplex.lib.helpers import line_break_xhtml


class LeniantValidationMixin(object):
    validator = forms.validators.Schema(
        allow_extra_fields=True, # Allow extra kwargs that tg likes to pass: pylons, start_request, environ...
        ignore_key_missing=True, # Required for multiple submit buttons
    )

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

class XHTMLTextArea(TextArea):
    def display(self, value=None, **kwargs):
        if value:
            value = line_break_xhtml(value)
        return TextArea.display(self, value, **kwargs)

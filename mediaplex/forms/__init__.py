from tw import forms
from tg.render import _get_tg_vars
from pylons.templating import pylons_globals


class LeniantValidationMixin(object):
    validator = forms.validators.Schema(
        allow_extra_fields=True, # Allow extra kwargs that tg likes to pass: pylons, start_request, environ...
        ignore_key_missing=True, # Required for multiple submit buttons
    )

class GlobalMixin(object):
    def __call__(self, *args, **kw):
        # Update the kwargs with the same values that are included in main templates
        # this allows us to access the following objects in widget templates:
        # ['tmpl_context', 'translator', 'session', 'ungettext', 'response', '_',
        #  'c', 'app_globals', 'g', 'url', 'h', 'request', 'helpers', 'N_', 'tg',
        #  'config']
        kw.update(_get_tg_vars())
        kw.update(pylons_globals())
        return forms.Widget.__call__(self, *args, **kw)

class Form(LeniantValidationMixin, forms.Form):
    pass

class ListForm(LeniantValidationMixin, forms.ListForm):
    pass

class TableForm(LeniantValidationMixin, GlobalMixin, forms.TableForm):
    pass

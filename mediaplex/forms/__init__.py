from tw import forms


class LeniantValidationMixin(object):
    validator = forms.validators.Schema(
        allow_extra_fields=True, # Allow extra kwargs that tg likes to pass: pylons, start_request, environ...
        ignore_key_missing=True, # Required for multiple submit buttons
    )

class ListForm(LeniantValidationMixin, forms.ListForm):
    pass

class TableForm(LeniantValidationMixin, forms.TableForm):
    pass

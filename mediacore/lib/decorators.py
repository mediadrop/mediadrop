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

import os

import formencode
import tw.forms
import webob.exc

from genshi import XML
from pylons import config, request, response, tmpl_context
from pylons.templating import render_genshi as render
from pylons.decorators import jsonify

from mediacore.lib.paginate import paginate

__all__ = ['expose', 'expose_xhr', 'paginate', 'validate']

_func_attrs = [
    # Attributes that define useful information or context for functions
    '__dict__', '__doc__', '__name__', 'im_class', 'im_func', 'im_self',
    'template', 'exposed' # custom attribute to allow web access
]

def _copy_func_attrs(f1, f2):
    """Copy relevant attributes from f1 to f2

    TODO: maybe replace this with the use of functools.wraps
    http://docs.python.org/library/functools.html#functools.wraps
    """

    for x in _func_attrs:
        if hasattr(f1, x):
            setattr(f2, x, getattr(f1, x))

def _get_func_attrs(f):
    """Return a dict of attributes. Used for debugging."""
    result = {}
    for x in _func_attrs:
        result[x] = getattr(f, x, (None,))
    return result

def _expose_wrapper(f, template):
    """Returns a function that will render the passed in function according
    to the passed in template"""
    f.exposed = True
    f.template = template

    if template == "json":
        return jsonify(f)
    elif template == "string":
        return f

    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)

        extra_vars = {
            # Steal a page from TurboGears' book:
            # include the genshi XML helper for convenience in templates.
            'XML': XML
        }
        extra_vars.update(result)

        if request.environ.get('paste.testing', False):
            # Make the vars passed from action to template accessible to tests
            request.environ['paste.testing_variables']['tmpl_vars'] = result

            # Serve application/xhtml+xml instead of text/html during testing.
            # This allows us to query the response xhtml as ElementTree XML
            # instead of BeautifulSoup HTML.
            # NOTE: We do not serve true xhtml to all clients that support it
            #       because of a bug in Mootools Swiff as of v1.2.4:
            #       https://mootools.lighthouseapp.com/projects/2706/tickets/758
            if response.content_type == 'text/html':
                response.content_type = 'application/xhtml+xml'

        return render(template, extra_vars=extra_vars)
    return wrapped_f

def expose(template='string'):
    """Simple expose decorator for controller actions.

    Transparently wraps a method in a function that will render the method's
    return value with the given template.

    Sets the 'exposed' and 'template' attributes of the wrapped method,
    marking it as safe to be accessed via HTTP request.

    Example, using a genshi template::

        class MyController(BaseController):

            @expose('path/to/template.html')
            def sample_action(self, *args):
                # do something
                return dict(message='Hello World!')

    :param template:
        One of:
            * The path to a genshi template, relative to the project's
              template directory
            * 'string'
            * 'json'
    :type template: string or unicode

    """
    def wrap(f):
        wrapped_f = _expose_wrapper(f, template)
        _copy_func_attrs(f, wrapped_f)
        return wrapped_f
    return wrap

def expose_xhr(template_norm='string', template_xhr='json'):
    """
    Expose different templates for normal vs XMLHttpRequest requests.

    Example, using two genshi templates::

        class MyController(BaseController):

            @expose_xhr('items/main_list.html', 'items/ajax_list.html')
            def sample_action(self, *args):
                # do something
                return dict(items=get_items_list())
    """
    def wrap(f):
        norm = _expose_wrapper(f, template_norm)
        xhr = _expose_wrapper(f, template_xhr)

        def choose(*args, **kwargs):
            if request.is_xhr:
                return xhr(*args, **kwargs)
            else:
                return norm(*args, **kwargs)
        _copy_func_attrs(f, choose)
        return choose
    return wrap

class validate(object):
    """Registers which validators ought to be applied to the following action

    Copies the functionality of TurboGears2.0, rather than that of Pylons1.0,
    except that we validate request.params, not kwargs. TurboGears has the
    unfortunate need to validate all kwargs because it uses object dispatch.
    We really only need to validate request.params: if we do need to
    validate the kw/routing args we can and should do that in our routes.

    If you want to validate the contents of your form,
    you can use the ``@validate()`` decorator to register
    the validators that ought to be called.

    :Parameters:
      validators
        Pass in a dictionary of FormEncode validators.
        The keys should match the form field names.
      error_handler
        Pass in the controller method which should be used
        to handle any form errors
      form
        Pass in a ToscaWidget based form with validators

    The first positional parameter can either be a dictonary of validators,
    a FormEncode schema validator, or a callable which acts like a FormEncode
    validator.
    """
    def __init__(self, validators=None, error_handler=None, form=None):
        if form:
            self.validators = form
        if validators:
            self.validators = validators
        self.error_handler = error_handler

    def __call__(self, func):
        self.func = func
        def validate(*args, **kwargs):
            # Initialize validation context
            tmpl_context.form_errors = {}
            tmpl_context.form_values = {}
            try:
                # Perform the validation
                values = self._to_python(request.params.mixed())
                tmpl_context.form_values = values
                # We like having our request params as kwargs but this is optional
                kwargs.update(values)
                # Call the decorated function
                return self.func(*args, **kwargs)
            except formencode.api.Invalid, inv:
                # Unless the input was in valid. In which case...
                return self._handle_validation_errors(args, kwargs, inv)
        _copy_func_attrs(func, validate)
        return validate

    def _handle_validation_errors(self, args, kwargs, exception):
        """
        Sets up tmpl_context.form_values and tmpl_context.form_errors to assist
        generating a form with given values and the validation failure
        messages.
        """
        tmpl_context.validation_exception = exception
        tmpl_context.form_errors = {}

        # Most Invalid objects come back with a list of errors in the format:
        # "fieldname1: error\nfieldname2: error"
        error_list = exception.__str__().split('\n')

        # Set up the tmpl_context.form_errors dict
        for error in error_list:
            field_value = error.split(':')
            # if the error has no field associated with it,
            # return the error as a global form error
            if len(field_value) == 1:
                tmpl_context.form_errors['_the_form'] = field_value[0].strip()
                continue
            tmpl_context.form_errors[field_value[0]] = field_value[1].strip()

        # Set up the tmpl_context.form_values dict with the invalid values
        tmpl_context.form_values = exception.value

        return self._call_error_handler(args, kwargs)

    def _call_error_handler(self, args, kwargs):
        # Get the correct error_handler function
        error_handler = self.error_handler
        if error_handler is None:
            error_handler = self.func
        return error_handler(*args, **kwargs)

    def _to_python(self, params):
        """
        self.validators can be in three forms:

        1) A dictionary, with key being the request parameter name, and value a
           FormEncode validator.

        2) A FormEncode Schema object

        3) Any object with a "validate" method that takes a dictionary of the
           request variables.

        Validation can "clean" or otherwise modify the parameters that were
        passed in, not just raise an exception.  Validation exceptions should
        be FormEncode Invalid objects.
        """
        if isinstance(self.validators, dict):
            new_params = {}
            errors = {}
            for field, validator in self.validators.iteritems():
                try:
                    new_params[field] = validator.to_python(params.get(field))
                # catch individual validation errors into the errors dictionary
                except formencode.api.Invalid, inv:
                    errors[field] = inv

            # If there are errors, create a compound validation error based on
            # the errors dictionary, and raise it as an exception
            if errors:
                raise formencode.api.Invalid(
                    formencode.schema.format_compound_error(errors),
                    params, None, error_dict=errors)
            return new_params

        elif isinstance(self.validators, formencode.Schema):
            # A FormEncode Schema object - to_python converts the incoming
            # parameters to sanitized Python values
            return v.to_python(params)

        elif isinstance(self.validators, tw.forms.InputWidget) \
        or hasattr(self.validators, 'validate'):
            # A tw.forms.InputWidget object. validate converts the incoming
            # parameters to sanitized Python values
            # - OR -
            # An object with a "validate" method - call it with the parameters
            # This is a generic case for classes mimicking tw.forms.InputWidget
            return self.validators.validate(params)

        # No validation was done. Just return the original params.
        return params

class validate_xhr(validate):
    """
    Special validation that returns JSON dicts for Ajax requests.

    Regular synchronous requests are handled normally.

    Example Usage::

        @expose_xhr()
        @validate_xhr(my_form_instance, error_handler=edit)
        def save(self, id, **kwargs):
            something = make_something()
            if request.is_xhr:
                return dict(my_id=something.id)
            else:
                redirect(action='view', id=id)

    On success, returns this in addition to whatever dict you provide::

        {'success': True, 'values': {}, 'my_id': 123}

    On validation error, returns::

        {'success': False, 'values': {}, 'errors': {}}

    """
    def __call__(self, func):
        """Catch redirects in the controller action and return JSON."""
        self.validate_func = super(validate_xhr, self).__call__(func)
        def validate_wrapper(*args, **kwargs):
            result = self.validate_func(*args, **kwargs)
            if request.is_xhr:
                if not isinstance(result, dict):
                    result = {}
                result.setdefault('success', True)
                values = result.get('values', {})
                for key, value in tmpl_context.form_values.iteritems():
                    values.setdefault(key, value)
            return result
        _copy_func_attrs(func, validate_wrapper)
        return validate_wrapper

    def _call_error_handler(self, args, kwargs):
        if request.is_xhr:
            return {'success': False, 'errors': tmpl_context.form_errors}
        else:
            return super(validate_xhr, self)._call_error_handler(args, kwargs)

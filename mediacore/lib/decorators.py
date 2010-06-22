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

_pylons_kwargs = [
    # extra kwargs that Pylons/Routes like to send to controller actions
    'pylons', 'start_response', 'controller', 'environ', 'action'
]

def kwargs_for_validator(validator, kwargs):
    """Takes a formencode.Schema object and a dict of kwargs.

    Returns a dict with all _pylons_kwargs stripped out, unless
    those args are explicitly required by the validator.
    """
    new_kwargs = {}
    extra_keys = [x for x in _pylons_kwargs if x not in validator.fields]
    for key, value in kwargs.items():
        if key not in extra_keys:
            new_kwargs[key] = value
    return new_kwargs


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

        # If the provided template path isn't absolute (ie, doesn't start with
        # a '/'), then prepend the default search path. By providing the
        # template path to genshi as an absolute path, we invoke different
        # rules for the resolution of 'xi:include' paths in the template.
        # See http://genshi.edgewall.org/browser/trunk/genshi/template/loader.py#L178
        if not template.startswith('/'):
            tmpl = os.path.join(config['genshi_search_path'], template)
        else:
            tmpl = template

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

        return render(tmpl, extra_vars=extra_vars)
    return wrapped_f

def expose(template='string'):
    """Simple expose decorator for controller actions.

    Transparently wraps a method in a function that will render the method's
    return value with the given template.

    Sets the 'exposed' and 'template' attributes of the wrapped method,
    marking it as safe to be accessed via HTTP request.

    :Usage:

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

def expose_xhr(template_norm='', template_xhr='json'):
    """
    Expose different templates for normal vs XMLHttpRequest requests.

    :Usage:

    Example, using two genshi templates:

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

    Copies the functionality of TurboGears2.0, rather than that of Pylons1.0

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
                kwargs = self._to_python(kwargs)
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

        # Set up the tmpl_context.form_values dict
        tmpl_context.form_values = exception.value

        return self._call_error_handler(args, kwargs)

    def _call_error_handler(self, args, kwargs):
        # Get the correct error_handler function
        error_handler = self.error_handler
        if error_handler is None:
            error_handler = self.func
        return error_handler(*args, **kwargs)

    def _to_python(self, kwargs):
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
        #Initialize new_kwargs -- if it never gets updated just return kwargs
        new_kwargs = {}

        # The validator may be a dictionary, a FormEncode Schema object, or any
        # object with a "validate" method.
        if isinstance(self.validators, dict):
            errors = {}
            for field, validator in self.validators.iteritems():
                try:
                    new_kwargs[field] = validator.to_python(kwargs.get(field))
                # catch individual validation errors into the errors dictionary
                except formencode.api.Invalid, inv:
                    errors[field] = inv

            # Parameters that don't have validators are returned verbatim
            for param, param_value in kwargs.items():
                if not param in new_kwargs:
                    new_kwargs[param] = param_value

            # If there are errors, create a compound validation error based on
            # the errors dictionary, and raise it as an exception
            if errors:
                raise formencode.api.Invalid(
                    formencode.schema.format_compound_error(errors),
                    kwargs, None, error_dict=errors)

        elif isinstance(self.validators, formencode.Schema):
            # A FormEncode Schema object - to_python converts the incoming
            # parameters to sanitized Python values
            v = self.validators

            # 1) First, filter out the extra kwargs that pylons passes in
            new_kwargs = kwargs_for_validator(v, kwargs)
            # 2) Validate the appropriate kwargs
            new_kwargs = v.to_python(new_kwargs)
            # 3) Replace the extra kwargs that Pylons passes in
            for key in [x for x in kwargs if x not in new_kwargs]:
                new_kwargs[key] = kwargs[key]

        elif isinstance(self.validators, tw.forms.InputWidget):
            # A tw.forms.InputWidget object. validate converts the incoming
            # parameters to sanitized Python values

            # 1) First, try to filter out the extra kwargs that pylons passes in
            v = getattr(self.validators, 'validator', None)
            if v:
                new_kwargs = kwargs_for_validator(v, kwargs)
            # 2) Validate the appropriate kwargs
            new_kwargs = self.validators.validate(new_kwargs)
            # 3) Replace the extra kwargs that Pylons passes in (if previously stripped)
            for key in [x for x in kwargs if x not in new_kwargs]:
                new_kwargs[key] = kwargs[key]

        elif hasattr(self.validators, 'validate'):
            # An object with a "validate" method - call it with the parameters
            # This is a generic case for classes mimicking tw.forms.InputWidget
            new_kwargs = self.validators.validate(kwargs)

        else:
            # No validation was done. Just return the original kwargs.
            return kwargs

        return new_kwargs

class validate_xhr(validate):
    """
    Special validation that returns JSON dicts for Ajax requests.

    Regular synchronous requests are handled normally.

    Example usage::

        @expose_xhr()
        @validate_xhr(my_form_instance, error_handler=edit)
        def save(self, id, **kwargs):
            something = make_something()
            if request.is_xhr:
                return dict(my_id=something.id)
            else:
                redirect(id=id)

    On success, returns this in addition to whatever dict you provide::

        {'success': True, 'values': {}, 'my_id': 123}

    On validation error, returns::

        {'success': False, 'values': {}, 'errors': {}}

    """
    def __call__(self, func):
        """Catch redirects in the controller action and return JSON."""
        self.validate_func = super(validate_xhr, self).__call__(func)
        def validate_wrapper(*args, **kwargs):
            result = {}
            try:
                result = self.validate_func(*args, **kwargs)
            except webob.exc.HTTPRedirection:
                if not request.is_xhr:
                    raise
            if request.is_xhr:
                if not isinstance(result, dict):
                    result = {}
                result.setdefault('success', True)
                result.setdefault('values', request.params.mixed())
            return result
        _copy_func_attrs(func, validate_wrapper)
        return validate_wrapper

    def _call_error_handler(self, args, kwargs):
        if request.is_xhr:
            return {'success': False, 'errors': tmpl_context.form_errors}
        else:
            return super(validate_xhr, self)._call_error_handler(args, kwargs)

# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import warnings
import simplejson
import time

import formencode
import tw.forms

from decorator import decorator
from paste.deploy.converters import asbool
from pylons import config, request, response, tmpl_context, translator
from pylons.decorators.cache import create_cache_key, _make_dict_from_args
from pylons.decorators.util import get_pylons
from webob.exc import HTTPException, HTTPMethodNotAllowed

from mediacore.lib.paginate import paginate
from mediacore.lib.templating import render

__all__ = [
    'ValidationState',
    'autocommit',
    'beaker_cache',
    'expose',
    'expose_xhr',
    'memoize',
    'observable',
    'paginate',
    'validate',
    'validate_xhr',
]

log = logging.getLogger(__name__)

# TODO: Rework all decorators to use the decorators module. By using it,
#       the function signature of the original action method is preserved,
#       allowing pylons.controllers.core.WSGIController._inspect_call to
#       do its job properly.

_func_attrs = [
    # Attributes that define useful information or context for functions
    '__dict__', '__doc__', '__name__', 'im_class', 'im_func', 'im_self',
    'exposed', # custom attribute to allow web access
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

def _expose_wrapper(f, template, request_method=None, permission=None):
    """Returns a function that will render the passed in function according
    to the passed in template"""
    f.exposed = True

    # Shortcut for simple expose of strings
    if template == 'string' and not request_method and not permission:
        return f

    if request_method:
        request_method = request_method.upper()

    def wrapped_f(*args, **kwargs):
        if request_method and request_method != request.method:
            raise HTTPMethodNotAllowed().exception

        result = f(*args, **kwargs)
        tmpl = template

        if hasattr(request, 'override_template'):
            tmpl = request.override_template

        if tmpl == 'string':
            return result

        if tmpl == 'json':
            if isinstance(result, (list, tuple)):
                msg = ("JSON responses with Array envelopes are susceptible "
                       "to cross-site data leak attacks, see "
                       "http://wiki.pylonshq.com/display/pylonsfaq/Warnings")
                if config['debug']:
                    raise TypeError(msg)
                warnings.warn(msg, Warning, 2)
                log.warning(msg)
            response.headers['Content-Type'] = 'application/json'
            return simplejson.dumps(result)

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

        return render(tmpl, tmpl_vars=result, method='auto')

    if permission:
        from mediacore.lib.auth import FunctionProtector, has_permission
        wrapped_f = FunctionProtector(has_permission(permission)).wrap(wrapped_f)

    return wrapped_f

def expose(template='string', request_method=None, permission=None):
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

    :param request_method: Optional request method to verify. If GET or
        POST is given and the method of the current request does not match,
        a 405 Method Not Allowed error is raised.

    """
    def wrap(f):
        wrapped_f = _expose_wrapper(f, template, request_method, permission)
        _copy_func_attrs(f, wrapped_f)
        return wrapped_f
    return wrap

def expose_xhr(template_norm='string', template_xhr='json',
               request_method=None, permission=None):
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
        norm = _expose_wrapper(f, template_norm, request_method, permission)
        xhr = _expose_wrapper(f, template_xhr, request_method, permission)

        def choose(*args, **kwargs):
            if request.is_xhr:
                return xhr(*args, **kwargs)
            else:
                return norm(*args, **kwargs)
        _copy_func_attrs(f, choose)
        return choose
    return wrap

class ValidationState(object):
    """A ``state`` for FormEncode validate API with a smart ``_`` hook.

    This idea and explanation borrowed from Pylons, modified to work with
    our custom Translator object.

    The FormEncode library used by validate() decorator has some
    provision for localizing error messages. In particular, it looks
    for attribute ``_`` in the application-specific state object that
    gets passed to every ``.to_python()`` call. If it is found, the
    ``_`` is assumed to be a gettext-like function and is called to
    localize error messages.

    One complication is that FormEncode ships with localized error
    messages for standard validators so the user may want to re-use
    them instead of gathering and translating everything from scratch.
    To allow this, we pass as ``_`` a function which looks up
    translation both in application and formencode message catalogs.

    """
    @staticmethod
    def _(msgid):
        """Get a translated string from the mediacore or FormEncode domains.

        This allows us to "merge" localized error messages from built-in
        FormEncode's validators with application-specific validators.

        :type msgid: ``str``
        :param msgid: A byte string to retrieve translations for.
        :rtype: ``unicode``
        :returns: The translated string, or the original msgid if no
            translation was found.
        """
        gettext = translator.gettext
        trans = gettext(msgid)
        if trans == msgid:
            trans = gettext(msgid, domain='FormEncode')
        return trans

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

    The first positional parameter can either be a dictionary of validators,
    a FormEncode schema validator, or a callable which acts like a FormEncode
    validator.
    """
    def __init__(self, validators=None, error_handler=None, form=None,
                 state=ValidationState):
        if form:
            self.validators = form
        if validators:
            self.validators = validators
        self.error_handler = error_handler
        self.state = state

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
        c = tmpl_context._current_obj()
        c.validation_exception = exception

        # Set up the tmpl_context.form_values dict with the invalid values
        c.form_values = exception.value

        # Set up the tmpl_context.form_errors dict
        c.form_errors = exception.unpack_errors()
        if not isinstance(c.form_errors, dict):
            c.form_errors = {'_the_form': c.form_errors}

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
                    new_params[field] = validator.to_python(params.get(field),
                                                            self.state)
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
            return self.validators.to_python(params, self.state)

        elif isinstance(self.validators, tw.forms.InputWidget) \
        or hasattr(self.validators, 'validate'):
            # A tw.forms.InputWidget object. validate converts the incoming
            # parameters to sanitized Python values
            # - OR -
            # An object with a "validate" method - call it with the parameters
            # This is a generic case for classes mimicking tw.forms.InputWidget
            return self.validators.validate(params, self.state)

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

def beaker_cache(key="cache_default", expire="never", type=None,
                 query_args=False,
                 cache_headers=('content-type', 'content-length'),
                 invalidate_on_startup=False,
                 cache_response=True, **b_kwargs):
    """Cache decorator utilizing Beaker. Caches action or other
    function that returns a pickle-able object as a result.

    Optional arguments:

    ``key``
        None - No variable key, uses function name as key
        "cache_default" - Uses all function arguments as the key
        string - Use kwargs[key] as key
        list - Use [kwargs[k] for k in list] as key
    ``expire``
        Time in seconds before cache expires, or the string "never".
        Defaults to "never"
    ``type``
        Type of cache to use: dbm, memory, file, memcached, or None for
        Beaker's default
    ``query_args``
        Uses the query arguments as the key, defaults to False
    ``cache_headers``
        A tuple of header names indicating response headers that
        will also be cached.
    ``invalidate_on_startup``
        If True, the cache will be invalidated each time the application
        starts or is restarted.
    ``cache_response``
        Determines whether the response at the time beaker_cache is used
        should be cached or not, defaults to True.

        .. note::
            When cache_response is set to False, the cache_headers
            argument is ignored as none of the response is cached.

    If cache_enabled is set to False in the .ini file, then cache is
    disabled globally.

    """
    if invalidate_on_startup:
        starttime = time.time()
    else:
        starttime = None
    cache_headers = set(cache_headers)

    def wrapper(func, *args, **kwargs):
        """Decorator wrapper"""
        pylons = get_pylons(args)
        log.debug("Wrapped with key: %s, expire: %s, type: %s, query_args: %s",
                  key, expire, type, query_args)
        enabled = pylons.config.get("cache_enabled", "True")
        if not asbool(enabled):
            log.debug("Caching disabled, skipping cache lookup")
            return func(*args, **kwargs)

        if key:
            key_dict = kwargs.copy()
            key_dict.update(_make_dict_from_args(func, args))

            ## FIXME: if we can stop there variables from being passed to the
            # controller action (also the Genshi Markup/pickle problem is
            # fixed, see below) then we can use the stock beaker_cache.
            # Remove some system variables that can cause issues while generating cache keys
            [key_dict.pop(x, None) for x in ("pylons", "start_response", "environ")]

            if query_args:
                key_dict.update(pylons.request.GET.mixed())

            if key != "cache_default":
                if isinstance(key, list):
                    key_dict = dict((k, key_dict[k]) for k in key)
                else:
                    key_dict = {key: key_dict[key]}
        else:
            key_dict = None

        self = None
        if args:
            self = args[0]
        namespace, cache_key = create_cache_key(func, key_dict, self)

        if type:
            b_kwargs['type'] = type

        cache_obj = getattr(pylons.app_globals, 'cache', None)
        if not cache_obj:
            cache_obj = getattr(pylons, 'cache', None)
        if not cache_obj:
            raise Exception('No cache object found')
        my_cache = cache_obj.get_cache(namespace, **b_kwargs)

        if expire == "never":
            cache_expire = None
        else:
            cache_expire = expire

        def create_func():
            log.debug("Creating new cache copy with key: %s, type: %s",
                      cache_key, type)
            result = func(*args, **kwargs)
            # This is one of the two changes to the stock beaker_cache
            # decorator
            if hasattr(result, '__html__'):
                # Genshi Markup object, can not be pickled
                result = unicode(result.__html__())
            glob_response = pylons.response
            headers = glob_response.headerlist
            status = glob_response.status
            full_response = dict(headers=headers, status=status,
                                 cookies=None, content=result)
            return full_response

        response = my_cache.get_value(cache_key, createfunc=create_func,
                                      expiretime=cache_expire,
                                      starttime=starttime)
        if cache_response:
            glob_response = pylons.response
            glob_response.headerlist = [header for header in response['headers']
                                        if header[0].lower() in cache_headers]
            glob_response.status = response['status']

        return response['content']
    return decorator(wrapper)

def observable(event):
    """Filter the result of the decorated action through the events observers.

    :param event: An instance of :class:`mediacore.plugin.events.Event`
        whose observers are called.
    :returns: A decorator function.
    """
    def wrapper(func, *args, **kwargs):
        for observer in event.pre_observers:
            args, kwargs = observer(*args, **kwargs)
        result = func(*args, **kwargs)
        for observer in event.post_observers:
            result = observer(**result)
        return result
    return decorator(wrapper)

def _memoize(func, *args, **kwargs):
    if kwargs: # frozenset is used to ensure hashability
        key = args, frozenset(kwargs.iteritems())
    else:
        key = args
    cache = func.cache # attributed added by memoize
    if key in cache:
        return cache[key]
    else:
        cache[key] = result = func(*args, **kwargs)
        return result

def memoize(func):
    """Decorate this function so cached results are returned indefinitely.

    Copied from docs for the decorator module by Michele Simionato:
    http://micheles.googlecode.com/hg/decorator/documentation.html#the-solution
    """
    func.cache = {}
    return decorator(_memoize, func)

@decorator
def autocommit(func, *args, **kwargs):
    """Handle database transactions for the decorated controller actions.

    This decorator supports firing callbacks immediately after the
    transaction is committed or rolled back. This is useful when some
    external process needs to be called to process some new data, since
    it should only be called once that data is readable by new transactions.

    .. note:: If your callback makes modifications to the database, you must
        manually handle the transaction, or apply the @autocommit decorator
        to the callback itself.

    On the ingress, two attributes are added to the :class:`webob.Request`:

        ``request.commit_callbacks``
            A list of callback functions that should be called immediately
            after the DBSession has been committed by this decorator.

        ``request.rollback_callbacks``
            A list of callback functions that should be called immediately
            after the DBSession has been rolled back by this decorator.

    On the egress, we determine which callbacks should be called, remove
    the above attributes from the request, and then call the appropriate
    callbacks.

    """
    req = request._current_obj()
    req.commit_callbacks = []
    req.rollback_callbacks = []
    try:
        result = func(*args, **kwargs)
    except HTTPException, e:
        if 200 <= e.code < 400:
            _autocommit_commit(req)
        else:
            _autocommit_rollback(req)
        raise
    except:
        _autocommit_rollback(req)
        raise
    else:
        _autocommit_commit(req)
        return result

def _autocommit_commit(req):
    from mediacore.model.meta import DBSession
    try:
        DBSession.commit()
    except:
        _autocommit_rollback(req)
        raise
    else:
        _autocommit_fire_callbacks(req, req.commit_callbacks)

def _autocommit_rollback(req):
    from mediacore.model.meta import DBSession
    DBSession.rollback()
    _autocommit_fire_callbacks(req, req.rollback_callbacks)

def _autocommit_fire_callbacks(req, callbacks):
    # Clear the callback lists from the request so doing crazy things
    # like applying the autocommit decorator to an autocommit callback won't
    # conflict.
    del req.commit_callbacks
    del req.rollback_callbacks
    if callbacks:
        log.debug('@autocommit firing these callbacks: %r', callbacks)
        for cb in callbacks:
            cb()

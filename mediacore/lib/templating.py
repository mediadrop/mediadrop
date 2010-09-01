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

import logging
import os

from genshi import XML
from genshi.template import loader
from pylons import app_globals, request, tmpl_context
from pylons.templating import render_genshi as _render

__all__ = ['render', 'TemplateLoader']

log = logging.getLogger(__name__)

def render(template, extra_vars=None, method=None, **kwargs):
    """Render the given template with helpful default params.

    :param template: A template path.
    :param extra_vars: A dict of variables to pass into the template.
    :param method: The serialization method for Genshi to use.
        Defaults to xhtml unless the template file extension is xml.
    :returns: The rendered unicode string.

    """
    if extra_vars is None:
        extra_vars = {}
    assert isinstance(extra_vars, dict), \
        'extra_vars must be a dict or None, given: %r' % extra_vars

    # Steal a page from TurboGears' book:
    # include the genshi XML helper for convenience in templates.
    extra_vars.setdefault('XML', XML)

    # Default to xhtml serialization except when given a "*.xml" template file
    if method is None:
        if template.endswith('.xml'):
            method = 'xml'
        else:
            method = 'xhtml'

    # Pass in all the plugin templates that will manipulate this template
    # The idea is that these paths should be <xi:include> somewhere in the
    # top of the template file.
    plugin_mgr = app_globals.plugin_mgr
    if plugin_mgr:
        extra_vars['plugin_templates'] = plugin_mgr.match_templates(template)

    return _render(template, extra_vars=extra_vars, method=method, **kwargs)

class TemplateLoader(loader.TemplateLoader):
    def load(self, filename, relative_to=None, cls=None, encoding=None):
        """Load the template with the given name.

        XXX: This code copied and modified from Genshi 0.6

        If the `filename` parameter is relative, this method searches the
        search path trying to locate a template matching the given name. If the
        file name is an absolute path, the search path is ignored.

        If the requested template is not found, a `TemplateNotFound` exception
        is raised. Otherwise, a `Template` object is returned that represents
        the parsed template.

        Template instances are cached to avoid having to parse the same
        template file more than once. Thus, subsequent calls of this method
        with the same template file name will return the same `Template`
        object (unless the ``auto_reload`` option is enabled and the file was
        changed since the last parse.)

        If the `relative_to` parameter is provided, the `filename` is
        interpreted as being relative to that path.

        :param filename: the relative path of the template file to load
        :param relative_to: the filename of the template from which the new
                            template is being loaded, or ``None`` if the
                            template is being loaded directly
        :param cls: the class of the template object to instantiate
        :param encoding: the encoding of the template to load; defaults to the
                         ``default_encoding`` of the loader instance
        :return: the loaded `Template` instance
        :raises TemplateNotFound: if a template with the given name could not
                                  be found
        """
        if cls is None:
            cls = self.default_class
        search_path = self.search_path

        # Make the filename relative to the template file its being loaded
        # from, but only if that file is specified as a relative path, or no
        # search path has been set up
        if relative_to and (not search_path or not os.path.isabs(relative_to)):
            filename = os.path.join(os.path.dirname(relative_to), filename)

        filename = os.path.normpath(filename)
        cachekey = filename

        self._lock.acquire()
        try:
            # First check the cache to avoid reparsing the same file
            try:
                tmpl = self._cache[cachekey]
                if not self.auto_reload:
                    return tmpl
                uptodate = self._uptodate[cachekey]
                if uptodate is not None and uptodate():
                    return tmpl
            except (KeyError, OSError):
                pass

            isabs = False

            if os.path.isabs(filename):
                # Make absolute paths relative to the base search path.
                log.debug('Modifying the default TemplateLoader behaviour '
                          'for path %r; treating the absolute template path '
                          'as relative to the template search path.', filename)
                relative_to = None
                filename = filename[1:] # strip leading slash

            if relative_to and os.path.isabs(relative_to):
                # Make sure that the directory containing the including
                # template is on the search path
                dirname = os.path.dirname(relative_to)
                if dirname not in search_path:
                    search_path = list(search_path) + [dirname]
                isabs = True

            elif not search_path:
                # Uh oh, don't know where to look for the template
                raise TemplateError('Search path for templates not configured')

            for loadfunc in search_path:
                if isinstance(loadfunc, basestring):
                    loadfunc = loader.directory(loadfunc)
                try:
                    filepath, filename, fileobj, uptodate = loadfunc(filename)
                except IOError:
                    continue
                else:
                    try:
                        if isabs:
                            # If the filename of either the included or the
                            # including template is absolute, make sure the
                            # included template gets an absolute path, too,
                            # so that nested includes work properly without a
                            # search path
                            filename = filepath
                        tmpl = self._instantiate(cls, fileobj, filepath,
                                                 filename, encoding=encoding)
                        if self.callback:
                            self.callback(tmpl)
                        self._cache[cachekey] = tmpl
                        self._uptodate[cachekey] = uptodate
                    finally:
                        if hasattr(fileobj, 'close'):
                            fileobj.close()
                    return tmpl

            raise TemplateNotFound(filename, search_path)

        finally:
            self._lock.release()

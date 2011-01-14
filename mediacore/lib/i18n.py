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
from gettext import NullTranslations, translation as gettext_translation

from pylons import request, translator
from pylons.i18n.translation import lazify

log = logging.getLogger(__name__)

class LanguageError(Exception):
    pass

class DomainError(Exception):
    pass

class Translator(object):
    """
    Multi-Domain Translator for a single Locale.

    """
    def __init__(self, locale, locale_dirs):
        """Initialize this translator for the given locale.

        :type locale: :class:`babel.Locale`.
        :param locale: The locale to load translations for.
        :type locale_dirs: dict
        :param locale_dirs: A mapping of translation domain names to the
            localedir where they can be found. See :func:`gettext.translation`
            for more details.
        """
        self.locale = locale
        self._domains = {}
        self._locale_dirs = locale_dirs
        self._languages = [str(locale)]
        if locale.territory:
            self._languages.append(locale.language)

    def install_pylons_global(self):
        """Replace the current pylons.translator SOP with this instance.

        This is specific to the current request.
        """
        environ = request.environ
        environ['pylons.pylons'].translator = self
        environ['paste.registry'].replace(translator, self)

    def _load_domain(self, domain):
        """Load the given domain from one of the pre-configured locale dirs.

        Returns a :class:`gettext.NullTranslations` instance if no
        translations could be found for a non-critical domain. This
        allows untranslated plugins to be rendered in English instead
        of an error being raised.

        :param domain: A domain name.
        :rtype: :class:`gettext.GNUTranslations`
        :returns: The native python translator instance for this domain.
        :raises LanguageError: If no translations could be found for this
            locale in the 'mediacore' domain.
        """
        localedir = self._locale_dirs.get(domain, None)
        if not localedir:
            raise DomainError('No localedir specified for domain %r' % domain)
        try:
            t = gettext_translation(domain, localedir, self._languages)
        except IOError:
            msg = 'No %r translations found for %r at %r.' % \
                (domain, self._languages, localedir)
            if self._languages[0] == 'en':
                t = NullTranslations()
            elif domain != 'mediacore':
                # This is a non-critical domain so we don't care if it can't
                # be translated.
                t = NullTranslations()
                log.warn(msg)
            else:
                raise LanguageError(msg)
        self._domains[domain] = t
        return t

    def gettext(self, msgid, domain=None):
        """Get the translated string for this msgid in the given domain.

        :type msgid: ``str``
        :param msgid: A byte string to retrieve translations for.
        :type domain: ``str``
        :param domain: An optional domain to use, if not 'mediacore'.
        :rtype: ``unicode``
        :returns: The translated string, or the original msgid if no
            translation was found.
        """
        if not msgid:
            return u''
        if domain is None:
            domain = getattr(msgid, 'domain', 'mediacore')
        try:
            t = self._domains[domain]
        except KeyError:
            t = self._load_domain(domain)
        return t.ugettext(msgid)

    def ngettext(self, singular, plural, n, domain=None):
        """Get the translated string for this msgid in the given domain.

        :type singular: ``str``
        :param singular: A byte string msgid for the singular form.
        :type plural: ``str``
        :param plural: A byte string msgid for the plural form.
        :type n: ``int``
        :param n: The number of items.
        :type domain: ``str``
        :param domain: An optional domain to use, if not 'mediacore'.
        :rtype: ``unicode``
        :returns: The translated string, or the original msgid if no
            translation was found.
        """
        if domain is None:
            domain = getattr(singular, 'domain', 'mediacore')
        try:
            t = self._domains[domain]
        except KeyError:
            t = self._load_domain(domain)
        return t.ungettext(singular, plural, n)

    def dgettext(self, domain, msgid):
        """Alternate syntax needed for :module:`genshi.filters.i18n`."""
        return self.gettext(msgid, domain=domain)

    def dngettext(self, domain, singular, plural, n):
        """Alternate syntax needed for :module:`genshi.filters.i18n`."""
        return self.ngettext(singular, plural, n, domain=domain)

    # We always return unicode so these can be simple aliases
    ugettext = gettext
    ungettext = ngettext
    dugettext = dgettext
    dungettext = dngettext


def gettext(msgid, domain=None):
    return translator.gettext(msgid, domain)
_ = ugettext = gettext

def ngettext(singular, plural, n, domain=None):
    return translator.ngettext(singular, plural, n, domain)


class TranslateableUnicode(unicode):
    """A special string that remembers what domain it belongs to."""
    __slots__ = ('domain',)

def gettext_noop(msgid, domain=None):
    """Mark the given msgid for later translation.

    Ordinarily this simply returns the original msgid unaltered. Babel's
    message extractors recognize the form ``N_('xyz')`` and include 'xyz'
    in the POT file so that it can be ready for translation when it is
    finally passed through :func:`gettext`.

    If the domain name is given, a slightly altered string is returned:
    a special unicode string stores the domain stored as a property. The
    domain is then retrieved by :func:`gettext` when translation occurs,
    ensuring the translation comes from the correct domain.

    """
    if domain is not None:
        msgid = TranslateableUnicode(msgid)
        msgid.domain = domain
    return msgid
N_ = gettext_noop


# Lazy functions that evaluate when cast to unicode or str.
# These are not to be confused with N_ which returns the msgid unmodified.
# AFAIK these aren't currently in use and may be removed.
lazy_gettext = lazy_ugettext = lazify(gettext)
lazy_ngettext = lazy_ungettext = lazify(ngettext)

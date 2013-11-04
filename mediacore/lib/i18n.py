# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import os

from gettext import NullTranslations, translation as gettext_translation

from babel.core import Locale
from babel.dates import (format_date as _format_date,
    format_datetime as _format_datetime, format_time as _format_time)
from babel.numbers import format_decimal as _format_decimal
from babel.util import LOCALTZ
from pylons import config, request, translator
from pylons.i18n.translation import lazify


__all__ = ['_', 'N_', 'format_date', 'format_datetime', 'format_decimal',
    'format_time']

log = logging.getLogger(__name__)

MEDIACORE = 'mediacore'
"""The primary MediaDrop domain name."""

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

        :type locale: :class:`babel.Locale` or ``str``.
        :param locale: The locale to load translations for.
        :type locale_dirs: dict
        :param locale_dirs: A mapping of translation domain names to the
            localedir where they can be found. See :func:`gettext.translation`
            for more details.
        :raises DomainError: If no locale dir has been configured for this
            domain and the fallback is off.
        :raises LanguageError: If no translations could be found for this
            locale in the 'mediacore' domain and the fallback is off.
        """
        self.locale = locale = Locale.parse(locale)

        # Save configuration required for loading translations
        self._locale_dirs = locale_dirs

        # If the locale is pt_BR, look for both pt_BR and pt translations
        self._languages = [str(locale)]
        if locale.territory:
            self._languages.append(locale.language)

        # Storage for all message catalogs keyed by their domain name
        self._domains = {}

        # Fetch the mediacore domain immediately & cache a direct ref for perf
        self._mediacore = self._load_domain(MEDIACORE)

    def install_pylons_global(self):
        """Replace the current pylons.translator SOP with this instance.

        This is specific to the current request.
        """
        environ = request.environ
        environ['pylons.pylons'].translator = self
        environ['paste.registry'].replace(translator, self)

    def _load_domain(self, domain, fallback=True):
        """Load the given domain from one of the pre-configured locale dirs.

        Returns a :class:`gettext.NullTranslations` instance if no
        translations could be found for a non-critical domain. This
        allows untranslated plugins to be rendered in English instead
        of an error being raised.

        :param domain: A domain name.
        :param fallback: An optional flag that, when True, returns a
            :class:`gettext.NullTranslations` instance if no translations
            file could be found for the given language(s).
        :rtype: :class:`gettext.GNUTranslations`
        :returns: The native python translator instance for this domain.
        :raises DomainError: If no locale dir has been configured for this
            domain and the fallback is off.
        :raises LanguageError: If no translations could be found for this
            domain in this locale and the fallback is off.
        """
        localedir = self._locale_dirs.get(domain, None)
        if localedir:
            try:
                t = gettext_translation(domain, localedir, self._languages,
                                        fallback=fallback)
            except IOError:
                # This only occurs when fallback is false.
                msg = 'No %r translations found for %r at %r.' % \
                    (domain, self._languages, localedir)
                raise LanguageError(msg)
        elif fallback:
            t = NullTranslations()
        else:
            raise DomainError('No localedir specified for domain %r' % domain)
        self._domains[domain] = t
        return t

    def gettext(self, msgid, domain=None):
        """Translate the given msgid in this translator's locale.

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
        if domain is None and isinstance(msgid, _TranslateableUnicode):
            domain = msgid.domain
        if domain is None or domain == MEDIACORE:
            t = self._mediacore
        else:
            try:
                t = self._domains[domain]
            except KeyError:
                t = self._load_domain(domain)
        return t.ugettext(msgid)

    def ngettext(self, singular, plural, n, domain=None):
        """Pluralize the given number in this translator's locale.

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
        if domain is None or domain == MEDIACORE:
            t = self._mediacore
        else:
            try:
                t = self._domains[domain]
            except KeyError:
                t = self._load_domain(domain)
        return t.ungettext(singular, plural, n)

    def dgettext(self, domain, msgid):
        """Alternate syntax needed for :module:`genshi.filters.i18n`.

        This is only called when the ``i18n:domain`` directive is used."""
        return self.gettext(msgid, domain)

    def dngettext(self, domain, singular, plural, n):
        """Alternate syntax needed for :module:`genshi.filters.i18n`.

        This is only called when the ``i18n:domain`` directive is used."""
        return self.ngettext(singular, plural, n, domain)

    # We always return unicode so these can be simple aliases
    ugettext = gettext
    ungettext = ngettext
    dugettext = dgettext
    dungettext = dngettext


def gettext(msgid, domain=None):
    """Get the translated string for this msgid in the given domain.

    :type msgid: ``str``
    :param msgid: A byte string to retrieve translations for.
    :type domain: ``str``
    :param domain: An optional domain to use, if not 'mediacore'.
    :rtype: ``unicode``
    :returns: The translated string, or the original msgid if no
        translation was found.
    """
    translator_obj = translator._current_obj()
    if not isinstance(translator_obj, Translator):
        if config['debug']:
            log.warn('_, ugettext, or gettext called with msgid "%s" before '\
                     'pylons.translator has been replaced with our custom '\
                     'version.' % msgid)
        return translator_obj.gettext(msgid)
    return translator_obj.gettext(msgid, domain)
_ = ugettext = gettext

def ngettext(singular, plural, n, domain=None):
    """Pluralize the given number using the current translator.

    This uses the ``pylons.translator`` SOP to access the translator
    appropriate for the current request.

    :type singular: ``str``
    :param singular: A byte string msgid for the singular form.
    :type plural: ``str``
    :param plural: A byte string msgid for the plural form.
    :type n: ``int``
    :param n: The number of items.
    :type domain: ``str``
    :param domain: An optional domain to use, if not 'mediacore'.
    :rtype: ``unicode``
    :returns: The pluralized translation.
    """
    return translator.ngettext(singular, plural, n, domain)

class _TranslateableUnicode(unicode):
    """A special string that remembers what domain it belongs to.

    This class should not be constructed directly, use :func:`N_` instead.
    If you do choose to call this class directly, be sure the domain
    attribute is set, as the :class:`Translator` assumes it is defined
    for performance reasons.

    """
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
        msgid = _TranslateableUnicode(msgid)
        msgid.domain = domain
    return msgid
N_ = gettext_noop

# Lazy functions that evaluate when cast to unicode or str.
# These are not to be confused with N_ which returns the msgid unmodified.
# AFAIK these aren't currently in use and may be removed.
lazy_gettext = lazy_ugettext = lazify(gettext)
lazy_ngettext = lazy_ungettext = lazify(ngettext)


def format_date(date=None, format='medium'):
    """Return a date formatted according to the given pattern.

    This uses the locale of the current request's ``pylons.translator``.

    :param date: the ``date`` or ``datetime`` object; if `None`, the current
                 date is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :rtype: `unicode`
    """
    return _format_date(date, format, translator.locale)

def format_datetime(datetime=None, format='medium', tzinfo=None):
    """Return a date formatted according to the given pattern.

    This uses the locale of the current request's ``pylons.translator``.

    :param datetime: the `datetime` object; if `None`, the current date and
                     time is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :param tzinfo: the timezone to apply to the time for display
    :rtype: `unicode`
    """
    if datetime and (datetime.tzinfo is None):
        datetime = datetime.replace(tzinfo=LOCALTZ)
    return _format_datetime(datetime, format, tzinfo, translator.locale)

def format_decimal(number):
    """Return a formatted number (using the correct decimal mark).

    This uses the locale of the current request's ``pylons.translator``.

    :param number: the ``int``, ``float`` or ``decimal`` object
    :rtype: `unicode`
    """
    return _format_decimal(number, locale=translator.locale)

def format_time(time=None, format='medium', tzinfo=None):
    """Return a time formatted according to the given pattern.

    This uses the locale of the current request's ``pylons.translator``.

    :param time: the ``time`` or ``datetime`` object; if `None`, the current
                 time in UTC is used
    :param format: one of "full", "long", "medium", or "short", or a custom
                   date/time pattern
    :param tzinfo: the time-zone to apply to the time for display
    :rtype: `unicode`
    """
    if time and (time.tzinfo is None):
        time = time.replace(tzinfo=LOCALTZ)
    return _format_time(time, format, tzinfo, translator.locale)

def get_available_locales():
    """Yield all the locale names for which we have translations.

    Considers only the 'mediacore' domain, not plugins.
    """
    i18n_dir = os.path.join(config['pylons.paths']['root'], 'i18n')
    for name in os.listdir(i18n_dir):
        mo_path = os.path.join(i18n_dir, name, 'LC_MESSAGES/mediacore.mo')
        if os.path.exists(mo_path):
            yield name

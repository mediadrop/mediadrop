#!/usr/bin/env python
# encoding: utf-8

import re
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 6):
    print 'MediaDrop requires Python 2.6 or 2.7.'
    sys.exit(1)

from mediadrop import __version__ as VERSION

# setuptools' dependency resolution is often too simplistic. If we install
# MediaDrop into an existing virtualenv we often face the problem that
# setuptools does not upgrade the components (even though some dependencies
# like Pylons actually require a newer version). Therefore often we add a
# specific minimum version even though that's not really a requirement by
# MediaDrop (rather an a Pylons requirement).
setup_requires = [
    'PasteScript >= 1.7.4.2', # paster_plugins=
]

def requires_from_file(filename):
    requirements = []
    with open(filename, 'r') as requirements_fp:
        for line in requirements_fp.readlines():
            match = re.search('^\s*([a-zA-Z][^#]+?)(\s*#.+)?\n$', line)
            if match:
                requirements.append(match.group(1))
    return requirements

install_requires = setup_requires + requires_from_file('requirements.txt')
if sys.version_info < (2, 7):
    # importlib is included in Python 2.7
    # however we can't do try/import/except because this might generate eggs
    # with missing requires which can not be used in other environments
    # see https://github.com/mediadrop/mediadrop/pull/44#issuecomment-573242
    install_requires.extend(requires_from_file('requirements.py26.txt'))

extra_arguments_for_setup = {}

# extractors are declared separately so it is easier for 3rd party users
# to use them for other packages as well...
extractors = [
    ('lib/unidecode/**', 'ignore', None),
    ('tests/**', 'ignore', None),
    ('**.py', 'python', None),
    ('templates/**.html', 'genshi', {
            'template_class': 'genshi.template.markup:MarkupTemplate'
        }),
    ('public/**', 'ignore', None),
]
is_babel_available = True
try:
    import babel
except ImportError:
    is_babel_available = False
if is_babel_available:
    extra_arguments_for_setup['message_extractors'] = {'mediadrop': extractors}

setup(
    name='MediaDrop',
    version=VERSION,
    description='A audio, video and podcast publication platform.',
    author='MediaDrop contributors.',
    author_email='info@mediadrop.video',
    url='http://mediadrop.video',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: TurboGears :: Applications',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Multimedia :: Sound/Audio',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        ],

    setup_requires=setup_requires,
    install_requires=install_requires,
    paster_plugins=[
        'PasteScript',
        'Pylons',
    ],

    test_suite='mediadrop.lib.test.suite',

    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'mediadrop': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,

    entry_points="""
    [paste.app_factory]
    main = mediadrop.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,

    **extra_arguments_for_setup
)

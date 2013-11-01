try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys
from mediacore import __version__ as VERSION

# setuptools' dependency resolution is often too simplistic. If we install
# MediaDrop into an existing virtualenv we often face the problem that
# setuptools does not upgrade the components (even though some dependencies
# like Pylons actually require a newer version). Therefore often we add a
# specific minimum version even though that's not really a requirement by
# MediaDrop (rather an a Pylons requirement).
setup_requires = [
    'PasteScript >= 1.7.4.2', # paster_plugins=
]
install_requires = setup_requires + [
    'ddt',
    'formencode >= 1.2.4', # (version required by Pylons 1.0)
    'Pylons >= 1.0',
    # WebOb 1.2.x raises an error if we use "request.str_params" (as we did in
    # MediaDrop 0.10/WebOb 1.0.7) but the non-deprecated attribute was only
    # added in WebOb 1.1 so we need that as baseline.
    'WebOb >= 1.1',
    'WebHelpers == 1.0',
    # 0.7: event listener infrastructure, alembic 0.5 requires at least 0.7.3
    # we need to change our class_mappers for 0.8 support
    'SQLAlchemy >= 0.7.3, < 0.8',
    # theoretically every alembic since 0.4 should work (which added the 
    # alembic.config.Config class) but MediaDrop is only tested with 0.5+
    'alembic >= 0.4',
    'Genshi >= 0.6', # i18n improvements in Genshi
    'Babel >= 0.9.6',
    'Routes == 1.12.3',
    'repoze.who == 1.0.18',
    'repoze.who-friendlyform',
    'repoze.who.plugins.sa',
    'Paste >= 1.7.5.1', # (version required by Pylons 1.0)
    'PasteDeploy >= 1.5',  # (version required by Pylons 1.0)
    'ToscaWidgets >= 0.9.12', # 0.9.9 is not compatible with Pylons 1.0
    'tw.forms == 0.9.9',
    'MySQL-python >= 1.2.2',
    'BeautifulSoup == 3.0.7a',
        # We monkeypatch this version of BeautifulSoup in mediacore.__init__
        # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
    'Pillow',
    'akismet == 0.2.0',
    'gdata > 2, < 2.1',
    'unidecode',
    'decorator >= 3.3.2', # (version required by Pylons 1.0)
    'simplejson >= 2.2.1', # (version required by Pylons 1.0)
]

if sys.version_info < (2, 7):
    # importlib is included in Python 2.7
    # however we can't do try/import/except because this might generate eggs
    # with missing requires which can not be used in other environments
    # see https://github.com/mediadrop/mediadrop/pull/44#issuecomment-573242
    install_requires.append('importlib')

if sys.version_info < (2, 6):
    print 'MediaDrop requires Python 2.6 or 2.7.'
    sys.exit(1)

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
    extra_arguments_for_setup['message_extractors'] = {'mediacore': extractors}

setup(
    name='MediaDrop',
    version=VERSION,
    description='A audio, video and podcast publication platform.',
    author='MediaDrop contributors.',
    author_email='info@mediadrop.net',
    url='http://mediadrop.net',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: TurboGears :: Applications',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
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

    test_suite='mediacore.lib.test.suite',

    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'mediacore': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,

    entry_points="""
    [paste.app_factory]
    main = mediacore.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,

    **extra_arguments_for_setup
)

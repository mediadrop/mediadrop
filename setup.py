try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys
from mediacore import __version__ as VERSION

install_requires = [
    'WebTest == 1.2',
    'Pylons == 0.10',
    'WebOb == 1.0.7',
    'WebHelpers == 1.0',
    # 0.7: event listener infrastructure
    # migrate does not yet support 0.8
    'SQLAlchemy >= 0.7, < 0.8',
    'sqlalchemy-migrate >= 0.7', # 0.6 is not compatible with SQLAlchemy >= 0.7
    'Genshi >= 0.6', # i18n improvements in Genshi
    'Babel == 0.9.6',
    'Routes == 1.12.3',
    'repoze.who == 1.0.18',
    'repoze.who-friendlyform',
    'repoze.who.plugins.sa',
    'Paste == 1.7.4',
    'PasteDeploy == 1.3.3',
    'PasteScript == 1.7.3',
    'ToscaWidgets == 0.9.9',
    'tw.forms == 0.9.9',
    'MySQL-python >= 1.2.2',
    'BeautifulSoup == 3.0.7a',
        # We monkeypatch this version of BeautifulSoup in mediacore.__init__
        # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
    'Pillow',
    'akismet == 0.2.0',
    'gdata > 2, < 2.1',
    'unidecode',
    'decorator',
    'simplejson',
]

if sys.version_info < (2, 7):
    # importlib is included in Python 2.7
    # however we can't do try/import/except because this might generate eggs
    # with missing requires which can not be used in other environments
    # see https://github.com/mediadrop/mediadrop/pull/44#issuecomment-573242
    install_requires.append('importlib')

if sys.version_info < (2, 5):
    # These package comes bundled in Python >= 2.5 as xml.etree.cElementTree.
    install_requires.append('elementtree >= 1.2.6, < 1.3')
    install_requires.append('cElementTree >= 1.0.5, < 1.1')

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
extra_arguments_for_setup['message_extractors'] = {'mediacore': extractors}

setup(
    name='MediaCore',
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

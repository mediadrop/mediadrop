import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from mediacore import __version__ as VERSION

install_requires = [
    'WebTest == 1.2',
    'Pylons == 0.10',
    'WebHelpers == 1.0',
    'SQLAlchemy >= 0.6.1',
    'sqlalchemy-migrate >= 0.6dev',
    'Genshi >= 0.5.1',
    'Routes == 1.12',
    'repoze.who == 1.0.18',
    'repoze.what-pylons == 1.0',
    'repoze.what-quickstart',
    'Paste == 1.7.4',
    'PasteDeploy == 1.3.3',
    'PasteScript == 1.7.3',
    'ToscaWidgets == 0.9.9',
    'tw.forms == 0.9.9',
    'MySQL-python >= 1.2.2',
    'BeautifulSoup == 3.0.7a',
        # We monkeypatch this version of BeautifulSoup in mediacore.__init__
        # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
    'akismet == 0.2.0',
    'feedparser >= 4.1', # needed only for rss import script
]

# PIL has some weird packaging issues (because its been around forever).
# If PIL is installed via MacPorts, setuptools tries to install again.
# The original PIL 1.1.6 package won't install via setuptools so this
# this setup script will install http://dist.repoze.org/PIL-1.1.6.tar.gz
try:
    import PIL
except ImportError:
    install_requires.append('PIL >= 1.1.6')

extra_arguments_for_setup = {}
# optional dependency on babel - if it is not installed, you can not extract
# new messages but MediaCore itself will still work...
try:
    import babel
    # extractors are declared separately so it is easier for 3rd party users
    # to use them for other packages as well...
    extractors = [
        ('**.py',             'python', None),
        ('templates/**.html', 'genshi', None),
        ('public/**',         'ignore', None),
    ]
    extra_arguments_for_setup['message_extractors'] = {'mediacore': extractors}
except ImportError:
    pass

# Path to the local copy of SQLAlchemy-Migrate-0.6.dev.
# We need this version for SQLAlchemy 0.6.x support, and it isn't on PyPi yet.
local_dependency_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'dependencies',
)

setup(
    name='MediaCore',
    version=VERSION,
    description='A audio, video and podcast publication platform.',
    author='Simple Station Inc.',
    author_email='info@simplestation.com',
    url='http://getmediacore.com/',
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

    test_suite='nose.collector',
    tests_require=[
        'WebTest',
        ],

    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'mediacore': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,
    dependency_links=[
        local_dependency_dir
    ],

    entry_points="""
    [paste.app_factory]
    main = mediacore.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,

    **extra_arguments_for_setup
)

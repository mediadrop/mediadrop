try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from mediacore import __version__ as VERSION

install_requires = [
    'Pylons == 0.10rc1',
    'SQLAlchemy == 0.5.8',
    'Genshi == 0.5.1',
    'Routes == 1.12',
    'repoze.who == 1.0.18',
    'repoze.what-pylons == 1.0',
    'repoze.what-quickstart',
    'repoze.tm2 == 1.0a5',
    'ToscaWidgets == 0.9.9',
    'tw.dynforms',
    'zope.sqlalchemy == 0.4',
    'MySQL-python >= 1.2.2',
    'BeautifulSoup == 3.0.7a',
        # We monkeypatch this version of BeautifulSoup in mediacore.__init__
        # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
    'akismet',
]

# PIL has some weird packaging issues (because its been around forever).
# If PIL is installed via MacPorts, setuptools tries to install again.
# The original PIL 1.1.6 package won't install via setuptools so this
# this setup script will install http://dist.repoze.org/PIL-1.1.6.tar.gz
try:
    import PIL
except ImportError:
    install_requires.append('PIL >= 1.1.6')

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
    setup_requires=[
        'PasteScript >= 1.6.3'
    ],
    paster_plugins=[
        'PasteScript',
        'Pylons',
    ],

    test_suite='nose.collector',
    tests_require=[
        'WebTest',
        'BeautifulSoup',
        ],

    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'mediacore': ['i18n/*/LC_MESSAGES/*.mo']},
    # message_extractors = {'mediacore': [
    #    ('**.py', 'python', None),
    #    ('templates/**.html', 'genshi', None),
    #    ('public/**', 'ignore', None)]},
    zip_safe=False,

    entry_points="""
    [paste.app_factory]
    main = mediacore.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)

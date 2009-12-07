try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from mediacore import __version__ as VERSION

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

    install_requires=[
        # FIXME: Change to 2.0.4 when its out, right now we require a customized version
        'TurboGears2',
        'ToscaWidgets >= 0.9.1',
        'tw.dynforms',
        'zope.sqlalchemy',
        'sqlalchemy >= 0.5.2',
        'repoze.what-quickstart',
        'PIL >= 1.1.6',
        'MySQL-python >= 1.2.2',
        'BeautifulSoup == 3.0.7a',
            # We monkeypatch this version of BeautifulSoup in mediacore.__init__
            # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
        ],
    setup_requires=[
        'PasteScript >= 1.6.3'
        ],
    paster_plugins=[
        'PasteScript',
        'Pylons',
        'TurboGears2',
        ],

    test_suite='nose.collector',
    tests_require=[
        'WebTest',
        'BeautifulSoup',
        ],

    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'mediacore': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors = {'mediacore': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = mediacore.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)

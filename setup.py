try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from simpleplex import __version__ as VERSION

setup(
    name='Simpleplex',
    version=VERSION,
    description='Simpleplex is a media-oriented content manager.',
    author='Simplestation Inc.',
    author_email='info@simplestation.com',
    url='http://simplestation.com/',

    install_requires=[
        "TurboGears2",
        "ToscaWidgets >= 0.9.1",
        "tw.dynforms",
        "zope.sqlalchemy",
        "sqlalchemy >= 0.5.2",
        "repoze.what-quickstart",
        "BeautifulSoup == 3.0.7a",
            # We monkeypatch this version of BeautifulSoup in simpleplex.__init__
            # Patch pending: https://bugs.launchpad.net/beautifulsoup/+bug/397997
        "PIL",
        ],
    setup_requires=[
        "PasteScript >= 1.6.3"
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
    package_data={'simpleplex': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors = {'simpleplex': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = simpleplex.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)

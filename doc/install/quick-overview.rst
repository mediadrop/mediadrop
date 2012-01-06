.. _install_overview:

===========================
Quick Installation Overview
===========================

If you're already familiar with installing Pylons apps, here's a
six-step run-down of how to install MediaCore CE.

If you're not already familiar with the process, head to the main
:ref:`install_toplevel` page for a more detailed description of the process.

1. Create and activate a new ``virtualenv``.
2. Run ``python setup.py develop`` to install MediaCore CE and its
   dependencies.
3. For production, run ``paster make-config mediacore deployment.ini``
   and to create a unique ``deployment.ini`` config. On development
   machines there's already a ``development.ini`` file for you to use.
4. Configure your database credentials in the ini config file.
5. Run ``paster setup-app path/to/your/config.ini`` to set up the database
   tables and data.
6. Run ``paster serve path/to/your/config.ini`` and test it out!



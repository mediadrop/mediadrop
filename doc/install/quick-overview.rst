:orphan:

.. _install_overview:

===========================
Quick Installation Overview
===========================

If you're already familiar with installing Pylons apps, here's a
quick run-down of how to install MediaDrop.

If you're not already familiar with the process, head to the main
:ref:`install_toplevel` page for a more detailed description of the process.

#. Ensure that you have development headers for MySQL, libjpeg, zlib, 
   freetype, and Python installed.
#. Create and activate a new ``virtualenv``.
#. Run ``python setup.py develop`` to install MediaDrop and its
   dependencies.
#. For production, run ``paster make-config mediacore deployment.ini``
   and to create a unique ``deployment.ini`` config. On development
   machines there's already a ``development.ini`` file for you to use.
#. Configure your database credentials in the ini config file.
#. Run ``paster setup-app path/to/your/config.ini`` to set up the database
   tables and data.
#. Run ``paster serve path/to/your/config.ini`` and test it out!



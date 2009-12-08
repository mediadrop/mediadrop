.. _dev_contributing:

=========================
Contributing to MediaCore
=========================

We'd be very grateful for any 

Documentation
-------------

We use `Sphinx <http://sphinx.pocoo.org/>`_ for our building our documentation,
which expands on the generic format
`reStructuredText <http://en.wikipedia.org/wiki/ReStructuredText>`_.

To build the documentation you must have Sphinx and Pygments installed. They
were probably installed when you first installed MediaCore, but just in case,
here's how to install them. (This example assumes that you're using a
``virtualenv`` called ``mediacore_env``, as outlined in the :ref:`install
instructions <install_toplevel>`.)

.. sourcecode:: bash

   $ source mediacore_env/bin/activate
   $ easy_install Sphinx
   $ easy_install Pigments
   $ cd doc
   $ make html

Reporting Bugs & Submitting Patches
-----------------------------------

Please post issues to our `tracker on Github
<http://github.com/simplestation/mediacore/issues>`_.


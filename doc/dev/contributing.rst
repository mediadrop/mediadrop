.. _dev_contributing:

==========================
Contributing to Simpleplex
==========================

Documentation
-------------

We use `Sphinx <http://sphinx.pocoo.org/>`_ for our building our documentation,
which expands on the generic format
`reStructuredText <http://en.wikipedia.org/wiki/ReStructuredText>`_.

To build the documentation you must have Sphinx and Pygments installed. They
were probably installed when you first installed Simpleplex, but just in case,
here's how to install them. (This example assumes that you're using a
``virtualenv`` called ``simpleplex_env``, as outlined in the :ref:`install
instructions <install>`.)

.. sourcecode:: bash

   $ source simpleplex_env/bin/activate
   $ easy_install Sphinx
   $ easy_install Pigments
   $ cd simpleplex/doc
   $ make html

If you get an exception ``DistributionNotFound: Simpleplex``, try putting the
root simpleplex folder (the one with Simpleplex.EGG-INFO in it) on your
:envvar:`PYTHONPATH`. (I'm really not sure why I had to do this to get it
working, there's a ``Simpleplex.egg-link`` file in my virtualenv site-packages
folder which points here so I would expect it to be able to find it, but it
can't. Hopefully someone else will have some insight.)

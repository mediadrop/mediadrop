.. _dev_contributing:

============================
Contributing to MediaDrop
============================

Reporting Bugs
--------------

The simplest way to give back to MediaDrop is to report bugs as you find
them!

Please post issues to our `issue tracker on Github
<https://github.com/mediadrop/mediadrop/issues>`_.

You can always post to our `community forums <http://mediadrop.net/community/>`_ if you aren't sure if its a bug or
not.


Coding Conventions
------------------

We follow `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_, which is
practically universal in the Python world. The only exception is that
templates and javascript need not obey the 79 char line limit. Also,
please be sure to use unix line endings.


Documentation
-------------

We use `Sphinx <http://sphinx.pocoo.org/>`_ for our building our documentation,
which is an extension of
`reStructuredText <http://en.wikipedia.org/wiki/ReStructuredText>`_.

To build the documentation you must have Sphinx and Pygments installed. They
were probably installed when you first installed MediaDrop, but just in case,
here's how to install them. (This example assumes that you're using a
``virtualenv`` called ``mediadrop_env``, as outlined in the :ref:`install
instructions <install_toplevel>`.)

.. sourcecode:: bash

    # As always, don't forget to work in your virtualenv
    $ source mediadrop_env/bin/activate
    $ easy_install Sphinx Pygments

    # Build the HTML docs with sphinx
    $ cd doc
    $ make html

Patches to the documentation can be submitted in the same way as
patches to code, discussed below.


Submitting Patches
------------------

Generally we request that you create an issue in our `issue tracker
<https://github.com/mediadrop/mediadrop/issues>`_ for any patch
you'd like to submit. It helps us stay organized in the long run.

Our Git repository is hosted over at `Github <http://github.com/>`_ and
one of their handy features is forking. This perfect for submitting
large features, or anything with two or more people working on it.
There is an `excellent tutorial <http://help.github.com/forking/>`_
on their site, so we won't explain it here. Pull requests can be sent to
Nathan Wright.

We'll explain how to do this if you've cloned our public Git repository
on your local machine, without using Github forking. This is perfect for
bugfixes and smaller features, where only one person is working on it.

.. sourcecode:: bash

    # Getting a copy of our git repository (if you haven't already):
    $ git clone git://github.com/mediadrop/mediadrop.git

    # Create a new branch and switch to it:
    $ git checkout -b your_local_branch

Make your changes and commit them. Once that's done, you're ready to
create a patch for submission:

.. sourcecode:: bash

    # Make sure you have the latest changes from our repository
    $ git fetch

    # Move your branch on top of our latest changes
    $ git rebase origin/master

    # This creates a file your_patch from the commits in your_local_branch
    $ git format-patch --stdout origin/master.. > your_patch

Attach the ``your_patch`` file to an `issue
<https://github.com/mediadrop/mediadrop/issues>`_ describing the
problem and the fix.


Helpful Resources
-----------------

Git can be a bit overwhelming at first but you'll grow to love it.

* `Rails Contributor Guide
  <https://rails.lighthouseapp.com/projects/8994/sending-patches>`_:
  the principles are exactly the same.
* `Sourcemage Git FAQ <http://www.sourcemage.org/Git_Guide>`_:
  solutions for many common problems.
* `Git Community Book <http://book.git-scm.com/>`_.


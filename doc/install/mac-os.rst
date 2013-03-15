:orphan:

Mac OS X
----------------------------------------------

Installing MediaCore CE on a Mac is a bit more complicated than doing so on 
Linux because Mac OS does not come with all the required packages. However once
it is working you can run MediaCore on Mac just fine.

The following documentation was tested with a client version of Mac OS X 10.8 
(Mountain Lion). 

Please note: I'm not a Mac user myself so I'd be glad to improve this section
based on your input (e.g. other Mac OS versions, installation on Mac OS server 
edition, alternate install methods).


Compiler and System libraries
""""""""""""""""""""""""""""""""""""""""

First you need to install `Xcode <https://developer.apple.com/xcode/>`_ and
its "Command Line Tools" (Xcode – Preferences – Downloads) so you have a working
compiler.

There are different ways of installing the necessary system libraries. The 
following section uses `Homebrew <http://mxcl.github.com/homebrew/>`_ but of 
course other tools like `MacPorts <http://www.macports.org>`_ should work as 
well.

After you installed Homebrew (check their website for details) you can install
the missing imaging library:

.. sourcecode:: bash

    brew install libjpeg


MySQL
""""""""""""""""""""""""""""""""""""""""

Mac OS X server comes with a bundled MySQL server which you can use. However
you need at least the MySQL client library and the matching development header
files. In Homebrew these are all in one package but of course you don't have
to use their MySQL server if you already have one.

.. sourcecode:: bash

    brew install mysql


Python libraries and tools
""""""""""""""""""""""""""""""""""""""""

Before installing MediaCore you need also virtualenv. For the sake of 
simplicity we use a slightly insecure way of installing virtualenv as the 
install process doesn't use SSL. Of course there are other ways, the only 
important end-result is that you can create a working virtualenv.

.. sourcecode:: bash

    curl https://raw.github.com/pypa/virtualenv/1.9.1/virtualenv.py --output virtualenv.py

To create the virtualenv (see :ref:`install_setup_virtualenv`) please use this 
command instead:

.. sourcecode:: bash

    python virtualenv.py --distribute venv


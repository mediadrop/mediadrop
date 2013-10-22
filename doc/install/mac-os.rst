Mac OS X
----------------------------------------------

Installing MediaDrop on a Mac is a bit more complicated than doing so on 
Linux because Mac OS does not come with all the required packages. However once
it is working you can run MediaDrop on Mac just fine.

The following documentation was tested with a client version of Mac OS X 10.8 
(Mountain Lion). 

Please note: I'm not a Mac user myself so I'd be glad to improve this section
based on your input (e.g. other Mac OS versions, installation on Mac OS server 
edition, alternate install methods).


Compiler, Python, and System libraries
""""""""""""""""""""""""""""""""""""""""

First you need to install `Xcode <https://developer.apple.com/xcode/>`_ and
its "Command Line Tools" (Xcode – Preferences – Downloads) so you have a working
compiler. You can check your system by using the which command:

.. sourcecode:: bash

    which cc

This checks to see if we have the compiler ready. No output after hitting return 
means it's not installed; output indicates that it is installed and tells us 
exactly where it is in our system.

Now that you've got XCode installed, we need to set up Python. Every Mac does come
with an Apple-provided system version, but it is safest and best practice to not
use this and instead install a fresh version. There are a few ways of doing this, but
for our purposes it is best to do so with Homebrew.

Install `Homebrew <http://mxcl.github.com/homebrew/>`_ by following the instructions
on the website. Please note that you can use other such tools such as MacPorts, but
Homebrew is highly recommended for its interactive help. If you already have MacPorts 
installed (if it's new to you, then you probably don't), Homebrew will indicate to 
you that you need to delete MacPorts, and even provide the necessary command to 
execute.

Let's get a new fresh version of Python:

.. sourcecode:: bash

    brew install python

After this install occurs it's best if we grab the location of this new python so we
can be assured that we use it for the remainder of this tutorial:

.. sourcecode:: bash

    BREWPYTHON=`brew ls python | grep 'python$' | grep -v 'Frameworks' | sed 's/\/python$//'`

This above command looks convoluted but all it does is set the variable "BREWPYTHON" to the 
location of brew's python, which we'll use in the following section.

Now that we have Xcode and Python installed, now we need to get the necessary system libraries:

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

As with all brew commands, it print out some useful information that we may need
to get the installed software to work as expected. MediaDrop will actually need the
MySQL server running, which brew doesn't do for you, but it does tell you how:

.. sourcecode:: bash

    mysql.server start


Python libraries and tools
""""""""""""""""""""""""""""""""""""""""

Before installing MediaDrop we also need virtualenv. Virtualenv will manage any
future software that MediaDrop needs to ensure that it does not conflict with any 
other software, similar to sandboxing. Since we used Homebrew to install our Python,
and remembering have we've set up the variable "BREWPYTHON", we can do this:

.. sourcecode:: bash

  $BREWPYTHON/pip install virtualenv

Now we need to create a "virtual environment" (see :ref:`install_setup_virtualenv`) 
with the following command:

.. sourcecode:: bash

    /usr/local/share/python/virtualenv --no-site-packages  /path/to/venv

Finally, we can activate this virtual environment, which we'll have to do when we're
working with MediaDrop, with the following command:

.. sourcecode:: bash

    source /path/to/venv/bin/activate

The command line prompt will change to indicate that you are now within a virtual
environment, and you can continue the installation process.


.. _dev_closure:

=========================================
Javascript Development with Closure Tools
=========================================

This is an introductory guide to developing and building Javascript for
MediaDrop.

Beginning with v0.9, all new javascript development will be based on `Closure
Tools` instead of the Mootools framework.  Currently we're using two main
components of Closure Tools:

.. glossary::

   Closure Library
      "The `Closure Library <http://code.google.com/p/closure-library/>`_ is a
      broad, well-tested, modular, and cross-browser JavaScript library. You
      can pull just what you need from a large set of reusable UI widgets and
      controls, and from lower-level utilities for DOM manipulation, server
      communication, animation, data structures, unit testing, rich-text
      editing, and more."

   Closure Compiler
      "The `Closure Compiler <http://code.google.com/p/closure-library/>`_ is
      a tool for making JavaScript download and run faster. It is a true
      compiler for JavaScript. Instead of compiling from a source language
      to machine code, it compiles from JavaScript to better JavaScript. It
      parses your JavaScript, analyzes it, removes dead code and rewrites and
      minimizes what's left. It also checks syntax, variable references, and
      types, and warns about common JavaScript pitfalls."


Getting Closure Tools
---------------------

First off, you'll need to get Closure Library.  Checkout the official SVN
repository into your root MediaDrop directory:

.. sourcecode:: bash

    $ cd MediaDrop
    $ svn checkout http://closure-library.googlecode.com/svn/trunk/ closure-library

Next, you'll need to `download the latest version of Closure Compiler
<http://closure-compiler.googlecode.com/files/compiler-latest.tar.gz>`_ and
extract it into place:

.. sourcecode:: bash

    cd batch-scripts/closure/compiler
    wget http://closure-compiler.googlecode.com/files/compiler-latest.tar.gz
    tar -xzvf compiler-latest.tar.gz

.. note::

    The shell scripts detailed below require the library and compiler
    to be accessible at these locations.  If you'd like to store them
    elsewhere, you'll have to edit ``mediacore/config/middleware.py`` and
    the shell scripts at ``batch-scripts/closure/``.


Development Workflow
--------------------

Ordinarily all MediaDrop javascript that is loaded is pre-compiled.  This is
ideal for file size and run-time performance on the client, but as a side
effect, it obfuscates the code.  This makes it extremely difficult to trace
compiled code, so it's important for developers to be able to run the
uncompiled source code when necessary.

MediaDrop comes with a javascript debug mode built-in.  When enabled, all
javascript is loaded in its original source form.  Simply append
``?debug=true`` to any URL to enable debug mode for that request.

It's important to compile your code regularly throughout your development
process.  The compiler is capable of quickly finding many bugs in your code
and it often provides more precise error messages than a browser might.  Don't
think of it as a white-space remover: it's a very useful tool and you should
run it regularly.

Compiling your code can sometimes introduce bugs that aren't present in
uncompiled code.  This is because the compiler imposes certain restrictions on
your Javascript.  You should familiarize yourself with `the optimizations
the compiler makes
<http://code.google.com/closure/compiler/docs/api-tutorial3.html>`_
and their ramifications.


Working in Debug Mode
---------------------

MediaDrop contains a special debug mode which triggers uncompiled source files
be loaded instead of a single pre-compiled and obfuscated file.  Enable it by
appending ``?debug=true`` to any MediaDrop URL.

In debug mode, there are three files that are initially loaded.  Any additional
files that they depend on are loaded at run time, which we'll explain in more
detail below.

The initial files are:

.. glossary::

   ``goog/base.js``
      This is the core of Closure Library.  Among other things, it defines the
      dependency management functions ``goog.require()`` and ``goog.provide()``.

   ``mcore/deps.js``
      This file is auto-generated and informs the dependency manager in what
      files dependencies can be found.  This allows the correct script file to
      be loaded when one of your source files calls
      ``goog.require('mcore.players.Html5Player');`` (which
      happens to be mcore/players/html5.js in this example).

   ``mcore/base.js``
      This file contains our actual application code.  It exposes the API that
      you can call from within the page as needed.  It can depend on other
      javascript files which will be loaded at run-time when in debug mode.


Additional dependencies are loaded dynamically thanks to these two core
functions:

.. glossary::

   ``goog.provide(string name)``
      Indicate that the file which makes this call defines the given name.
      This does not actually do anything at run time, but is parsed by the
      build script that generates ``mcore/deps.js``.  (It is also parsed by
      the compiler build script.)

   ``goog.require(string name)``
      Load the file which has indicated it provides the given name.  In debug
      mode this creates a new <script> tag which points to the correct source
      file, as defined by ``goog/deps.js`` or ``mcore/deps.js``.


The build script that generates ``mcore/deps.js`` should be run any time you
add, modify or move a ``goog.provide()`` call. Do so by running this shell
script:

.. sourcecode:: bash

   $ batch-scripts/closure/writedeps.sh

.. note(nate): incorporate this somehow:
   -This debug mode can only be enabled if DEBUG is enabled in your INI
    config file.
   -If you installed closure-library while the server was running,
    you'll have to restart the server to enable static file serving
    of Closure Library source code.
   -goog.require() doesn't do anything until the current script finishes
    executing


Compiling Your Javascript
-------------------------

MediaDrop and Closure Library both share a very verbose coding style that spans
a large number of source files; Closure Compiler concatenates all relevant
source files, strips out dead code and optimizes everything that remains.

MediaDrop makes use of the most advanced optimizations offered by the compiler,
which imposes some `restrictions that you should be aware of
<http://code.google.com/closure/compiler/docs/api-tutorial3.html#dangers>`_.
If compiling your code introduces a bug, review the compiler documentation.

MediaDrop makes use of all the strict type checking offered by the compiler.
You should enter complete `JSDoc type annotations
<http://code.google.com/closure/compiler/docs/js-for-compiler.html>`_ as much
as possible, to improve the utility of these checks.  This has already proven
useful and will no doubt become even more useful as our codebase increases in
size.

Our build script is configured to complain as loudly as possible about a great
number of things.  Please do not ignore these warnings.  Learn about `the
problems they indicate
<http://code.google.com/closure/compiler/docs/error-ref.html>`_ and fix them.

Run the compiler by invoking this shell script:

.. sourcecode:: bash

   $ batch-scripts/closure/jscompile.sh

This produces a single file: ``mcore-compiled.js``.


Conventions and Guidelines
--------------------------

MediaDrop attempts to adhere the conventions of the Closure Library.  This
includes their coding style and design principles as much as possible.

The best way to get up to speed on Closure development is to read `Closure:
The Definitive Guide` by Michael Bolin.  It is the missing narrative
documentation for all of Closure Tools, and also proves insightful into more
general aspects of Javascript.

We make extensive use of goog.ui.Component.  It provides a consistent and
structured life cycle for UI elements.  Components can render DOM elements
onto the page or they can decorate DOM elements that have been included in
the initial page load, preferably both.  You should `familiarize yourself
with the component architecture
<http://code.google.com/p/closure-library/wiki/IntroToComponents>`_.

We follow the `Google Javascript Style Guide
<http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml>`_. The
key points are:

 * Two spaces instead of tabs.
 * Line length should not exceed 79 characters.
 * If an expression wraps to two lines, the second line should be indented
   twice (for a total of 4 spaces).  This includes long argument lists but
   excludes function bodies as well as multi-line object and array literals.
   `More info <http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml?showone=Code_formatting#Code_formatting>`_.
 * Built-in prototypes should never be modified.  This was the reason for our
   move from the Mootools framework; it's convenient at times, but it causes
   all kinds of interoperability problems with other libraries.

You can optionally use the `Closure Linter
<http://code.google.com/closure/utilities/>`_ for finding style and convention
errors and fixing them:

.. sourcecode:: bash

    # Install the python scripts into your MediaDrop virtualenv
    $ source mediadrop_env/bin/activate
    $ easy_install http://closure-linter.googlecode.com/files/closure_linter-latest.tar.gz

    # Lint one file:
    $ gjslint --strict mcore/fx.js

    # Try fixing some of the common errors with this utility:
    $ fixjsstyle --strict mcore/fx.js

.. _debug_toplevel:

=========================
Debugging in MediaDrop
=========================

Interactive Web-Based Debugging
-------------------------------

When debug mode is enabled (set in the ini config), you'll get interactive
web-based debugging when an exception occurs.

You can view the entire stack trace, with local variables and their
values, and even execute code in any context of the trace.


IPython
-------

If you're using the Paster server and you have if you have
`IPython <http://ipython.scipy.org/doc/rel-0.10/html/overview.html>`_
installed, try calling

.. sourcecode:: python

   mediadrop.ipython()()

at some point in your code; it'll act as a breakpoint and open up an IPython
shell with the local scope for you to play with.

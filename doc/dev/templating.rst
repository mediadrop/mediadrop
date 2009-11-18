.. _dev_templating:

===================
Templates and XHTML
===================

We use `Genshi <http://genshi.edgewall.org/>`_ for generating XHTML. It is built
on XML standards and, by design, ensures valid markup. This is the **V** in our
`**MVC** <http://en.wikipedia.org/wiki/Model-view-controller>`_.

Adding Your Own Layout
----------------------

The public-facing side of Simpleplex is designed so that it can be wrapped
in your own site layout.


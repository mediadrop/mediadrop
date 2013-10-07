.. _dev_templating:

===================
Templates and XHTML
===================

We use `Genshi <http://genshi.edgewall.org/>`_ for generating XHTML. It is built
on XML standards and, by design, ensures valid markup. This is the **V** in our
`**MVC** <http://en.wikipedia.org/wiki/Model-view-controller>`_.


Hierarchy and Layouts
---------------------

Each template that controllers call for rendering is wrapped by a ``master``
template and a ``layout`` template. ``master`` adds some CSS and JS necessary
for MediaDrop to work, and generally you shouldn't need to change it.
``layout``, however, is there for changing so you can easily wrap the output of
MediaDrop in your own site's layout.


Template Variables
------------------

Controllers define which templates are rendered and what variables to pass into
it. To find out what variables are passed, look up the returns of the
controller action in question.  If you're editing the template
``mediacore.templates.media.view`` look up the
:attr:`mediacore.controllers.media.MediaController.view` action. In nearly all
instances the naming matches one-to-one.


Further Resources
-----------------




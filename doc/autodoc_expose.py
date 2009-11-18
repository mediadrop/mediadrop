"""
Sphinx autodoc extension that reads @expose deco in controllers

"""
import mediacore
from tg.controllers import DecoratedController
from tg.decorators import Decoration

def setup(app):
    app.connect('autodoc-process-docstring', add_expose_info)

def add_expose_info(app, what, name, obj, options, lines):
    if (what != 'method' or not hasattr(obj, 'decoration')
        or not obj.im_class.__name__.endswith('Controller')):
        return

    deco = Decoration.get_decoration(obj)

    if not deco.expose:
        return

    try:
        # TODO: This ignores all but the first tmpl engine
        engine = deco.engines.values()[0]
        if engine[0] == 'genshi':
            template = engine[1]
            lines.append("\n")
            lines.append("\n")
            lines.append("Renders: :data:`%s`" % template)
    except:
        pass

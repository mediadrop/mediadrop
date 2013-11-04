"""
Sphinx autodoc extension that reads @expose decorator in controllers

"""
import mediadrop

def setup(app):
    app.connect('autodoc-process-docstring', add_expose_info)

def add_expose_info(app, what, name, obj, options, lines):
    if what == 'method' \
    and getattr(obj, 'exposed', False) \
    and obj.im_class.__name__.endswith('Controller') \
    and hasattr(obj, 'template'):
        lines.append("\n")
        lines.append("\n")
        lines.append("Renders: :data:`%s`" % obj.template)

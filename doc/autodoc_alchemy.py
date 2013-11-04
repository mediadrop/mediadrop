import mediadrop

def omit_sqlalchemy_descriptors(app, what, name, obj, skip, options):
    if obj.__doc__ == 'Public-facing descriptor, placed in the mapped class dictionary.':
        skip = True
    return skip

def setup(app):
    app.connect('autodoc-skip-member', omit_sqlalchemy_descriptors)

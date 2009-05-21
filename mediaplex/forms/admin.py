from tw.forms import ListForm, TextField

class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', suppress_label=True)]
    submit_text = None

    def display(self, value=None, **kw):
        """Display the form
        If value is a string we assume it is the search query
        """
        if isinstance(value, basestring):
            value = dict(search=value)
        elif value is None:
            value = 'SEARCH...'
        return super(SearchForm, self).display(value, **kw)

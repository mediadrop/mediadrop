from tw.forms import ListForm, TextField

class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', suppress_label=True)]
    submit_text = None

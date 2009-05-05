from tw.forms import ListForm, TextField

class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('searchquery', suppress_label=True)]
    submit_text = None

from tw.forms import ListForm, TextField

class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', label_text='SEARCH...')]
    submit_text = None


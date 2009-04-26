from tw.forms import ListForm, TextField

class SearchForm(ListForm):
    submit_text = None
    method = 'get'

    fields = [TextField('searchquery', suppress_label=True, attrs=dict(onclick="this.value=''"))]


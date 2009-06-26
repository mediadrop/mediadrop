from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, RadioButtonList
from tw.forms.validators import Schema, Int, NotEmpty, DateConverter, DateValidator, Email
from mediaplex.lib import helpers
from mediaplex.forms import ListForm

class PodcastForm(ListForm):
    template = 'mediaplex.templates.admin.podcasts.form'
    id = 'podcast-form'
    css_class = 'form'
    submit_text = None
    params = ['podcast']
    podcast = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    explicit_options = ['Yes', 'No', 'Clean']
    category_options = [
        'Arts',
        'Arts > Design',
        'Arts > Fashion & Beauty',
        'Arts > Food',
        'Arts > Literature',
        'Arts > Performing Arts',
        'Arts > Visual Arts',
        'Business',
        'Business > Business News',
        'Business > Careers',
        'Business > Investing',
        'Business > Management & Marketing',
        'Business > Shopping',
        'Comedy',
        'Education',
        'Education > Education Technology',
        'Education > Higher Education',
        'Education > K-12',
        'Education > Language Courses',
        'Education > Training',
        'Games & Hobbies',
        'Games & Hobbies > Automotive',
        'Games & Hobbies > Aviation',
        'Games & Hobbies > Hobbies',
        'Games & Hobbies > Other Games',
        'Games & Hobbies > Video Games',
        'Government & Organizations',
        'Government & Organizations > Local',
        'Government & Organizations > National',
        'Government & Organizations > Non-Profit',
        'Government & Organizations > Regional',
        'Health',
        'Health > Alternative Health',
        'Health > Fitness & Nutrition',
        'Health > Self-Help',
        'Health > Sexuality',
        'Kids & Family',
        'Music',
        'News & Politics',
        'Religion & Spirituality',
        'Religion & Spirituality > Buddhism',
        'Religion & Spirituality > Christianity',
        'Religion & Spirituality > Hinduism',
        'Religion & Spirituality > Islam',
        'Religion & Spirituality > Judaism',
        'Religion & Spirituality > Other',
        'Religion & Spirituality > Spirituality',
        'Science & Medicine',
        'Science & Medicine > Medicine',
        'Science & Medicine > Natural Sciences',
        'Science & Medicine > Social Sciences',
        'Society & Culture',
        'Society & Culture > History',
        'Society & Culture > Personal Journals',
        'Society & Culture > Philosophy',
        'Society & Culture > Places & Travel',
        'Sports & Recreation',
        'Sports & Recreation > Amateur',
        'Sports & Recreation > College & High School',
        'Sports & Recreation > Outdoor',
        'Sports & Recreation > Professional',
        'Technology',
        'Technology > Gadgets',
        'Technology > Tech News',
        'Technology > Podcasting',
        'Technology > Software How-To',
        'TV & Film'
    ]

    fields = [
        TextField('slug', validator=NotEmpty),
        TextField('title', validator=NotEmpty),
        TextField('subtitle'),
        TextField('author_name', validator=NotEmpty),
        TextField('author_email', validator=NotEmpty),
        TextArea('description', attrs=dict(rows=5, cols=25)),
        ListFieldSet('details', suppress_label=True, legend='Podcast Details:', children=[
            TextField('copyright'),
            SingleSelectField('category', options=category_options),
            RadioButtonList('explicit', label_text='Explicit?', options=explicit_options),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]

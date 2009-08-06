from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, RadioButtonList
from tw.forms.validators import Schema, Int, NotEmpty, DateConverter, DateValidator, Email, URL
from mediaplex.lib import helpers
from mediaplex.forms import ListForm, XHTMLTextArea, SubmitButton

class PodcastForm(ListForm):
    template = 'mediaplex.templates.admin.box-form'
    id = 'podcast-form'
    css_class = 'form'
    submit_text = None
    params = ['podcast']
    podcast = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    explicit_options = [('no', ''), ('yes', 'Parental Advisory'), ('clean', 'Clean')]
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
        TextField('slug', validator=NotEmpty, maxlength=50),
        TextField('title', validator=NotEmpty, maxlength=50),
        TextField('subtitle', maxlength=255),
        TextField('author_name', validator=NotEmpty, maxlength=50),
        TextField('author_email', validator=NotEmpty, maxlength=50),
        XHTMLTextArea('description', attrs=dict(rows=5, cols=25)),
        ListFieldSet('details', suppress_label=True, legend='Podcast Details:', css_classes=['details_fieldset'], children=[
            SingleSelectField('explicit', label_text='Explicit?', options=explicit_options),
            SingleSelectField('category', options=category_options),
            TextField('copyright', maxlength=50),
            TextField('itunes_url', label_text='iTunes URL', maxlength=80),
            TextField('feedburner_url', label_text='Feedburner URL', maxlength=80),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]

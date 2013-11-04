# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode.validators import URL
from tw.forms import SingleSelectField
from tw.forms.validators import NotEmpty

from mediadrop.forms import ListForm, ListFieldSet, SubmitButton, TextField, XHTMLTextArea, email_validator
from mediadrop.lib.i18n import N_, _
from mediadrop.plugin import events

class PodcastForm(ListForm):
    template = 'admin/box-form.html'
    id = 'podcast-form'
    css_class = 'form'
    submit_text = None
    
    event = events.Admin.PodcastForm
    
    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    explicit_options = lambda: (
        ('no', ''),
        ('yes', _('Parental Advisory')),
        ('clean', _('Clean')),
    )
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
        'TV & Film',
    ]

    fields = [
        TextField('slug', label_text=N_('Permalink'), validator=NotEmpty, maxlength=50),
        TextField('title', label_text=N_('Title'), validator=TextField.validator(not_empty=True), maxlength=50),
        TextField('subtitle', label_text=N_('Subtitle'), maxlength=255),
        TextField('author_name', label_text=N_('Author Name'), validator=TextField.validator(not_empty=True), maxlength=50),
        TextField('author_email', label_text=N_('Author Email'), validator=email_validator(not_empty=True), maxlength=50),
        XHTMLTextArea('description', label_text=N_('Description'), attrs=dict(rows=5, cols=25)),
        ListFieldSet('details', suppress_label=True, legend=N_('Podcast Details:'), css_classes=['details_fieldset'], children=[
            SingleSelectField('explicit', label_text=N_('Explicit?'), options=explicit_options),
            SingleSelectField('category', label_text=N_('Category'), options=category_options),
            TextField('copyright', label_text=N_('Copyright'), maxlength=50),
        ]),
        ListFieldSet('feed', suppress_label=True, legend=N_('Advanced Options:'), css_classes=['details_fieldset'], template='/admin/podcasts/feed_fieldset.html', children=[
            TextField('feed_url', maxlength=50, label_text=N_('Your Feed URL'), attrs={'readonly': True}),
            TextField('itunes_url', validator=URL, label_text=N_('iTunes URL'), maxlength=80),
            TextField('feedburner_url', validator=URL, label_text=N_('Feedburner URL'), maxlength=80),
        ]),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn']),
    ]

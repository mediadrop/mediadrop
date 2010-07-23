# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from formencode.validators import URL
from genshi.core import Markup
from tw.forms import ListFieldSet, SingleSelectField
from tw.forms.validators import NotEmpty
from mediacore.forms import ListForm, SubmitButton, TextField, XHTMLTextArea, email_validator

class PodcastForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'podcast-form'
    css_class = 'form'
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    explicit_options = [('no', ''), ('yes', _('Parental Advisory')), ('clean', _('Clean'))]
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
        TextField('slug', validator=NotEmpty, maxlength=50),
        TextField('title', validator=TextField.validator(not_empty=True), maxlength=50),
        TextField('subtitle', maxlength=255),
        TextField('author_name', validator=TextField.validator(not_empty=True), maxlength=50),
        TextField('author_email', validator=email_validator(not_empty=True), maxlength=50),
        XHTMLTextArea('description', attrs=dict(rows=5, cols=25)),
        ListFieldSet('details', suppress_label=True, legend='Podcast Details:', css_classes=['details_fieldset'], children=[
            SingleSelectField('explicit', label_text='Explicit?', options=explicit_options),
            SingleSelectField('category', options=category_options),
            TextField('copyright', maxlength=50),
        ]),
        ListFieldSet('feed', suppress_label=True, legend='Advanced Options:', css_classes=['details_fieldset'], children=[
            TextField('feed_url', maxlength=50, label_text='Your Feed URL', attrs={'readonly': True}),
            TextField('itunes_url', validator=URL, label_text='iTunes URL', help_text=Markup('<a href="https://phobos.apple.com/WebObjects/MZFinance.woa/wa/publishPodcast" target="_blank">Get an iTunes URL</a>'), maxlength=80),
            TextField('feedburner_url', validator=URL, label_text='Feedburner URL', help_text=Markup('<a href="http://feedburner.com/" target="_blank">Get a Feedburner URL</a>'), maxlength=80),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['btn', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['btn', 'btn-delete']),
    ]


/**
 * This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
 *
 * MediaCore is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * MediaCore is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
var SlugManager = new Class({

	Extends: Options,

	options: {
		slugField: 'slug',
		slugWrapper: 'slug_container',
		masterField: 'title',
		stub: 'slug_stub',
		stubWrapper: 'slug_stub_wrapper',
		stubParent: 'title_label',
		editSlugBtn: 'slug_edit'
	},

	slugField: null,
	slugWrapper: null,
	masterField: null,
	stub: null,
	stubWrapper: null,
	stubField: null,
	errorField: null,

	initialize: function(opts){
		this.setOptions(opts);

		this.slugField = $(this.options.slugField);
		this.slugWrapper = $(this.options.slugWrapper);
		this.masterField = $(this.options.masterField);

		var updateSlugFn = this.updateSlug.bind(this);
		this.masterField.addEvent('change', updateSlugFn).store('SlugManager', this);

		// Check if any error messages are set. if so, don't hide the slug field.
		this.errorField = this.slugWrapper.getElement('span.field_error');
		if (this.errorField == null) {
			this._hide(this.slugWrapper, true);
			this.slugField.set('disabled', true);

			var slug = this.slugField.get('value');
			this.stub = new Element('span', {text: slug, id: this.options.stub});
			this.stubField = new Element('input', {type: 'hidden', name: 'slug', value: slug});

			var editSlugBtn = new Element('span', {text: 'Edit', 'class': 'link', id: this.options.editSlugBtn});
			editSlugBtn.addEvent('click', this.showSlugField.bind(this));

			this.stubWrapper = new Element('div', {id: this.options.stubWrapper})
				.grab(new Element('label', {text: 'Slug:'})).appendText(' ')
				.grab(this.stub).appendText(' ')
				.grab(this.stubField)
				.grab(editSlugBtn)
				.inject($(this.options.stubParent), 'top');

			editSlugBtn.addEvent('click', function(){
				this.masterField.removeEvent('change', updateSlugFn);
			}.bind(this));
		}
	},

	showSlugField: function(){
		this._hide(this.stubWrapper, true);
		this._hide(this.slugWrapper, false);
		this.stubField.set('disabled', true);
		this.slugField.set('disabled', false);
	},

	updateSlug: function(){
		this.setSlug(this.masterField.get('value').slugify());
	},

	setSlug: function(slug){
		this.slugField.set('value', slug);
		if (this.errorField == null) {
			this.stubField.set('value', slug);
			this.stub.set('text', slug);
		}
	},

	_hide: function(field, flag){
		field.setStyle('display', (flag ? 'none' : 'block'));
	}
});

window.addEvent('domready', function(){
	smgr = new SlugManager();
});

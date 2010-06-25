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
String.implement({

	slugify: function(){
		return this.toString().trim().tidy().standardize().toLowerCase()
			.replace(/\s+/g,'-')
			.replace(/&(\#x?[0-9a-f]{2,6}|[a-z]{2,10});/g, '') // strip xhtml entities, they should be entered as unicode anyway
			.replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue') // some common german chars
			.replace(/[^a-z0-9\-]/g,'');
	}

});

var BoxForm = new Class({

	Implements: [Options, Events],

	options: {
	/*	onSave: function(){},
		onSaveSuccess: function(json){},
		onSaveError: function(json){}, */
		save: {link: 'cancel'},
		spinner: {
			'class': 'f-rgt form-saving',
			text: 'Saving...'
		},
		success: {
			'class': 'f-rgt form-saved',
			text: 'Saved!'
		},
		error: {
			'class': 'f-rgt form-save-error',
			text: 'Please correct the highlighted errors and save again.'
		}
	},

	initialize: function(form, opts){
		this.setOptions(opts);
		this.form = $(form).addEvent('submit', this.save.bind(this));
		this.request = this.form.get('send').addEvents({
			success: this.saved.bind(this),
			failure: function(){ alert('Saving failed. Please try again.'); }
		}).setOptions(this.options.save);
	},

	save: function(e){
		e = new Event(e).preventDefault();
		this.injectSpinner();
		if (this.tinyMCEInputs == undefined) {
			this.tinyMCEInputs = this.form.getElements('textarea.tinymcearea')
				.map(this.createHiddenTinyMCEInput, this);
		}
		this.tinyMCEInputs.each(this.stashTinyMCEValue, this);
		this.form.send();
		this.fireEvent('save');
	},

	saved: function(resp){
		var json = JSON.decode(resp);
		new Hash(json.values).each(this.injectValue, this);
		this.form.getElements('span[class=field_error]').destroy();
		if (!json.success) new Hash(json.errors).each(this.injectError, this);
		this.updateSpinner(json.success);
		this.fireEvent('save' + (json.success? 'Success' : 'Error'), json);
	},

	injectValue: function(value, name){
		var field = this.form.getElementById(name), tag = field.get('tag');
		if (tag == 'ul') {
			field.getElements('input[checked]').set('checked', false);
			if ($type(value) != 'array') value = [value];
			for (var i = 0, l = value.length; i < l; i++) {
				field.getElements('input[value="' + value[i] + '"]').set('checked', true);
			}
		} else if (tag == 'select' && field.multiple) {
			field.getElements('option[selected]').set('selected', false);
			if ($type(value) != 'array') value = [value];
			for (var i = 0, l = value.length; i < l; i++) {
				field.getElements('option[value="' + value[i] + '"]').set('selected', true);
			}
		} else if (tag == 'input' && (field.type == 'checkbox' || field.type == 'radio'))  {
			field.set('checked', !!value);
		} else {
			if (field.hasClass('hidden_tinymce_value')) tinyMCE.get(field.name).setContent(value || '');
			field.value = value;
		}
	},

	injectError: function(msg, name){
		var label = this.form.getElement('label[for=' + name + ']');
		var el = new Element('span', {'class': 'field_error', text: msg}).inject(label, 'after');
		var field = this.form.getElementById(name).highlight();
	},

	injectSpinner: function(){
		if (this.spinner) this.spinner.destroy();
		this.spinner = new Element('span', this.options.spinner);
		this.form.getElement('.box-foot').adopt(this.spinner);
	},

	updateSpinner: function(success){
		var props = this.options[success ? 'success' : 'error'];
		this.spinner = new Element('span', props).replaces(this.spinner);
		if (success) this.spinner.fade.delay(2000, this.spinner);
	},

	createHiddenTinyMCEInput: function(textarea){
		return new Element('input', {
			id: textarea.id,
			name: textarea.name,
			type: 'hidden',
			'class': 'hidden_tinymce_value'
		}).replaces(textarea);
	},

	stashTinyMCEValue: function(el){
		el.value = tinyMCE.get(el.name).getContent();
	}

});

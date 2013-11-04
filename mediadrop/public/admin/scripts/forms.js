/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

String.implement({

	slugify: function(){
		return this.toString().trim().tidy().standardize().toLowerCase()
			.replace(/\s+/g,'-')
			.replace(/&(\#x?[0-9a-f]{2,6}|[a-z]{2,10});/g, '') // strip xhtml entities, they should be entered as unicode anyway
			.replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss') // some common german chars
			.replace(/[^a-z0-9\-]/g,'');
	}

});

/**
 * <form> property that can get or set a hash of values.
 *
 * XXX: Element IDs should match field names, but only for checkbox/radio lists is this required.
 *      Add a prefix for all IDs by: $('my-form').store('fieldPrefix', 'my-form-')
 *      You can always avoid all this by calling Element.get('fieldValue') directly on your fields.
 *
 * @author Nathan Wright <nathan@mediacore.com>
 */
Element.Properties.formValues = {

	set: function(values){
		var prefix = this.retrieve('fieldPrefix', '');
		new Hash(values).each(function(value, name){
			var el = this.getElementById(prefix + name);
			if (!el) el = this.elements[name];
			if (!el || $type(el) == 'collection') Log.log('No ' + name + ' element to set the response value to', value);
			el.set('fieldValue', value);
		}, this);
	},

	get: function(){
		var values = new Hash();
		var fields = new Hash();
		var prefix = this.retrieve('fieldPrefix', '');
		for (var el, i = 0, l = this.elements.length; i < l; i++) {
			el = this.elements[i];
			if (!fields[el.name]) fields[el.name] = 1;
		}
		fields.each(function(a, name){
			var el = this.getElementById(prefix + name);
			if (!el) el = this.elements[name];
			if (!el || $type(el) == 'collection') return Log.log('No field element with id ' + prefix + name, this);
			var value = $(el).get('fieldValue');
			if (value == undefined) return;
			values[name] = value;
		}, this);
		return values;
	}

};

/**
 * <input/textarea/select> and <ul/ol> checkbox/radio value property.
 * Gets and sets scalar and list values, depending on the field type.
 *
 * @author Nathan Wright <nathan@mediacore.com>
 */
(function(){

Element.Properties.fieldValue = {

	set: function(value){
		var tag = this.get('tag');
		if (tag == 'input') {
			if (this.type == 'checkbox' || this.type == 'radio') this.checked = !!value;
			else if (this.retrieve('BoxForm.Slug')) this.retrieve('BoxForm.Slug').setSlug(value);
			else this.value = value;
		} else if (tag == 'textarea') {
			if (this.hasClass('tinymcearea')) tinyMCE.get(this.name).setContent(value || '');
			this.value = value;
		} else if (tag == 'select') {
			if (this.multiple) _setOptions(this, 'option', 'selected', value);
			else this.value = value;
		} else if (tag == 'ul' || tag == 'ol') {
			_setOptions(this, 'input', 'checked', value);
		}
	},

	get: function(){
		if (this.disabled) return;
		var tag = this.get('tag');
		if (tag == 'input') {
			if (this.type == 'checkbox' || this.type == 'radio') {
				return this.checked ? this.value : null;
			} else if (this.type != 'submit' && this.type != 'reset' && this.type != 'file') {
				return this.value;
			}
		} else if (tag == 'textarea') {
			if (this.hasClass('tinymcearea')) return tinyMCE.get(this.name).getContent();
			return this.value;
		} else if (tag == 'select') {
			if (this.multiple) return _getOptions(this, 'option', 'selected');
			return this.value;
		} else if (tag == 'ul' || tag == 'ol') {
			return _getOptions(this, 'input', 'checked');
		}
	}

};

// private helpers for fieldValue
var _setOptions = function(el, tag, prop, value){
	value = $splat(value);
	el.getElements(tag + '[' + prop + ']').set(prop, false);
	for (var i = 0, l = value.length; i < l; i++) {
		el.getElements(tag + '[value="' + value[i] + '"]').set(prop, true);
	}
}, _getOptions = function(el, tag, prop){
	return child = el.getElements(tag + '[' + prop + ']').map(function(opt){
		return opt.value;
	});
};

})();

var BoxForm = new Class({

	Implements: [Options, Events],

	Binds: ['save', 'saved', 'updateSpinner'],

	options: {
	/*	onSave: function(values){},
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
		failure: {
			'class': 'f-rgt form-save-error',
			text: 'Saving failed. Please try again.'
		},
		userError: {
			'class': 'f-rgt form-save-error',
			text: 'Please correct the highlighted errors and save again.'
		},
		slug: {
			slugify: 'title'
		}
	},

	initialize: function(form, opts){
		this.setOptions(opts);
		this.form = $(form).store('BoxForm', this)
			.addEvent('submit', this.save);
		if (this.options.slug && this.form.elements['slug']) {
			this.slug = new BoxForm.Slug(this.form.elements['slug'], this.options.slug);
		}
	},

	save: function(e){
		e = new Event(e).preventDefault();
		this.injectSpinner();
		if (!this.request) this.request = new Request.JSON(this.options.save).addEvents({
			success: this.saved,
			failure: this.updateSpinner.pass('failure')
		});
		var values = this.form.get('formValues');
		this.request.send({
			url: this.form.get('action'),
			method: this.form.get('method'),
			data: values
		});
		this.fireEvent('save', [values]);
	},

	saved: function(json){
		this.form.set('formValues', json.values).getElements('span[class=field_error]').destroy();
		if (!json.success) new Hash(json.errors).each(this.injectError, this);
		this.updateSpinner(json.success ? 'success' : 'userError');
		this.fireEvent('save' + (json.success? 'Success' : 'UserError'), json);
	},

	injectError: function(msg, name){
		var label = this.form.getElement('label[for=' + name + ']');
		if (label === null) {
		    /* This may happen if an element has it's label suppressed (e.g.
		     * a container widget). Not to highlight the error is not nice but
		     * at least the users is notified about the error right next to the
		     * 'save' button (as opposed to an endless spinner and a usually 
		     * invisible JS exception).
		     * Also this situation should not appear in stock MediaCore but only
		     * with optional plugins.
		     */
		    if (window.console !== undefined)
		        console.log('unable to display error message "' + msg + '" for field "' + name + '"');
	        return;
		}
		var el = new Element('span', {'class': 'field_error', text: msg}).inject(label, 'after');
		var field = this.form.getElementById(name).highlight();
	},

	injectSpinner: function(){
		if (this.spinner) this.spinner.destroy();
		this.spinner = new Element('span', this.options.spinner);
		this.form.getElement('.box-foot').adopt(this.spinner);
	},

	updateSpinner: function(status){
		var props = this.options[status];
		this.spinner = new Element('span', props).replaces(this.spinner);
		if (status == 'success') this.spinner.fade.delay(2000, this.spinner);
	}

});

BoxForm.Slug = new Class({

	Implements: Options,

	Binds: ['onChange', 'slugify', 'toggle'],

	options: {
		editText: 'Edit',
		hideText: 'Hide',
		slugify: '',
		slugifyOn: 'change'
	},

	initialValue: null,

	initialize: function(el, opts){
		this.field = $(el).store('BoxForm.Slug', this).addEvent('change', this.onChange);
		this.container = this.field.getParent('li');
		this.label = this.container.getElement('div.form_label');
		this.indicator = new Element('span', {'class': 'slug-indicator'})
			.inject(this.label, 'bottom');
		this.label.appendText(' ');
		this.toggleButton = new Element('span', {text: this.options.editText, 'class': 'slug-toggle link'})
			.inject(this.label, 'bottom')
			.addEvent('click', this.toggle);
		this.setOptions(opts);
		if (this.options.slugify) this.attachSlugifier();
		this.show(false);
	},

	attachSlugifier: function(){
		$(this.options.slugify).addEvent(this.options.slugifyOn, this.slugify);
		return this;
	},

	detachSlugifier: function(){
		$(this.options.slugify).removeEvent(this.options.slugifyOn, this.slugify);
		return this;
	},

	show: function(flag){
		if (flag) {
			this.container.removeClass('slug-minimized').addClass('slug-expanded');
			this.field.set('type', 'text').select();
			this.toggleButton.set('text', this.options.hideText);
			if (this.initialValue == null) this.initialValue = this.field.get('value');
		} else {
			this.container.addClass('slug-minimized').removeClass('slug-expanded');
			this.field.set('type', 'hidden');
			this.indicator.set('text', this.field.get('value'));
			this.toggleButton.set('text', this.options.editText);
		}
		this.shown = !!flag;
		return this;
	},

	toggle: function(){
		return this.show(!this.shown);
	},

	slugify: function(e){
		var target = $(new Event(e).target);
		return this.setSlug(target.get('value').slugify());
	},

	setSlug: function(slug){
		this.field.value = slug;
		this.indicator.set('text', slug);
		return this;
	},

	onChange: function(e){
		if (this.initialValue == this.field.get('value')) return;
		this.detachSlugifier();
	}

});

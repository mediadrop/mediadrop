/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * A Popup Form
 *
 * @author Nathan Wright <nathan@mediacore.com>
 */

var Modal = new Class({

	Implements: [Options, Events],

	options: {
	/*	onOpen: $empty,
		onClose: $empty, */
		squeezeBox: {
			handler: 'fittedAdopt',
			size: {x: 630, y: 400},
			overlayOpacity: 0.4
		}
	},

	content: null,
	stash: null,

	initialize: function(content, opts){
		this.setOptions(opts);
		this.content = $(content);
		this.stash = new Element('div', {id: this.content.id + '-stash'});
		this.stash.hide().adopt(this.content).inject(document.body);
		this.content.show();
	},

	open: function(e){
		if ($type(e) == 'event') {
			var e = new Event(e).stop(), target = $(e.target);
		} else {
			var target = $(e);
		}
		var self = this, onClose = function(squeezeContent){
			// steal back our content, preventing it from being trashed
			self.fireEvent('close');
			self.stash.empty().adopt(squeezeContent.getChildren());
			SqueezeBox.removeEvent('close', onClose);
		};
		SqueezeBox.initialize(this.options.squeezeBox)
			.fromElement(this.content, this.options.squeezeBox)
			.addEvent('close', onClose);
		return this.fireEvent('open', [target, this.content, this.form]);
	},

	close: function(){
		SqueezeBox.close();
		return this;
	}

});

var ModalForm = new Class({

	Extends: Modal,

	options: {
	/*	onSubmit: $empty,
		onComplete: $empty,
		onError: $empty, */
		focus: null,
		ajax: false,
		ajaxOptions: {link: 'cancel'},
		extraData: {}, // FIXME: Inject for static forms?
		slugifyField: '',
		resetOnComplete: false
	},

	form: null,
	req: null,

	initialize: function(content, opts){
		this.parent(content, opts);
		this.form = this.content && this.content.getElement('form');
		this.attach();
	},

	attach: function(){
		this.form.addEvent('submit', this.formSubmit.bind(this));
		if (this.options.slugifyField) {
			var slugifyField = $(this.form.elements[this.options.slugifyField]);
			var slugField = $(this.form.elements['slug']);
			slugifyField.addEvent('keyup', this._slugify.bindWithEvent(this, [slugField, slugifyField]));
		}
		var cancelBtn = this.form.getElement('button[type=reset]');
		if (cancelBtn) cancelBtn.addEvent('click', this.close.bind(this));
		return this.addEvent('complete', this._resetOnComplete.bind(this), true);
	},

	formSubmit: function(e, btn){
		var data = this.getValues();
		if (this.options.ajax) {
			if (e) new Event(e).stop();
			if (btn) data[btn] = btn; // specify which button was clicked so it is added to the submit data
			if (!this.req) this._setupRequest();
			data.extend(this.options.extraData);
			this.req.send({
				url: this.form.get('action'),
				data: data.toQueryString()
			});
		}
		return this.fireEvent('submit', [e, this.form, data]);
	},

	formSubmitted: function(resp){
		resp = new Hash(resp);
		if (resp.success) {
			this.fireEvent('complete', [resp.erase('success')]).close();
		} else {
			this.fireEvent('error', [resp.erase('success')]);
			if (resp.has('errors')) $each(resp.errors, this.formError.bind(this));
		}
	},

	formError: function(msg, field){
		var wrapper = this.content.getElement('label[for="' + field + '"]');
		if (wrapper) wrapper = wrapper.getParent();
		else wrapper = this.content.getElement('.box-content');
		var error = new Element('span', {'class': 'fielderror', text: msg});
		var next = wrapper.getNext();
		if (next && next.hasClass('fielderror')) error.replaces(next);
		else error.inject(wrapper, 'after');
	},

	setFormAction: function(url, method){
		if ($type(url) == 'element') var method = url.get('method'), url = url.get('action');
		this.form.set('action', url);
		if (method) this.form.set('method', method);
		return this;
	},

	setValues: function(input){
		if ($type(input) == 'element') input = input.get('formValues');
		return this.form.set('formValues', input);
	},

	getValues: function(){
		return this.form.get('formValues');
	},

	open: function(e){
		if ($type(e) == 'event') {
			var e = new Event(e).stop(), target = $(e.target);
		} else {
			var target = $(e);
		}
		if (target) {
			var targetForm = (target.tagName == 'form' && target) || target.getParent('form');
			if (targetForm) this.setFormAction(targetForm).setValues(targetForm);
		}

		var focusOn = (this.options.focus ? $(this.form.elements[this.options.focus]) : null);
		if (focusOn) {
			var onOpen = focusOn.focus.create({delay: 250, bind: focusOn}), onClose = function(){
				SqueezeBox.removeEvent('open', onOpen);
				SqueezeBox.removeEvent('close', onClose);
			};
			SqueezeBox.addEvents({'open': onOpen, 'close': onClose});
		}

		return this.parent(e);
	},

	_slugify: function(e, slugField, slugifyField){
		var slug = slugifyField.get('value').slugify();
		slugField.set('value', slug);
	},

	_setupRequest: function(){
		this.req = new Request.JSON(this.options.ajaxOptions).addEvents({
			success: this.formSubmitted.bind(this),
			failure: function(){ alert('error saving'); },
			exception: function(){ alert('exception saving'); }
		});
	},

	_resetOnComplete: function(e){
		if (this.options.resetOnComplete) this.form.reset();
	}

});

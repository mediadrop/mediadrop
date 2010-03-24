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

/**
 * A Popup Form
 *
 * @author Nathan Wright <nathan@simplestation.com>
 */
var ModalForm = new Class({

	Implements: [Options, Events],

	options: {
	/*	onOpen: $empty,
		onSubmit: $empty,
		onComplete: $empty,
		onError: $empty, */
		content: null,
		focus: null,
		squeezeBox: {handler: 'fittedAdopt'},
		ajax: false,
		ajaxOptions: {link: 'cancel'},
		extraData: {}, // FIXME: Inject for static forms?
		slugifyField: ''
	},

	content: null,
	form: null,
	stash: null,
	req: null,

	initialize: function(content, opts){
		this.setOptions(opts);
		this.content = $(content);
		this.form = this.content && this.content.getElement('form');
		this.build();
		this.attach();
	},

	build: function(){
		this.stash = new Element('div', {id: this.content.id + '-stash'});
		this.stash.hide().adopt(this.content).inject(document.body);
		this.content.show();
	},

	attach: function(){
		this.form.addEvent('submit', this.formSubmit.bind(this));
		if (this.options.slugifyField) {
			var slugifyField = $(this.form.elements[this.options.slugifyField]);
			var slugField = $(this.form.elements['slug']);
			slugifyField.addEvent('keyup', this._slugify.bindWithEvent(this, [slugField, slugifyField]));
		}
		return this;
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
		if ($type(input) == 'element') {
			var values = new Hash();
			// taken from Element.toQueryString
			input.getElements('input, select, textarea', true).each(function(el){
				if (!el.name || el.disabled || el.type == 'submit' || el.type == 'reset' || el.type == 'file') return;
				var value = (el.tagName.toLowerCase() == 'select') ? Element.getSelected(el).map(function(opt){
					return opt.value;
				}) : ((el.type == 'radio' || el.type == 'checkbox') && !el.checked) ? null : el.value;
				$splat(value).each(function(val){
					if (typeof val != 'undefined') values.set(el.name, val);
				});
			});
		} else {
			var values = new Hash(input);
		}

		for (var el, i = this.form.elements.length; i--; ) {
			el = $(this.form.elements[i]);
			el.set('value', values.get(el.name));
		}
		return this;
	},

	getValues: function(){
		var values = new Hash();
		for (var el, i = this.form.elements.length; i--; ) {
			el = $(this.form.elements[i]);
			if (el.type == 'submit' || el.type == 'reset') continue;
			values.set(el.get('name'), el.get('value'));
		};
		return values;
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

		this.fireEvent('open', [target, this.content, this.form]);

		var focusOn = (this.options.focus ? $(this.form.elements[this.options.focus]) : null);
		SqueezeBox.fromElement(this.content, $extend(this.options.squeezeBox, {
			onOpen: function(){
				if (focusOn) focusOn.focus.delay(250, focusOn);
			},
			onClose: function(squeezeContent){
				// steal back our content, preventing it from being trashed
				this.stash.empty().adopt(squeezeContent.getChildren());
			}.bind(this)
		}));

		return this;
	},

	close: function(){
		SqueezeBox.close();
		return this;
	},

	_slugify: function(e, slugField, slugifyField){
		var slug = slugifyField.get('value')
			.toLowerCase()
			.replace(/\s+/g, '-')
			.replace(/[^a-z0-9_-]/g, '');
		slugField.set('value', slug);
	},

	_setupRequest: function(){
		this.req = new Request.JSON(this.options.ajaxOptions).addEvents({
			success: this.formSubmitted.bind(this),
			failure: function(){ alert('error saving'); },
			exception: function(){ alert('exception saving'); }
		});
	}
});

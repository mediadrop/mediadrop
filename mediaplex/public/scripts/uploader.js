/**
 * Upload Controller, implements frontend for upload page
 * @author     Anthony Theocharis
 */
var UploadManager = new Class({
	form: null,
	action: null,
	fields: null,
	submit: null,
	submitted: false,
	uploadButton: null,
	browseButton: null,


	initialize: function(form, action) {
		this.form = $(form);
		this.action = action;
		this.fields = $$(this.form.elements).filter(function(el) {
			// filter out submit buttons
			return el.get('type') != 'submit';
		}, this).map(function(value) {
			// create upload field wrappers
			return new UploadField(this, value);
		}, this);

		console.log('fields:', this.fields)

		this.submit = this.form.getElement('input[type=submit]');
		this.form.addEvent('submit', this.onSubmit.bind(this));

		var opts = {
			url: this.action,
			onSuccess: this.displayErrors.bind(this),
			link: 'cancel' /* all new calls take precedence */
		};
		this.req = new Request.JSON(opts);
	},

	onSubmit: function(e) {
		if (e) {
			new Event(e).stop();
			this.validate();
			this.submit.set('disabled', true);
			this.submitted = true;
			return false;
		}
		return true;
	},

	validate: function() {
		var data = {};
		data['validate'] = JSON.encode(this.fields.map(function(f){return f.name;}));
		this.fields.each(function(f) {
			data[f.name] = f.field.get('value');
		});
		this.req.send({data: data});
	},

	displayErrors: function(responseJSON) {
		if (this.submitted && responseJSON['valid']) {
			this.form.submit();
		} else {
			this.fields.each(function(field) {
				field.displayError(responseJSON);
			});
		}

		if (this.submitted) {
			this.submit.set('disabled', false);
		}
	}
});

var UploadField = new Class({
	name: null,
	error: null,
	field: null,
	td: null,
	manager: null,
	req: null,

	initialize: function(manager, field) {
		this.manager = manager;
		this.field = field;
		this.field.addEvent('blur', this.validate.bind(this));
		this.name = this.field.get('name');
		/* NB: this path relies heavily on the current table layout,
		 * and should be updated along with the template */
		this.td = field.parentNode;
		this.error = this.td.parentNode.getPrevious().getElements('.field-error')[0];

		var opts = {
			url: this.manager.action,
			onSuccess: this.displayError.bind(this),
			link: 'cancel' /* all new calls take precedence */
		};
		this.req = new Request.JSON(opts);
	},

	displayError: function(responseJSON) {
		if (err = responseJSON['err'][this.field.get('name')]) {
			this.error.set('html', err);
			this.td.removeClass('noerr');
			this.td.addClass('err');
		} else {
			this.error.set('html', '');
			this.td.removeClass('err');
			this.td.addClass('noerr');
		}
	},

	validate: function() {
		var data = {};
		data['validate'] = JSON.encode([this.name]);
		data[this.field.get('name')] = this.field.get('value');
		this.req.send({data: data});
	}
});


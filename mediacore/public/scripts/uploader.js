/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * Upload Controller, implements frontend for Swiff.Uploader
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
			// filter out submit buttons (all browsers)
			// and filter out form elements themselves (ie only. go figure)
			return el.get('type') != 'submit' && el.get('tag') != 'form';
		}, this).map(function(value) {
			// create upload field wrappers
			return new UploadField(this, value);
		}, this);

		this.submit = this.form.getElement('button[type=submit]');
		this.form.addEvent('submit', this.onSubmit.bind(this));

		var opts = {
			url: this.action,
			onSuccess: this.displayErrors.bind(this),
			link: 'cancel' /* all new calls take precedence */
		};
		this.req = new Request(opts);
	},

	onSubmit: function(e) {
		if (e) {
//			new Event(e).stop();
			this.validate();
			this.submit.set('disabled', true);
			this.submitted = true;
//			return false;
		}
//		return true;
	},

	validate: function(o) {
		var data = {};
		this.form.fireEvent('beforeAjax');
		data['validate'] = JSON.encode(this.fields.map(function(f){return f.name;}));
		this.fields.each(function(f) {
			data[f.name] = f.field.get('value');
		});
		opts = {data: data}
		if (o) {
			opts = $extend(o, opts);
		}
		this.req.send(opts);
	},

	displayErrors: function(resp) {
		var responseJSON;
		if ($type(resp) == 'object') {
			// TODO: Figure out why the resp argument is sometimes a string and
			// sometimes an parsed object. I think it lies the Request object,
			// Request.processScripts().
			responseJSON = resp
		} else {
			responseJSON = JSON.decode(resp, true) || {};
		}
		if (this.submitted && responseJSON['valid']) {
			this.form.submit();
		} else {
			this.fields.each(function(field) {
				var singleJSON = {err: responseJSON['err'][field.name]};
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
		this.req = new Request(opts);
	},

	displayError: function(resp) {
		var responseJSON;
		if ($type(resp) == 'object') {
			// Sometimes this is passed in as a parsed object
			// from the UploadManager.displayErrors() method.
			responseJSON = resp
		} else {
			responseJSON = JSON.decode(resp, true) || {};
		}

		if (err = responseJSON['err'][this.name]) {
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
		this.field.form.fireEvent('beforeAjax');
		data['validate'] = JSON.encode([this.name]);
		data[this.field.get('name')] = this.field.get('value');
		this.req.send({data: data});
	}
});

var SwiffUploadManager = new Class({
	// TODO: Rewrite this class to use an options dict, instead of a huge
	//       number of constructor args.

	form: null,
	action: null,
	uploader: null,
	browseButton: null,
	uploadButton: null,
	progressBar: null,
	enabled: false,

	initialize: function(form, action, failurePage, baseUrl, typeFilter, browseButton, uploadButton, fileInfoDiv, statusDiv, messages, fileSizeMax) {
		if (Browser.Platform.linux) {
			// There's a bug in the flash player for linux that freezes the browser with swiff.uploader
			// don't bother setting it up.
			return;
		}

		this.form = $(form);
		this.action = action;
		this.failurePage = failurePage;
		this.baseUrl = baseUrl;
		this.typeFilter = typeFilter;
		this.browseButton = $(browseButton);
		this.uploadButton = $(uploadButton);
		this.fileInfoDiv = $(fileInfoDiv);
		this.statusDiv = $(statusDiv)
		this.percent = this.statusDiv.getChildren('.percent')[0];
		this.notices = this.statusDiv.getChildren('.text')[0];

		this.messages = {};
		for (x in messages) {
			this.messages[x] = [messages[x], false];
		}

		this.browseButton.addClass('enabled');
		this.fileInfoDiv.addClass('active');
		this.statusDiv.addClass('active');

		var submit = this.form.getElement('button[type=submit]');
		var finput = this.form.getElement('input[type=file]');

		// Uploader instance
		this.uploader = new Swiff.Uploader({
			path: this.baseUrl + 'scripts/third-party/Swiff.Uploader.swf',
			url: this.action,
			verbose: false,
			queued: false,
			multiple: false,
			typeFilter: this.typeFilter,
			target: this.browseButton, // the element to cover with the flash object
			fieldName: finput.get('name'), // set the fieldname to the default form's file input name
			instantStart: false,
			fileSizeMax: fileSizeMax,
			appendCookieData: false,
			onSelectSuccess: this.onSelectSuccess.bind(this),
			onSelectFail: this.onSelectFail.bind(this),
			onQueue: this.onQueue.bind(this),
			onFileComplete: this.onFileComplete.bind(this),
			onComplete: this.onComplete.bind(this),
			timeLimit: 60
		});

		// Set up the focus/blur and reposition events for the uploader Flash object
		this.browseButton.addEvents({
			mouseenter: function() {
				this.browseButton.addClass('hover');
				this.uploader.reposition();
			}.bind(this),
			mouseleave: function() {
				this.browseButton.removeClass('hover');
//				this.uploader.blur();
			}.bind(this),
			mousedown: function() {
				this.browseButton.addClass('active');
//				this.uploader.focus();
			}.bind(this)
		});

		var deactivateBtn = function(){
			this.browseButton.removeClass('active');
		}.bind(this);
		this.uploader.addEvents({
			select: deactivateBtn,
			cancel: deactivateBtn
		});

		this.form.addEvent('submit', function(e){
			if (this.uploader.fileList.length >= 1) {
				if (e) new Event(e).stop();
				this.startUpload();
			}
		}.bind(this));

		// Set the default onclick event for the upload button
/*		this.uploadButton.addEvent('click', function() {
			this.startUpload();
		}.bind(this));
*/

		// Overwrite the onSuccess event for the UploadManager's validation check.
		// It won't ever be called by UploadMGR because we just removed the button that triggers it
		// so it should be safe to overwrite for our own purposes.
		UploadMGR.req.removeEvents('onSuccess');
		UploadMGR.req.addEvents({onSuccess: this.validated.bind(this)});
		UploadMGR.fields = UploadMGR.fields.filter(function(f) {
			return f.field.get('type') != 'file';
		});

		// Erase the default file and submit inputs
		/* NB: this path relies heavily on the current table layout,
		 * and should be updated along with the template */
		finput.destroy();
/*		var fpp = $(finput.parentNode.parentNode); // ensure element has added mootools element properties.
		fpp.getPrevious().destroy();
		fpp.destroy();*/
	},

	// returns a dict with all the form fields/values,
	// in the format of the data object for Request objects
	getFormValues: function() {
		var values = {};
		this.form.fireEvent('beforeAjax');
		$$(this.form.elements).each(function(el) {
			values[el.get('name')] = el.get('value');
		});
		return values;
	},

	// callback for validation AJAX request, which is fired when the submit button is pressed
	validated: function(resp) {
		responseJSON = JSON.decode(resp, true) || {};
		if (responseJSON['valid']) {
			opts = {data: this.getFormValues()};
			this.uploader.setOptions(opts);
			this.uploader.start();
			this.setEnabled(false);
		} else {
			UploadMGR.displayErrors(responseJSON);
		}
	},

	// Default onclick event for the upload button.
	// should only actually do anything if enabled
	startUpload: function() {
		if (this.enabled) {
			UploadMGR.validate();
		}
	},

	// called by the uploader when uploading, every few hundred milliseconds
	onQueue: function() {
		if (!this.uploader.uploading) return;
		var p = this.uploader.percentLoaded;
		this.percent.set('html', (p>=1?p-1:p) + '%');

		// Iterate over all messages, displaying them if necessary.
		for (x in this.messages) {
			msg = this.messages[x]
			if (!msg[1]) {
				// If this message has not been displayed yet
				if (x <= p) {
					// If this message should be displayed at this point
					msg[1] = true;
					this.notices.set('html', msg[0]);
				}
			}
		}
	},

	// called by the uploader when selecting a file fails. eg. if it's too big.
	onSelectFail: function(files) {
		// console.log(files[0].name, files[0].validationError);
	},

	// called by the uploader when selecting a file from the browse box succeeds
	onSelectSuccess: function(files) {
		if (this.uploader.fileList.length > 1) {
			// If there was already a file in the list, remove that one, and keep
			// the new one.
			this.uploader.fileRemove(this.uploader.fileList[0]);
		}
		this.setEnabled(true);
		this.fileInfoDiv.set('html', '<span class="f-lft">You chose:&nbsp;</span> <span class="filename">'+files[0].name+' ('+Swiff.Uploader.formatUnit(files[0].size, 'b')+')</span>');
	},

	// called by the uploader when a file upload is completed
	onFileComplete: function(file) {
		if (file.response.error) {
			this.redirectFailure(this.uploader.fileList[0].response.code);
		} else {
			var json = JSON.decode(file.response.text, true)
			if (json.success) {
				this.notices.set('html', 'Success! You will be redirected shortly.');
				this.percent.set('html', '100%');
				this.statusDiv.addClass('finished');
				var redirect = function(){window.location = json.redirect;};
				redirect.create({delay: 1000})();
			} else {
				this.redirectFailure();
			}
		}

		file.remove();
	},

	// called by the uploader when all uploads are completed.
	// this doesn't really apply to us, because we only allow one upload at a time.
	onComplete: function() {
	},

	setEnabled: function(en) {
		if (en) {
//			this.uploader.setEnabled(false);
			this.enabled = true;
//			this.uploadButton.addClass('enabled');
		} else {
			this.uploader.setEnabled(true);
			this.enabled = false;
//			this.uploadButton.removeClass('enabled');
		}

	},

	redirectFailure: function(incl) {
		var text = "Failed Upload";
		if ($defined(incl)) {
			text += ": " + incl;
		}
		this.statusDiv.set('html', text);
		var redirect = function(){window.location = this.failurePage;};
		redirect.create({delay: 1000, bind:this})();
	}

});

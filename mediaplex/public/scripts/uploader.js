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
			// filter out submit buttons
			return el.get('type') != 'submit';
		}, this).map(function(value) {
			// create upload field wrappers
			return new UploadField(this, value);
		}, this);

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

	validate: function(o) {
		var data = {};
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

var SwiffUploadManager = new Class({
	form: null,
	action: null,
	uploader: null,
	browseButton: null,
	uploadButton: null,
	progressBar: null,
	enabled: false,
	
	initialize: function(form, action, failurePage, baseUrl, browseButton, uploadButton, fileInfoDiv, statusDiv) {
		if (Browser.Platform.linux) {
			// There's a bug in the flash player for linux that freezes the browser with swiff.uploader
			// don't bother setting it up.
			return;
		}

		this.form = $(form);
		this.action = action;
		this.failurePage = failurePage;
		this.baseUrl = baseUrl;
		this.browseButton = $(browseButton);
		this.uploadButton = $(uploadButton);
		this.fileInfoDiv = $(fileInfoDiv);
		this.statusDiv = $(statusDiv)

		this.browseButton.addClass('active').addClass('enabled');
		this.uploadButton.addClass('active');
		this.fileInfoDiv.addClass('active');
		this.statusDiv.addClass('active');

		var submit = this.form.getElement('input[type=submit]');
		var finput = this.form.getElement('input[type=file]');

		// Uploader instance
		this.uploader = new Swiff.Uploader({
			path: this.baseUrl + 'scripts/third-party/Swiff.Uploader.swf',
			url: this.action,
			verbose: false,
			queued: false,
			multiple: false,
			typeFilter: "*.avi; *.divx; *.dv; *.dvx; *.flv; *.m4v; *.mov; *.mp4; *.mpeg; *.mpg; *.qt; *.vob; *.3gp; *.wmv",
			target: this.browseButton, // the element to cover with the flash object
			fieldName: finput.get('name'), // set the fieldname to the default form's file input name
			instantStart: false,
			fileSizeMax: 500 * 1024 * 1024, // 500 mb upload limit
			appendCookieData: true,
			onSelectSuccess: this.onSelectSuccess.bind(this),
			onSelectFail: this.onSelectFail.bind(this),
			onQueue: this.onQueue.bind(this),
			onFileComplete: this.onFileComplete.bind(this),
			onComplete: this.onComplete.bind(this)
		});

		// Set up the focus/blur and reposition events for the uploader Flash object
		this.browseButton.addEvents({
			mouseenter: function() {
				this.browseButton.removeClass('active');
				this.browseButton.addClass('browse-button-hover');
				this.uploader.reposition();
			}.bind(this),
			mouseleave: function() {
				this.browseButton.removeClass('browse-button-hover');
				this.browseButton.addClass('active');
//				this.uploader.blur();
			}.bind(this),
			mousedown: function() {
//				this.uploader.focus();
			}.bind(this)
		});

		// Set the default onclick event for the upload button
		this.uploadButton.addEvent('click', function() {
			this.startUpload();
		}.bind(this));

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
		finput.parentNode.parentNode.getPrevious().destroy();
		finput.parentNode.parentNode.destroy();
		submit.parentNode.parentNode.getPrevious().destroy();
		submit.parentNode.parentNode.destroy();
	},

	// returns a dict with all the form fields/values,
	// in the format of the data object for Request objects
	getFormValues: function() {
		var values = {};
		$$(this.form.elements).each(function(el) {
			values[el.get('name')] = el.get('value');
		});
		return values;
	},

	// callback for validation AJAX request, which is fired when the submit button is pressed
	validated: function(responseJSON) {
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
		this.statusDiv.getChildren()[1].set('html', (p>=1?p-1:p) + '%');
	},

	// called by the uploader when selecting a file fails. eg. if it's too big.
	onSelectFail: function(files) {
		// console.log(files[0].name, files[0].validationError);
	},

	// called by the uploader when selecting a file from the browse box succeeds
	onSelectSuccess: function(files) {
		this.setEnabled(true);
		this.fileInfoDiv.set('html', 'You chose: <span class="filename">'+files[0].name+' ('+Swiff.Uploader.formatUnit(files[0].size, 'b')+')</span>');
	},

	// called by the uploader when a file upload is completed
	onFileComplete: function(file) {
		if (file.response.error) {
			this.redirectFailure(this.uploader.fileList[0].response.code);
		} else {
			var json = JSON.decode(file.response.text, true)
			if (json.success) {
				this.statusDiv.getChildren()[0].set('html', 'Success! You will be redirected shortly.');
				this.statusDiv.getChildren()[1].set('html', '100%');
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
			this.uploadButton.addClass('enabled');
		} else {
			this.uploader.setEnabled(true);
			this.enabled = false;
			this.uploadButton.removeClass('enabled');
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


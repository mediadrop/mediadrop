var Uploader = new Class({

	Extends: Options,

	options: {
		target: null,
		uploadBtn: {text: 'Upload a file', 'class': 'mo btn-upload'},
		statusContainer: null,
		statusFile: '.upload-file',
		statusProgress: '.upload-progress',
		statusError: '.upload-error',
		fxProgressBar: {},
		uploader: {
			verbose: false,
			queued: false,
			multiple: false,
			target: null,
			instantStart: true,
			typeFilter: '*.*',
			fileSizeMax: 50 * 1024 * 1024,
			appendCookieData: true
		}
	},

	target: null,
	fxProgress: null,

	ui: {
		file: null,
		progress: null,
		error: null
	},

	initialize: function(options){
		this.setOptions(options);
		var uploaderOpts = this.options.uploader;

		this.target = $(this.options.target) || $(this.options.uploader.target);
		if (this.target.get('type') == 'file') {
			uploaderOpts.fieldName = this.target.get('name');
			uploaderOpts.url = this.target.form.get('action');
			this.target = this._createUploadBtn().replaces(this.target);
		}
		uploaderOpts.target = this.target;

		this.uploader = new Swiff.Uploader(uploaderOpts).addEvents({
			browse: this.onBrowse.bind(this),
			selectSuccess: this.onSelectSuccess.bind(this),
			selectFail: this.onSelectFail.bind(this),
			queue: this.onQueue.bind(this),
			fileComplete: this.onFileComplete.bind(this),
			fileError: this.onFileError.bind(this),
			buttonEnter: this.onButtonEnter.bind(this),
			buttonLeave: this.onButtonLeave.bind(this)
		});

		this.ui.container = $(this.options.statusContainer);
		this.ui.file = this.ui.container.getElement(this.options.statusFile);
		this.ui.progress = this.ui.container.getElement(this.options.statusProgress);
		this.ui.error = this.ui.container.getElement(this.options.statusError);
	},

	onBrowse: function(){
//		this.clearStatusBar();
	},

	clearStatusBar: function(){
		this.ui.file.empty();
		if (this.ui.progress) this.progress.set(0).element.hide();
	},

	onSelectSuccess: function(files){
		var file = files[0];
		this._displayFile(file);
		if (this.ui.error) {
			this.ui.error.slide('out').empty.delay(100, this.ui.error);
		}
		if (!this.fxProgress) {
			this.fxProgress = new Fx.ProgressBar(this.ui.progress.getElement('img'), this.options.fxProgressBar);
		}
		this.fxProgress.set(0);
		this.ui.progress.slide('hide').show().slide('in');
		this.uploader.setEnabled(false);
	},

	onSelectFail: function(files){
		var file = files[0];
		this._displayFile(file);
		if (this.fxProgress) {
			this.fxProgress.set(0);
		}
		this.ui.progress.hide();
		var errorMsg = MooTools.lang.get('FancyUpload', 'validationErrors')[file.validationError] || '{error} #{code}';
		var error = errorMsg.substitute($extend({
			fileSizeMin: Swiff.Uploader.formatUnit(this.uploader.options.fileSizeMin, 'b'),
			fileSizeMax: Swiff.Uploader.formatUnit(this.uploader.options.fileSizeMax, 'b')
		}, file));
		this.uploader.fireEvent('fileError', [file, null, error]);
	},

	onQueue: function(){
		if (this.fxProgress) this.fxProgress.set(this.uploader.percentLoaded);
	},

	onFileComplete: function(file){
		file.remove();
		this.uploader.setEnabled(true);
		if (this.fxProgress) {
			this.fxProgress.set(100);
		}
		if (file.response.error) {
			var errorMsg = MooTools.lang.get('FancyUpload', 'errors')[file.response.error] || '{error} #{code}';
			var error = errorMsg.substitute($extend({name: file.name}, file.response));
			return this.uploader.fireEvent('fileError', [file, file.response, error]);
		}
		var json = JSON.decode(file.response.text, true);
		if (!json.success) {
			return this.uploader.fireEvent('fileError', [file, file.response, json.message]);
		}
		this.ui.file.getElement('.upload-file-size').highlight();
		this.ui.container.highlight();
		this.ui.file.slide.delay(500, this.ui.file, ['out']);
		this.ui.progress.slide.delay(500, this.ui.progress, ['out']);
	},

	_displayFile: function(file){
		var fileName = new Element('span', {
			'class': 'upload-file-name',
			text: file.name
		})
		var fileSize = new Element('span', {
			'class': 'upload-file-size',
			text: '(' + Swiff.Uploader.formatUnit(file.size, 'b') + ') '
		});
		this.ui.file.empty()
			.grab(fileName).grab(fileSize)
			.slide('hide').show().slide('in');
	},

	onFileError: function(file, response, errorMsg){
		this.ui.error.addClass('box-error').removeClass('inprogress')
			.set('html', errorMsg)
			.slide('hide').show().slide('in').highlight();
	},

	onButtonEnter: function(){
		this.target.setStyle('background-position', 'bottom');
	},

	onButtonLeave: function(){
		this.target.setStyle('background-position', 'top');
	},

	_createUploadBtn: function(){
		return new Element('span', this.options.uploadBtn);
	}

});

var AlbumArtUploader = new Class({

	Extends: Uploader,

	options: {
		image: '',
		updateFormActionsOnSubmit: false,
		uploader: {
			fileSizeMax: 10 * 1024 * 1024,
//			typeFilter: '*.jpg; *.jpeg; *.gif; *.png'
		}
	},

	image: null,

	onFileComplete: function(file){
		this.parent(file);
		if (!file.response.error){
			this.image = this.image || $(this.options.image);
			if (!this.image) return;
			var json = JSON.decode(file.response.text, true);
			if (json.success) {
				var src = this.image.get('src'), newsrc = src.replace(/\/new/, '/' + json.id);
				this.image.set('src', newsrc + '?' + $time());
				if (this.options.updateFormActionsOnSubmit && src != newsrc) {
					// Update the form actions on the page to point to refer to the newly assigned ID
					this.updateFormActions(json.id);
				}
			}
		}
	},

	updateFormActions: function(id){
		var find = /\/new\//, repl = '/' + id + '/';
		this.uploader.setOptions({
			url: this.uploader.options.url.replace(find, repl)
		});
		$$('form').each(function(form){
			form.action = form.action.replace(find, repl);
		});
	}

});


MooTools.lang.set('en-US', 'FancyUpload', {
	errors: {
		httpStatus: 'Server returned HTTP-Status #{code}',
		securityError: 'Security error occured ({text})',
		ioError: 'Error caused a send or load operation to fail ({text})'
	},
	validationErrors: {
		duplicate: 'File has already been added, duplicates are not allowed.',
		sizeLimitMin: 'File is too small, the minimal file size is {fileSizeMin}.',
		sizeLimitMax: 'File is too large, the maximum file size is <em>{fileSizeMax}</em>.',
		fileListMax: 'File could not be added, amount of <em>{fileListMax} files</em> exceeded.',
		fileListSizeMax: 'File is too big, overall filesize of <em>{fileListSizeMax}</em> exceeded.'
	}
});

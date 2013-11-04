/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

var UploaderBase = new Class({

	Extends: Swiff.Uploader,

	options: {
		uploadBtn: {'class': 'btn grey'},
		uploadBtnText: 'Upload a file',
		postAuthCookie: 'authtkt',
		verbose: false,
		queued: false,
		multiple: false,
		target: null,
		instantStart: true,
		typeFilter: '*.*',
		fileSizeMax: 50 * 1024 * 1024, // default max size of 50 MB
		appendCookieData: false,
		data: {},
		timeLimit: 60
	},

	initialize: function(options){
		this.setOptions(options);
		if (this.options.postAuthCookie) {
			this.options.data[this.options.postAuthCookie] = Cookie.read(this.options.postAuthCookie);
		}

		this.target = $(this.options.target);
		if (this.target.get('type') == 'file') {
			this.options.fieldName = this.target.get('name');
			this.options.url = this.target.form.get('action');
			this.target = this._createUploadBtn().replaces(this.target);
		}
		this.options.target = this.target;

		this.parent();

		this.addEvents({
			buttonEnter: this.onButtonEnter.bind(this),
			buttonLeave: this.onButtonLeave.bind(this),
			browse: this.onButtonClick.bind(this),
			select: this.onButtonReset.bind(this),
			cancel: this.onButtonReset.bind(this)
		});
	},

	onButtonEnter: function(){
		if (this.target) this.target.addClass('hover');
	},

	onButtonLeave: function(){
		if (this.target) this.target.removeClass('hover');
	},

	onButtonClick: function(){
		if (this.target) this.target.addClass('active');
	},

	onButtonReset: function(){
		if (this.target) this.target.removeClass('active');
	},

	_createUploadBtn: function(){
		return new Element('span', this.options.uploadBtn).grab(new Element('span', {text: this.options.uploadBtnText}));
	},

	reposition: function(coords) {
		// fix a logic bug when target is null
		coords = coords || (this.target && this.target.offsetHeight
			? this.target.getCoordinates(this.box.getOffsetParent())
			: {top: window.getScrollTop(), left: 0, width: 1, height: 1});
		this.box.setStyles(coords);
		this.fireEvent('reposition', [coords, this.box, this.target]);
	}

});

var Uploader = new Class({

	Extends: UploaderBase,

	options: {
		statusContainer: null,
		statusFile: '.upload-file',
		statusProgress: '.upload-progress',
		statusError: '.upload-error',
		statusNotice: '.upload-notice',
		fxProgressBar: {},
		messages: {}
	},

	fxProgress: null,

	ui: {
		file: null,
		progress: null,
		error: null
	},

	initialize: function(options){
		this.parent(options);

		this.messages = {};
		for (x in this.options.messages) {
			this.messages[x] = [this.options.messages[x], false];
		}

		this.addEvents({
			selectSuccess: this.onSelectSuccess.bind(this),
			selectFail: this.onSelectFail.bind(this),
			fileComplete: this.onFileComplete.bind(this),
			fileProgress: this.onFileProgress.bind(this),
			error: this.onError.bind(this) // not a Swiff.Uploader event
		});

		this.ui.container = $(this.options.statusContainer);
		this.ui.file = this.ui.container.getElement(this.options.statusFile);
		this.ui.progress = this.ui.container.getElement(this.options.statusProgress);
		this.ui.error = this.ui.container.getElement(this.options.statusError);
		this.ui.notice = this.ui.container.getElement(this.options.statusNotice);
	},

	clearStatus: function(){
		this.ui.file.empty().slide('hide').show();
		this.ui.progress.slide('hide').show();
		this.ui.error.slide('hide').show();
		this.ui.notice.slide('hide').show();
	},

	onSelectSuccess: function(files){
		var file = files[0];
		this._displayFile(file);
		if (this.ui.error) {
			this.ui.error.slide('out');
		}
		if (!this.fxProgress) {
			this.fxProgress = new Fx.ProgressBar(this.ui.progress.getElement('img'), this.options.fxProgressBar);
		}
		this.fxProgress.set(0);
		this.ui.progress.slide('hide').show().slide('in');
		this.setEnabled(false);
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
			fileSizeMin: Swiff.Uploader.formatUnit(this.options.fileSizeMin, 'b'),
			fileSizeMax: Swiff.Uploader.formatUnit(this.options.fileSizeMax, 'b')
		}, file));
		this.fireEvent('error', [error]);
	},

	onFileComplete: function(file){
		file.remove();
		this.setEnabled(true);
		if (this.fxProgress) {
			this.fxProgress.set(100);
		}
		if (file.response.error) {
			var errorMsg = MooTools.lang.get('FancyUpload', 'errors')[file.response.error] || '{error} #{code}';
			var error = errorMsg.substitute($extend({name: file.name}, file.response));
			return this.fireEvent('error', [error]);
		}
		var json = JSON.decode(file.response.text, true);
		if (!json.success) {
			return this.fireEvent('error', [json.message]);
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

	onError: function(msg){
		this.ui.error.addClass('box-error').removeClass('inprogress')
			.set('text', msg)
			.slide('hide').show().slide('in').highlight();
	},

	onFileProgress: function(){
		var p = this.percentLoaded;
		if (this.fxProgress) this.fxProgress.set(p);

		// Iterate over all messages, displaying them if necessary.
		if (this.ui.notice) {
			for (x in this.messages) {
				// If this message has not been displayed yet
				// and this message should be displayed at this point
				var msg = this.messages[x];
				if (!msg[1] && x <= p) {
					msg[1] = true;
					this.ui.notice.show().set('html', msg[0]).slide('in');
				}
			}
		}
	}

});

var ThumbUploader = new Class({

	Extends: Uploader,

	options: {
		image: '',
		fileSizeMax: 10 * 1024 * 1024,
		typeFilter: '*.jpg; *.jpeg; *.gif; *.png',
		uploadBtn: {'class': 'btn block'},
		uploadBtnText: 'Upload image'
	},

	initialize: function(options){
		this.parent(options);
		this.image = $(this.options.image);
	},

	onFileComplete: function(file){
		this.parent(file);
		if (!file.response.error){
			var json = JSON.decode(file.response.text, true);
			if (json.success) {
				if (json.id) this.setNewID(json.id);
				this.refreshThumb();
			}
		}
	},

	setNewID: function(id){
		var src = this.image.get('src'), newsrc = src.replace(/\/new([sml])\.(jpg|png)/, '/' + id + '$1.$2');
		if (newsrc && src != newsrc) this.image.set('src', newsrc);
		return this;
	},

	refreshThumb: function(){
		var src = this.image.get('src'), qsStart = src.indexOf('?');
		if (qsStart > 0) src = src.substr(0, qsStart);
		this.image.set('src', src + '?' + $time());
		return this;
	}

});


MooTools.lang.set('en-US', 'FancyUpload', {
	errors: {
		httpStatus: 'Saving the file failed. Please try again',
		securityError: 'Security error occured ({text})',
		ioError: 'Error caused a send or load operation to fail ({text})'
	},
	validationErrors: {
		duplicate: 'File has already been added, duplicates are not allowed',
		sizeLimitMin: 'File is too small, the minimal file size is {fileSizeMin}',
		sizeLimitMax: 'File is too large, the maximum file size is {fileSizeMax}',
		fileListMax: 'File could not be added, amount of {fileListMax} files exceeded',
		fileListSizeMax: 'File is too big, overall filesize of {fileListSizeMax} exceeded'
	}
});

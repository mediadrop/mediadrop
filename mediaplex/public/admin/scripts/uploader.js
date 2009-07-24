var Uploader = new Class({

	Extends: Options,

	options: {
		target: null,
		uploadBtn: {text: 'Upload a file', 'class': 'mo btn-upload'},
		statusBar: null,
		progressBar: null,
		progressBarOptions: {},
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
	statusBar: null,
	statusFile: null,
	progressBar: null,

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
			buttonEnter: this.onButtonEnter.bind(this),
			buttonLeave: this.onButtonLeave.bind(this)
		});

		this.statusBar = $(this.options.statusBar).slide('hide');
		this.statusFile = $(this.options.statusFile);
	},

	onBrowse: function(){
		this.clearStatusBar();
	},

	clearStatusBar: function(){
		this.statusFile.empty();
		if (this.progressBar) this.progressBar.set(0).element.setStyle('display', 'none');
	},

	onSelectSuccess: function(files){
		var file = files[0];
		this.statusFile.grab(new Element('span', {
			text: '(' + Swiff.Uploader.formatUnit(file.size, 'b') + ') '
		})).appendText(file.name);
		if (!this.progressBar) this.progressBar = new Fx.ProgressBar(this.options.progressBar, this.options.progressBarOptions).set(0);
		this.progressBar.element.setStyle('display', 'block');
		this.statusBar.slide('in');
		this.uploader.setEnabled(false);
	},

	onSelectFail: function(files){
		var file = files[0];
		this.statusFile.grab(new Element('span', {
			text: '(' + Swiff.Uploader.formatUnit(file.size, 'b') + ') '
		})).appendText(file.name);
		console.log(files[0].name + ' was not added! (Error: #' + files[0].validationError + ')');
		this.statusBar.setStyle('display', 'block');
	},

	onQueue: function(){
		this.progressBar.set(this.uploader.percentLoaded);
	},

	onFileComplete: function(file){
		file.remove();
		this.uploader.setEnabled(true);
		this.progressBar.set(100);
		this.statusBar.slide.delay(500, this.statusBar, ['out']);
/*		if (file.response.error) {
			this.uploader.setEnabled(true);
			this._displayControls('block');
			this.statusBar.addClass('error').removeClass('inprogress')
				.set('html', this.uploader.fileList[0].name + ' failed to upload. Please try again. '
					+ '(Error: #' + this.uploader.fileList[0].response.code + ' '
					+ this.uploader.fileList[0].response.error + ')')
				.highlight();
		} else {
			this.statusBar.addClass('success').removeClass('inprogress')
				.set('html', this.uploader.fileList[0].name + ' uploaded successfully!').highlight();
		}*/
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
		updateFormActionsOnSubmit: false
	},

	image: null,

	onFileComplete: function(file){
		this.parent(file);
		this.image = this.image || $(this.options.image);
		if (!this.image) return;
		var json = JSON.decode(file.response.text, true);
		var src = this.image.get('src'), newsrc = src.replace(/\/new/, '/' + json.id);
		this.image.set('src', newsrc + '?' + $time());
		if (this.options.updateFormActionsOnSubmit && src != newsrc) {
			// Update the form actions on the page to point to refer to the newly assigned ID
			this.updateFormActions(json.id);
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

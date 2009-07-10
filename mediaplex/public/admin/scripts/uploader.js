var Uploader = new Class({

	Extends: Options,

	options: {
		target: null,
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

		this.statusBar = $(this.options.statusBar);
		this.statusFile = $(this.options.statusFile);
	},

	onBrowse: function(){
		this.statusBar.setStyle('display', 'none');
		this.progressBar
	},

	onSelectSuccess: function(files){
		var file = files[0];
		this.statusFile.set('text', file.name).grab(new Element('div', {
			text: ' (' + Swiff.Uploader.formatUnit(files[0].size, 'b') + ')'}), 'bottom');
		this.progressBar = new Fx.ProgressBar(this.options.progressBar, this.options.progressBarOptions).set(0);
		this.progressBar.element.setStyle('display', 'block');
		this.statusBar.setStyle('display', 'block');
		this.uploader.setEnabled(false);
	},

	onSelectFail: function(files){
		console.log(files[0].name + ' was not added! (Error: #' + files[0].validationError + ')');
		this.statusBar.setStyle('display', 'block');
	},

	onQueue: function(){
		console.log('percent ' + this.uploader.percentLoaded);
		this.progressBar.set(this.uploader.percentLoaded);
	},

	onFileComplete: function(file){
		file.remove();
		this.uploader.setEnabled(true);
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
		return new Element('span', {text: 'Upload a file', 'class': 'mo btn-upload'});
	}
});

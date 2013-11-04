/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

var MediaManager = new Class({

	Implements: [Events],

	initialize: function(opts){
		this.metaForm = opts.metaForm.addEvents({
			saveSuccess: this.onMetaSaved.bind(this)
		});
		this.statusForm = opts.statusForm.addEvents({
			onUpdate: this.updateSlugifier.bind(this)
		});
		this.fileUploader = opts.fileUploader;
		this.thumbUploader = opts.thumbUploader;
		this.thumbUploader.addEvents({
			fileComplete: this.onThumbUpload.bind(this)
		});
		this.files = opts.files.addEvents({
			fileAdded: this.onFileAdded.bind(this),
			fileEdited: this.updateStatusForm.bind(this),
			fileDeleted: this.updateStatusForm.bind(this)
		});
		this.isNew = !!opts.isNew;
		this.newID = null;
		this.mergeURL = opts.mergeURL;
		this.type = opts.type;
		this.head = $(opts.head);
		this.updateSlugifier();
	},

	initNewMedia: function(mediaID){
		this.isNew = false;
		this.newID = mediaID;
		window.location.hash = '#' + mediaID;
		this.fireEvent('initMedia', [mediaID]);
	},

	onMetaSaved: function(json){
		if (this.isNew) {
			this.initNewMedia(json.media_id);
			this.updateFormActions(json.media_id);
		}
		if (this.newID && this.newID != json.media_id) {
			this.mergeMedia(json.media_id);
		} else {
			this.updateStatusForm(json.status_form);
			this.updateTitle(json.values.title, json.link);
		}
	},

	onThumbUpload: function(file){
		var json = JSON.decode(file.response.text, true);
		if (this.isNew) {
			this.initNewMedia(json.id);
			this.setStubData(json.title, json.slug, json.link);
			this.updateFormActions(json.id);
		}
		if (this.newID && this.newID != json.id) {
			this.mergeMedia(json.id);
		}
	},

	onFileAdded: function(json){
		// XXX: mergeMedia calls fileAdded directly, which triggers this event an extra time
		if (this.isNew) {
			this.initNewMedia(json.media_id);
			this.updateFormActions(json.media_id);
			this.thumbUploader.setNewID(json.media_id);
		}
		if (this.newID && this.newID != json.media_id) {
			this.mergeMedia(json.media_id);
		} else if ($defined(json.slug)) {
			this.setStubData(json.title, json.slug, json.link, json.description);
			this.updateStatusForm(json.status_form);
		}
		this.thumbUploader.refreshThumb();
	},

	onFileEdited: function(json){
		this.updateStatusForm(json.status_form);
	},

	mergeMedia: function(mediaID){
		var r = new Request.JSON({url: this.mergeURL, onSuccess: this.onMediaMerged.bind(this)});
		r.send('orig_id=' + this.newID + '&input_id=' + mediaID);
	},

	onMediaMerged: function(json){
		if (!json.success) return alert(json.message);
		this.updateStatusForm(json.status_form);
		this.updateTitle(json.title, json.link);
		new Hash(json.file_forms).each(function(xhtml, id){
			var pseudoresp = {success: true, media_id: this.newID};
			var row = Elements.from(xhtml)[0];
			var replaces = $(this.files._getFileID(id));
			this.files.fileAdded(pseudoresp, replaces, row);
		}, this);
		this.thumbUploader.refreshThumb();
	},

	setStubData: function(title, slug, link, desc){
		var slugObj = this.metaForm.slug;
		if (!slugObj.field.value || slugObj.field.value.match(/^_stub_/)) {
			slugObj.setSlug(slug);
			this.metaForm.form.title.value = title;
		}
		if (desc) $(this.metaForm.form.description).set('fieldValue', desc);
		this.updateTitle(title, link);
	},

	updateTitle: function(title, link){
		if (!title) return;
		if (link && !(new String(window.location).match(new RegExp(link.escapeRegExp())))) {
			var el = new Element('a', {href: link});
		} else {
			var el = new Element('span');
		}
		this.head.empty().adopt(el.set('text', title));
		var i = document.title.lastIndexOf(' | '), suffix = (i > 0 ? document.title.substr(i) : '');
		document.title = 'Edit: ' + title + suffix;
	},

	updateFormActions: function(mediaID){
		var find = /\/new\//, repl = '/' + mediaID + '/';
		this.metaForm.form.action = this.metaForm.form.action.replace(find, repl);
		this.statusForm.form.action = this.statusForm.form.action.replace(find, repl);
		this.thumbUploader.setOptions({
			url: this.thumbUploader.options.url.replace(find, repl)
		});
		this.fileUploader.setOptions({
			url: this.fileUploader.options.url.replace(find, repl)
		});
		this.files.addForm.action = this.files.addForm.action.replace(find, repl);
		this.files.options.editURL = this.files.options.editURL.replace(find, repl);
	},

	updateStatusForm: function(resp){
		if (resp && resp.status_form) resp = resp.status_form;
		if ($type(resp) != 'string' || !resp) return;
		this.statusForm.updateForm(Elements.from(resp)[0]);
	},

	updateSlugifier: function(form, json){
		if (this.statusForm.isPublished()) this.metaForm.slug.detachSlugifier();
		else this.metaForm.slug.attachSlugifier();
		if (json && $defined(json.slug)) this.metaForm.slug.setSlug(json.slug);
	}

});

var MediaMetaForm = new Class({

	Extends: BoxForm,

	initialize: function(el, opts){
		this.parent(el, opts);
		var podSelect = $(this.form.elements['podcast']);
		if ((podSelect.type == 'hidden' && $$('#podcast-dropdown ol li').length <= 1) || (podSelect.options && podSelect.options.length <= 1)) {
			podSelect.getParent('li').hide();
		}
		this.notesArea = new DynamicTextarea(this.form.elements['notes']);
		var desc = $(this.form.elements['description']);
		if (!desc.hasClass('tinymcearea')) {
			this.descArea = new DynamicTextarea(desc, {minRows: 4});
		}
	}

});

var StatusForm = new Class({

	Implements: [Options, Events],

	options: {
		form: '',
		error: '',
		submitReq: {noCache: true},
		publishPickerField: 'publish_on',
		publishToggleOn: 'status-publish',
		expiryPickerField: 'publish_until',
		expiryToggleOn: 'status-expiry',
		pickerOptions: {
			yearPicker: false,
			timePicker: true,
			allowEmpty: true,
			format: '%b %d %Y @ %H:%M'
		},
		connectionErrorText: 'A connection problem occurred, try again.',
		genericErrorText: 'An error has occurred, try again.'
	},

	form: null,
	submitReq: null,
	publishDatePicker: null,
	expiryDatePicker: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.saveStatus.bind(this));
		this.attachDatePickers();
	},
    
    attachDatePickers: function() {
        this.attachPublishDatePicker();
        this.attachExpiryDatePicker();
    },
    
	attachPublishDatePicker: function() {
	    var toggleID = this.options.publishToggleOn;
	    this.publishDatePicker = this.attachDatePicker(this.publishDatePicker, 
	        this.options.publishPickerField, toggleID, this.changePublishDate);
	},
	
	attachExpiryDatePicker: function() {
	    var toggleID = this.options.expiryToggleOn;
	    this.expiryDatePicker = this.attachDatePicker(this.expiryDatePicker, 
	        this.options.expiryPickerField, toggleID, this.changeExpiryDate);
	},
	
	attachDatePicker: function(picker, pickerFieldName, toggleID, selectCallback){
		var toggle = $(toggleID);
		if (!toggle) 
		    return picker;
	    if (picker === null) {
	        this.options.pickerOptions.toggle = toggleID;
	        return new DatePicker(pickerFieldName, this.options.pickerOptions)
				.addEvent('select', selectCallback.bind(this))
	    }
	    return picker.attach(pickerFieldName, toggle);
	},

	saveStatus: function(e){
		e = new Event(e).stop();
		if (!this.submitReq) {
			var submitOpts = $extend({url: this.form.action}, this.options.submitReq);
			this.submitReq = new Request.JSON(submitOpts).addEvents({
				success: this.statusSaved.bind(this),
				failure: this._displayError.bind(this, [this.options.connectionErrorText])
			});
		}
		var data = this.form.toQueryString();
		this.submitReq.send(data);
	},

	statusSaved: function(json){
		json = json || {};
		if (json.success) this.updateForm(json.status_form, json);
		else this._displayError(json.message);
	},

	updateForm: function(form, json){
		if ($type(form) == 'string') {
			form = new Element('div', {html: form}).getFirst();
		}
		var formContents = $(form).getChildren();
		this.form.empty().adopt(formContents);
		this.attachDatePickers();
		this.fireEvent('update', [this.form, json]);
	},

	_displayError: function(msg){
		var errorBox = $(this.options.error);
		errorBox.set('html', msg || this.options.genericErrorText);
		if (!errorBox.isDisplayed()) errorBox.slide('hide').show().slide('in');
		errorBox.highlight();
	},

	changePublishDate: function(d){
		var publishDate = d.format(this.options.pickerOptions.format);
		$(this.publishDatePicker.options.toggle).getFirst().set('text', publishDate);

		var r = new Request.JSON({
			url: this.form.get('action'),
			onComplete: this.statusSaved.bind(this)
		}).send(new Hash({
			publish_on: publishDate,
			update_button: 'Change publish date'
		}).toQueryString());
	},
	
	changeExpiryDate: function(d) {
		var expiryDate = d.format(this.options.pickerOptions.format);
		$(this.expiryDatePicker.options.toggle).getFirst().set('text', expiryDate);
		
		var r = new Request.JSON({
			url: this.form.get('action')
		}).send(new Hash({
			publish_until: expiryDate,
			update_button: 'Change expiry date'
		}).toQueryString());
	},

	isPublished: function(){
		return this.form.elements['is_published'].value == '1';
	}
});

var DimensionOverText = new Class({

	Extends: OverText,

	test: function(){
		var v = this.element.get('value');
		if (v == '0x0') v = '';
		return !v;
	}

});

var FileManager = new Class({

	Implements: [Events, Options],

	options: {
	/*	onFileAdded: function(json, row)
		onFileEdited: function(json, row, target),
		onFileDeleted: function(json, row), */
		editURL: '',
		modal: {
			squeezeBox: {
				zIndex: 10000,
				size: {x: 830, y: 450}
			}
		},
		deleteConfirmMsg: function(name){ return "Are you sure you want to delete this file?\n\n" + name; },
		uploadQueueRow: {'class': 'uploading'},
		uploadCancelBtn: {
			'class': 'file-delete',
			type: 'submit',
			value: 'Cancel upload',
			name: 'cancel'
		},
		errorDiv: {'class': 'file-error'},
		uploader: {
			allowDuplicates: true,
			multiple: true,
			queued: 1,
			zIndex: 65555
		},
		overtext: {
			textOverride: '-'
		},
		addError: 'Failed to add this file. Please try again.',
		saveError: 'Failed to save your change. Please try again.',
		uploadingText: 'Uploading',
		queuedText: 'Queued',
		errorText: 'Error'
	},

	files: [],
	durationInputs: [],
	overtexts: [],

	initialize: function(container, opts){
		this.setOptions(opts);
		this.container = $(container);
		this.addForm = $(this.options.addForm);
		this.uploader = new UploaderBase(this.options.uploader);
		this.modal = new Modal(this.container, this.options.modal);
		this.thead = this.container.getElement('table thead');
		this.tbody = this.container.getElement('table tbody');
		this.files = this.tbody.getChildren();
		this.updateDisplay();
		this.urlOverText = new OverText('url', {wrap: true});
		this.attach();
	},

	attach: function(){
		this.addForm.addEvent('submit', this.addFile.bind(this));
		this.addForm.url.addEvent('focus', this.addForm.url.select);
		this.files.each(this._attachFile.bind(this));
		this._attachModal(this.modal);
		this._attachUploader(this.uploader);
		return this;
	},

	_attachFile: function(row){
		row.getElement('button.file-delete').addEvent('click', this.editFile.bind(this));
		var typeSelect = row.getElement('select[name=file_type]');
		var dropdown = new DropdownSelect(typeSelect).addEvent('change', this.editFile.bind(this));
		row.getElements('input[class=textfield]').addEvents({
			blur: this.editFile.bind(this),
			keydown: function(e){
				e = new Event(e);
				if (e.key == 'enter') this.editFile(e);
			}.bind(this)
		});
		// Custom handling for the duration row.
		var duration = row.getElement('input[name=duration]');
		duration.addEvent('keyup', this.syncDurations.bind(this));
		this.durationInputs.push(duration);
		// Custom handling for the width x height row
		var wxh = row.getElement('input[name=width_height]');
		wxh.meiomask('Regexp.widthxheight', {});
		// Default labels when no value is entered
		var otOpts = this.options.overtext;
		this.overtexts.push(new OverText(duration, otOpts));
		this.overtexts.push(new OverText(row.getElement('input[name=bitrate]'), otOpts));
		this.overtexts.push(new DimensionOverText(wxh, otOpts));
		return row;
	},

	_attachUploader: function(uploader){
		// Hide the uploader when the modal isn't open
		return uploader.addEvents({
			selectSuccess: this.onUploadSelectSuccess.bind(this),
			selectFail: this.onUploadSelectFail.bind(this),
			fileStart: this.onFileUploadStart.bind(this),
			fileProgress: this.onFileUploadProgress.bind(this),
			fileComplete: this.onFileUploadComplete.bind(this),
			fileRemove: this.onFileQueueRemove.bind(this)
		});
	},

	_attachModal: function(modal){
		this.onClose();
		return this.modal.addEvents({
			open: this.onOpen.bind(this),
			close: this.onClose.bind(this)
		});
	},

	open: function(){
		this.modal.open();
		return this;
	},

	close: function(){
		this.modal.close();
		return this;
	},

	onOpen: function(){
		this.uploader.target = this.uploader.options.target;
		this.uploader.reposition();
		this.urlOverText.reposition();
		this._repositionOverTexts.delay(300, this);
	},

	_repositionOverTexts: function(){
		this.urlOverText.reposition();
		this.overtexts.each(function(ot){ ot.reposition(); });
	},

	onClose: function(){
		this.uploader.target = null;
		this.uploader.reposition();
		this.urlOverText.reposition();
	},

	addFile: function(e){
		var e = new Event(e).preventDefault(), form = $(e.target);
		var fileSpoof = new Hash({ // a Swiff.Uploader.File-like obj, see this.onFileQueue
			name: form.url.get('value'),
			size: '-',
			typeText: 'Saving'
		});
		var row = this._createQueueRow(fileSpoof).inject(this.tbody).highlight();
		this.updateDisplay();
		var req = new Request.JSON({
			url: form.get('action'),
			onSuccess: this.fileAdded.bindWithEvent(this, [row]),
			onFailure: this._injectError.bind(this, [row, this.options.addError])
		});
		req.addEvent('success', function(){
			form.url.set('value', '').blur();
			this.urlOverText.reposition();
		}.bind(this));
		req.send(form.toQueryString());
	},

	fileAdded: function(resp, replaces, row){
		if (!row) {
			if (!resp.success) this._injectError(replaces, resp.message);
			row = Elements.from(resp.edit_form)[0];
		}
		row = this._attachFile(row);
		this.files.push(row);
		if (replaces) row.replaces(replaces);
		else row.inject(this.tbody);
		this.updateDisplay();
		if (resp.duration) this.syncDurations(resp.duration);
		row.highlight();
		return this.fireEvent('fileAdded', [resp, row, replaces]);
	},

	editFile: function(eOrTarget, el){
		if (el) var target = el;
		else if ($type(eOrTarget) == 'event') var target = $(eOrTarget.target);
		else var target = $(eOrTarget);
		var row = target.getParent('tr');
		var oldError = row.retrieve('fileError');
		if (oldError) oldError.destroy();
		if (target.get('name') == 'delete') {
			eOrTarget.stop();
			var name = row.getElement('td[headers="thf-name"]').get('text').trim();
			var msg = $lambda(this.options.deleteConfirmMsg)(name);
			if (!confirm(msg)) return false;
			var value = true;
		} else {
			var value = target.get('value');
		}
		row.className = 'saving';
		var data = new Hash({file_id: this._getFileID(row)})
			.set(target.get('name'), value);
		var r = new Request.JSON({
			url: this.options.editURL,
			data: data,
			onSuccess: this.fileEdited.bindWithEvent(this, [target]),
			onFailure: this._injectError.bind(this, [row, this.options.saveError])
		}).send();
	},

	fileEdited: function(json, target){
		json = json || {};
		var row = target.getParent('tr');
		if (!json.success) return this._injectError(row, json.message);
		if (target.get('name') == 'delete') {
			this.files.erase(row);
			row.dispose();
			this.updateDisplay();
			return this.fireEvent('fileDeleted', [json, row]);
		} else {
			if (json.duration) this.syncDurations(json.duration);
			row.className = json.file_type;
			return this.fireEvent('fileEdited', [json, row, target]);
		}
	},

	syncDurations: function(eOrValue){
		if ($type(eOrValue) == 'event') var e = new Event(eOrValue), target = $(e.target), value = target.get('value');
		else var target, value = eOrValue;
		for (var input, i = 0, l = this.durationInputs.length; i < l; i++) {
			input = this.durationInputs[i];
			if (input != target) input.set('value', value);
		}
	},

	onUploadSelectSuccess: function(files){
		for (var i = 0; i < files.length; i++) this.onFileQueue(files[i]);
	},

	onUploadSelectFail: function(files){
		for (var i = 0; i < files.length; i++) this.onFileQueueError(files[i]);
	},

	onFileQueue: function(file){
		var row = this._createQueueRow(file).inject(this.tbody).highlight();
		this.updateDisplay();
		this.fireEvent('fileQueued', [row, file]);
	},

	onFileQueueError: function(file){
		var row = this._createQueueRow(file);
		var msg = MooTools.lang.get('FancyUpload', 'validationErrors')[file.validationError] || file.validationError;
		this._injectError(row, msg.substitute({
			name: file.name,
			size: file.ui.size.get('text'),
			fileSizeMin: Swiff.Uploader.formatUnit(this.uploader.options.fileSizeMin || 0, 'b'),
			fileSizeMax: Swiff.Uploader.formatUnit(this.uploader.options.fileSizeMax || 0, 'b'),
			fileListMax: this.uploader.options.fileListMax || 0,
			fileListSizeMax: Swiff.Uploader.formatUnit(this.uploader.options.fileListSizeMax || 0, 'b')
		}));
		file.ui.type.set('text', 'Error');
		row.inject(this.tbody).highlight();
		this.updateDisplay();
	},

	onFileQueueRemove: function(file){
		var row = this.container.getElementById('fileupload-' + file.id).dispose();
		this.updateDisplay();
		return this.fireEvent('fileDeleted', [{}, row]);
	},

	onFileUploadStart: function(file, pollAttempts){
		if (!file.ui) {
			if (pollAttempts > 10) return;
			return this.onFileUploadStart.delay(2, this, [file, (pollAttempts || 0) + 1]);
		}
		file.ui.progress = new Element('span', {'class': 'f-rgt', text: '0%'});
		var progressContainer = new Element('div', {'class': 'fmgr-upload-progress'})
			.grab(file.ui.progress)
			.grab(new Element('span', {text: this.options.uploadingText}));
		file.ui.type.empty().grab(progressContainer);
	},

	onFileUploadProgress: function(file){
		if (file.ui.progress) file.ui.progress.set('text', file.progress.percentLoaded + '%');
	},

	onFileUploadComplete: function(file){
		if (file.response.error) {
			var msg = MooTools.lang.get('FancyUpload', 'errors')[file.response.error] || '{error} #{code}';
			return this._injectError(file.ui.row, msg.substitute(file.response));
		}
		var replaces = this.container.getElementById('fileupload-' + file.id);
		var resp = JSON.decode(file.response.text);
		this.fileAdded(resp, replaces);
	},

	updateDisplay: function(){
		var hasFiles = !!this.tbody.getFirst();
		if (hasFiles == this.container.hasClass('no-files')) this.container.toggleClass('no-files');
	},

	_createQueueRow: function(file){
		/* XXX: The form DOM created below mimics that in .../mediadrop/templates/admin/media/file-edit-form.html */
		var cancelBtn = new Element('button', this.options.uploadCancelBtn);
		file.ui = new Hash({
			name: new Element('td', {headers: 'thf-name', text: file.name}),
			size: new Element('td', {headers: 'thf-size', text: (file.size == '-') ? '-' : Swiff.Uploader.formatUnit(file.size, 'b')}),
			duration: new Element('td', {headers: 'thf-duration', text: '-'}),
			bitrate: new Element('td', {headers: 'thf-max-bitrate', text: '-'}),
			'width-height': new Element('td', {headers: 'thf-width-height', text: '-'}),
			type: new Element('td', {headers: 'thf-type', text: file.typeText || this.options.queuedText}),
			del: new Element('td', {headers: 'thf-delete'}).grab(cancelBtn)
		});
		file.ui.row = new Element('tr', this.options.uploadQueueRow)
			.set('id', 'fileupload-' + file.id)
			.adopt(file.ui.getValues());
		cancelBtn.addEvent('click', file.id > 0
			? file.remove.bind(file)
			: file.ui.row.destroy.bind(file.ui.row));
		return file.ui.row;
	},

	_injectError: function(row, msg){
		var errorDiv = new Element('div', this.options.errorDiv);
		row.store('fileError', errorDiv).getElement('td[headers="thf-name"]').grab(errorDiv);
		var typeCol = row.getElement('td[headers="thf-type"]');
		if (typeCol && !typeCol.getElement('select, input')) typeCol.set('text', this.options.errorText);
		row.className = 'error';
		this.fireEvent('fileError', [row, msg]);
		return errorDiv.set('html', msg);
	},

	_getFileID: function(el){
		var type = $type(el);
		if (type == 'number' || type == 'string') return 'file-' + el; // add prefix
		else if (el) return el.get('id').replace('file-', ''); // strip prefix
		else return null;
	}

});

var FileList = new Class({

	Implements: Options,

	options: {
		statusContainer: '',
		progress: '.upload-progress',
		fxProgress: {}
	},

	list: null,
	mgr: null,
	ui: {},
	fxProgress: null,

	initialize: function(list, mgr, options){
		this.list = $(list);
		this.mgr = mgr.addEvents({
			onFileAdded: this.onFileAdded.bind(this),
			onFileEdited: this.onFileEdited.bind(this),
			onFileDeleted: this.onFileDeleted.bind(this),
			onFileQueued: this.onFileQueued.bind(this),
			onFileError: this.onFileError.bind(this)
		});
		this.mgr.uploader.addEvents({
			onStart: this.onUploadStart.bind(this),
			onFileProgress: this.onUploadProgress.bind(this),
			onComplete: this.onUploadComplete.bind(this)
		});
		this.setOptions(options);
		this.ui.container = $(this.options.statusContainer);
		this.ui.progress = this.ui.container.getElement(this.options.progress);
	},

	onUploadStart: function(){
		if (!this.fxProgress) {
			this.fxProgress = new Fx.ProgressBar(this.ui.progress.getElement('img'), this.options.fxProgressBar);
		}
		this.fxProgress.set(0);
		this.ui.progress.slide('hide').show().slide('in');
	},

	onUploadProgress: function(file){
		this.fxProgress.set(file.base.percentLoaded);
	},

	onUploadComplete: function(){
		if (this.fxProgress) this.fxProgress.set(100);
		this.ui.progress.slide.delay(500, this.ui.progress, ['out']);
	},

	onFileAdded: function(json, row, replaces){
		// a file has been added. it may have been a queued file (already in the list)
		// or its a URL being added and it's the first time we're seeing it
		if (replaces) replaces = this.list.getElementById('list-' + replaces.id);
		if (replaces) var li = replaces.set('id', 'list-' + row.id);
		else var li = this._createLi(row).inject(this.list);
		li.className = row.className;
		var namelink = row.getElement('td[headers="thf-name"]').getChildren();
		li.empty().adopt(namelink.clone());
	},

	onFileEdited: function(json, row, target){
		// a file has been changed, make sure its type stays up to date
		this.list.getElementById('list-' + row.id).className = row.className;
	},

	onFileDeleted: function(json, row){
		this.list.getElementById('list-' + row.id).destroy();
	},

	onFileQueued: function(row, file){
		// a file is queued and is about to start uploading
		var name = row.getElement('td[headers="thf-name"]').get('text');
		this.list.grab(this._createLi(row).set('text', name));
	},

	onFileError: function(row, msg){
		// a queued file fails to upload properly
		var li = this.list.getElementById('list-' + row.id);
		if (li) li.className = row.className;
	},

	_createLi: function(row){
		return new Element('li', {id: 'list-' + row.id, 'class': row.className});
	}

});

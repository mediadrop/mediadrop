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
var MediaManager = new Class({
	metaForm: null,
	metaFormPodcastID: null,
	statusForm: null,
	files: null,
	uploader: null,
	isNew: null,
	podcastWarning: null,
	type: '',

	initialize: function(opts){
		// metaForm, files, uploader, statusForm, thumbUploader, thumbImg, isNew, type
		this.metaForm = $(opts.metaForm);
		this.metaFormPodcastID = this.metaForm.podcast.value;
		this.statusForm = opts.statusForm;
		this.uploader = opts.uploader;
		this.thumbUploader = opts.thumbUploader.addEvent('fileComplete', this.onThumbUpload.bind(this));
		this.files = opts.files.addEvents({
			fileAdded: this.onFileAdded.bind(this),
			fileEdited: this.updateStatusForm.bind(this),
			fileDeleted: this.updateStatusForm.bind(this)
		});
		this.isNew = !!opts.isNew;
		this.type = opts.type;
		this.metaForm.podcast.addEvent('change', this.onPodcastChange.bind(this));
	},

	onFileAdded: function(json){
		this.updateFormActions(json.media_id);
		this.updateStatusForm(json.status_form);
	},

	onFileEdited: function(json){
		if (this.isNew) return; // dont let them click 'review complete' etc until saving!
		this.updateStatusForm(json.status_form);
	},

	updateFormActions: function(mediaID){
		var find = /\/new\//, repl = '/' + mediaID + '/';
		this.metaForm.action = this.metaForm.action.replace(find, repl);
		this.statusForm.form.action = this.statusForm.form.action.replace(find, repl);
		this.thumbUploader.setOptions({
			url: this.thumbUploader.options.url.replace(find, repl)
		});
		this.uploader.setOptions({
			url: this.uploader.options.url.replace(find, repl)
		});
		this.files.addForm.action = this.files.addForm.action.replace(find, repl);
	},

	updateStatusForm: function(resp){
		if (this.isNew) return; // dont let them click 'review complete' etc until saving!
		if (resp['status_form']) resp = resp['status_form'];
		this.statusForm.updateForm(Elements.from(resp)[0]);
	},

	onThumbUpload: function(file){
		var json = JSON.decode(file.response.text, true);
		this.updateFormActions(json.id);
	},

	onPodcastChange: function(e){
		return;
		var podcastID = this.metaForm.podcast.value, oldPodcastID = this.metaFormPodcastID;
		if (podcastID && !oldPodcastID && this._isPublished()) {
			var inputs = this.files.list.getElements("input[name='is_playable']");
			for (var warn = true, i = inputs.length; i--; i) {
				if (inputs[i].value == 'true') {
					warn = false;
					break;
				}
			}
			if (warn) this.displayPodcastWarning();
		} else if (this.podcastWarning && !podcastID && oldPodcastID) {
			this.podcastWarning.dispose();
		}
		this.metaFormPodcastID = podcastID;
	},

	displayPodcastWarning: function(){
		this.podcastWarning = this.podcastWarning || new Element('div', {
			id: 'podcast_warning',
			html: 'You need an encoded ' + this.type + ' before publishing in podcast.<br />'
			    + 'Choose to ignore this warning and this media will be unpublished.'
		});
		$('podcast_container').getElement('.form_field').grab(this.podcastWarning);
	},

	_isPublished: function(){
		return this.statusForm.form.get('html').match(/published/i);
	}

});

var StatusForm = new Class({
	Extends: Options,

	options: {
		form: '',
		error: '',
		submitReq: {noCache: true},
		pickerField: '#publish_on',
		pickerOptions: {
			toggleElements: '#status-publish',
			yearPicker: false,
			timePicker: true,
			allowEmpty: true,
			format: 'M d Y @ H:i',
			inputOutputFormat: 'M d Y @ H:i'
		}
	},

	form: null,
	submitReq: null,
	publishDatePicker: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.saveStatus.bind(this));
		this.attachDatePicker();
	},

	attachDatePicker: function(){
		try {
			if (!this.publishDatePicker) {
				this.publishDatePicker = new DatePicker(this.options.pickerField, $extend(this.options.pickerOptions, {
					onSelect: this.changePublishDate.bind(this),
					onShow: this.onShowDatePicker.bind(this)
				}));
			}
			return this.publishDatePicker.attach();
		} catch(e) {}
	},

	saveStatus: function(e){
		e = new Event(e).stop();
		if (!this.submitReq) {
			var submitOpts = $extend({url: this.form.action}, this.options.submitReq);
			this.submitReq = new Request.JSON(submitOpts).addEvents({
				success: this.statusSaved.bind(this),
				failure: this._displayError.bind(this, ['A connection problem occurred, try again.'])
			});
		}
		var data = this.form.toQueryString() + '&update_button=' + this.form.update_button.get('value');
		this.submitReq.send(data);
	},

	statusSaved: function(json){
		json = json || {};
		if (json.success) this.updateForm(json.status_form);
		else this._displayError(json.message);
	},

	updateForm: function(form){
		if ($type(form) == 'string') {
			form = new Element('div', {html: form}).getFirst();
		}
		var formContents = $(form).getChildren();
		this.form.empty().adopt(formContents);
		this.attachDatePicker();
	},

	_displayError: function(msg){
		var errorBox = $(this.options.error);
		errorBox.set('html', msg || 'An error has occurred, try again.');
		if (!errorBox.isDisplayed()) errorBox.slide('hide').show().slide('in');
		errorBox.highlight();
	},

	onShowDatePicker: function(){
		var coords = $$(this.publishDatePicker.options.toggleElements)[0].getCoordinates();
		var ml = coords.left - Math.floor($(document).getSize().x / 2);
		$$('.datepicker')[0].setStyles({left: '50%', top: coords.bottom + 'px', marginLeft: ml + 'px'});
	},

	changePublishDate: function(d){
		var publishDate = d.format('%b %d %Y @ %H:%M');
		$$(this.publishDatePicker.options.toggleElements)[0].getFirst().set('text', publishDate);

		var r = new Request.JSON({
			url: this.form.get('action'),
			onComplete: this.statusSaved.bind(this)
		}).send(new Hash({
			publish_on: publishDate,
			update_button: 'Change publish date'
		}).toQueryString());
	}
});

/**
 * Agh! This class got big quickly, and I don't have time to refactor it
 * into smaller, more managable chunks.
 */
var FileManager = new Class({

	Implements: [Events, Options],

	options: {
	/*	onFileAdded: function(json, row)
		onFileEdited: function(json, row, target),
		onFileDeleted: function(json), */
		editURL: '',
		modal: {squeezeBox: {zIndex: 10000}},
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
			multiple: true,
			queued: 1,
			zIndex: 65555
		}
	},

	container: null,
	files: [],
	uploader: null,
	modal: null,

	initialize: function(container, opts){
		this.setOptions(opts);
		this.container = $(container);
		this.addForm = $(this.options.addForm);
		this.uploader = new UploaderBase(this.options.uploader);
		this.modal = new Modal(this.container, this.options.modal);
		this.files = this.container.getElements('table tbody tr');
		this.urlOverText = new OverText('url', {wrap: true});
		this.attach();
	},

	attach: function(){
		this.addForm.addEvent('submit', this.addFile.bind(this));
		this.addForm.url.addEvent('focus', this.addForm.url.select);
		this.files.each(this._attachFile.bind(this));
		this._attachUploader(this.uploader);
		this._attachModal(this.modal);
		return this;
	},

	_attachFile: function(row){
		row.getElement('input.file-delete').addEvent('click', this.editFile.bind(this));
		row.getElement('select[name=file_type]').addEvent('change', this.editFile.bind(this));
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
		this.urlOverText.reposition.delay(300);
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
		var row = this._createQueueRow(fileSpoof)
			.inject(this.container.getElement('table tbody'))
			.highlight();
		var req = new Request.JSON({
			url: form.get('action'),
			onSuccess: this.fileAdded.bindWithEvent(this, [row]),
			onFailure: this._injectError.bind(this, [row, 'Failed to add this file. Please try again.'])
		});
		req.addEvent('success', function(){
			form.url.set('value', '').blur();
			this.urlOverText.reposition();
		}.bind(this));
		req.send(form.toQueryString());
	},

	fileAdded: function(resp, replaces){
		if (!resp.success) this._injectError(replaces, resp.message);
		var row = this._attachFile(Elements.from(resp.edit_form)[0]);
		this.files.push(row);
		if (replaces) row.replaces(replaces);
		else row.inject(this.container.getElement('table tbody'));
		row.highlight();
		return this.fireEvent('fileAdded', [resp, row, replaces]);
	},

	editFile: function(e){
		var e = new Event(e), target = $(e.target), row = target.getParent('tr');
		var oldError = row.retrieve('fileError');
		if (oldError) oldError.destroy();
		if (target.get('name') == 'delete') {
			e.stop();
			var name = row.getElement('td[headers="thf-name"]').get('text').trim();
			var msg = $lambda(this.options.deleteConfirmMsg)(name);
			if (!confirm(msg)) return false;
		}
		row.className = 'saving';
		var data = new Hash({file_id: this._getFileID(row)})
			.set(target.get('name'), target.get('value'));
		var r = new Request.JSON({
			url: this.options.editURL,
			data: data,
			onSuccess: this.fileEdited.bindWithEvent(this, [target]),
			onFailure: this._injectError.bind(this, [row, 'Failed to save your change. Please try again.'])
		}).send();
	},

	fileEdited: function(json, target){
		json = json || {};
		var row = target.getParent('tr');
		if (!json.success) return this._injectError(row, json.message);
		if (target.get('name') == 'delete') {
			this.files.erase(row);
			row.dispose();
			return this.fireEvent('fileDeleted', [json, row]);
		} else {
			row.className = json.file_type;
			return this.fireEvent('fileEdited', [json, row, target]);
		}
	},

	onUploadSelectSuccess: function(files){
		for (var i = 0; i < files.length; i++) this.onFileQueue(files[i]);
	},

	onUploadSelectFail: function(files){
		for (var i = 0; i < files.length; i++) this.onFileQueueError(files[i]);
	},

	onFileQueue: function(file){
		var row = this._createQueueRow(file)
			.inject(this.container.getElement('table tbody'))
			.highlight();
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
		row.inject(this.container.getElement('table tbody')).highlight();
	},

	onFileQueueRemove: function(file){
		this.container.getElementById('fileupload-' + file.id).destroy();
	},

	onFileUploadStart: function(file){
		file.ui.progress = new Element('span', {'class': 'f-rgt', text: '0%'});
		file.ui.type.empty()
			.grab(file.ui.progress)
			.grab(new Element('span', {text: 'Uploading'}));
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

	_createQueueRow: function(file){
		var cancelBtn = new Element('input', this.options.uploadCancelBtn);
		file.ui = new Hash({
			name: new Element('td', {headers: 'thf-name', text: file.name}),
			size: new Element('td', {headers: 'thf-size', text: (file.size == '-') ? '-' : Swiff.Uploader.formatUnit(file.size, 'b')}),
			type: new Element('td', {headers: 'thf-type', text: file.typeText || 'Queued'}),
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
		if (typeCol && !typeCol.getElement('select')) typeCol.set('text', 'Error');
		row.className = 'error';
		this.fireEvent('fileError', [row, msg]);
		return errorDiv.set('text', msg);
	},

	_getFileID: function(el){
		var type = $type(el);
		if (type == 'number' || type == 'string') return 'file-' + el; // add prefix
		else if (el) return el.get('id').replace('file-', ''); // strip prefix
		else return null;
	}

});

var FileList = new Class({

	initialize: function(list, mgr){
		this.list = $(list);
		this.mgr = mgr.addEvents({
			onFileAdded: this.onFileAdded.bind(this),
			onFileEdited: this.onFileEdited.bind(this),
			onFileDeleted: this.onFileDeleted.bind(this),
			onFileQueued: this.onFileQueued.bind(this),
			onFileError: this.onFileError.bind(this)
		});
	},

	onFileAdded: function(json, row, replaces){
		// a file has been added. it may have been a queued file (already in the list)
		// or its a URL being added and it's the first time we're seeing it
		var li = this.list.getElementById('list-' + replaces.id);
		if (li) li.set('id', 'list-' + row.id);
		else li = this._createLi(row).inject(this.list);
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

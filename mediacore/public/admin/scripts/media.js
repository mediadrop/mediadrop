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
		this.files = opts.files;
		this.uploader = opts.uploader;
		this.thumbUploader = opts.thumbUploader;
		this.thumbUploader.uploader.addEvent('fileComplete', this.onThumbUpload.bind(this));
		this.files.addEvents({
			fileAdded: this.onFileAdded.bind(this),
			fileEdited: this.onFileEdited.bind(this)
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
		this.thumbUploader.uploader.setOptions({
			url: this.thumbUploader.uploader.options.url.replace(find, repl)
		});
		this.uploader.uploader.setOptions({
			url: this.uploader.uploader.options.url.replace(find, repl)
		});
		this.files.addForm.action = this.files.addForm.action.replace(find, repl);
	},

	updateStatusForm: function(html){
		if (this.isNew) return; // dont let them click 'review complete' etc until saving!
		var statusFormEl = new Element('div', {html: html}).getFirst();
		this.statusForm.updateForm(statusFormEl);
	},

	onThumbUpload: function(file){
		var json = JSON.decode(file.response.text, true);
		this.updateFormActions(json.id);
	},

	onPodcastChange: function(e){
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
 * Handles dynamic adding/editing of files to the media files box.
 *
 * Uploading itself is left to the Uploader and is expected to
 * be tied in from that end.
 */
var FileManager = new Class({

	Implements: [Events, Options],

	options: {
	/*	onFileAdded: function(json)
	 *	onFileEdited: function(json, buttonClicked), */
		saveOrderUrl: ''
	},

	container: null,
	list: null,
	addForm: null,
	uploader: null,
	errorDiv: null,

	initialize: function(container, addForm, uploader, errorDiv, opts){
		this.setOptions(opts);
		this.container = $(container);
		this.uploader = this._setupUploader(uploader);
		this.errorDiv = $(errorDiv);

		this.list = $(this.container.getElement('ol'));
		this.list.getChildren().each(this._setupLi.bind(this));

		this.addForm = $(addForm).addEvent('submit', this.addFile.bind(this));
		this.addForm.url.addEvent('focus', this.addForm.url.select);
		var addFileBtn = this._setupAddFileBtn();
		addFileBtn.addEvent('click', function(){
			var open = !this.addForm.slide.run(['toggle'], this.addForm).get('slide').open;
			this.uploader.uploader.setEnabled(open);
		}.bind(this));
	},

	addFile: function(e){
		e = new Event(e).preventDefault();
		var form = $(e.target), r = new Request({
			url: form.get('action'),
			onComplete: this.fileAdded.bind(this),
			onFailure: this._displayError.bind(this, ['Could not add the file, please try again.'])
		}).send(form.toQueryString());
	},

	fileAdded: function(resp){
		json = JSON.decode(resp, true) || {};
		if (!json.success) return this._displayError(json.message);
		var li = new Element('li', {
			id: this._getFileID(json.file_id),
			html: json.edit_form
		}).inject(this.list, 'bottom');
		li.slide('hide').set('slide', {onComplete: function(){
			// slide creates an extra wrapping div that interferes with sorting
			var div = li.getParent();
			li.dispose().inject(this.list, 'bottom');
			div.destroy();
		}.bind(this)}).slide('in').highlight();
		this._setupLi(li);
		return this.fireEvent('fileAdded', [json]);
	},

	editFile: function(e){
		e = new Event(e).stop();
		var button = $(e.target), form = button.form, data = new Hash();

		// create a dict of all hidden values + the clicked submit button
		// cuz form.send() sends the values of ALL buttons, not just the clicked 1
		for (var field, i = form.length; i--; i) {
			field = $(form[i]);
			if (field.get('type') == 'hidden' || field == button) {
				data.set(field.name, field.value);
			}
		}

		var r = new Request.JSON({
			url: form.get('action'),
			onComplete: this.fileEdited.bindWithEvent(this, button),
			onFailure: this._displayError.bind(this, ['A connection problem occurred.'])
		}), sendRequest = function(){
			button.parentNode.addClass('spinner');
			button.blur();
			r.send(data.toQueryString());
		};

		if (button.get('name') == 'delete') {
			var c = new ConfirmMgr({
				header: 'Delete Confirmation',
				msg: 'Are you sure you want to delete this file?',
				onConfirm: sendRequest
			}).openConfirmDialog(e);
		} else {
			sendRequest();
		}
	},

	fileEdited: function(json, button){
		json = json || {};
		if (!json.success) {
			button.getParent().removeClass('spinner');
			return this._displayError(json.message);
		}
		if (json.field == 'delete') {
			var li = button.getParent('li');
			li.set('slide', {onComplete: li.destroy.bind(li)}).slide('out');
		} else if (json.field) {
			var field = button.form.getElement('input[name=' + json.field + ']').set('value', json.value);
			var span = button.parentNode;
			if (json.value != undefined) {
				if (json.value) span.addClass('file-toggle-on');
				else span.removeClass('file-toggle-on');
			}
			span.removeClass('spinner');
		}
		return this.fireEvent('fileEdited', [json, button]);
	},

	_setupUploader: function(uploader){
		var self = this;
		uploader.uploader.addEvents({
			fileComplete: function(file){
				self.fileAdded(file.response.text);
			},
			fileError: self._hideError.bind(self)
		});
		return uploader;
	},

	_displayError: function(msg){
		this.uploader.clearStatus();
		this.errorDiv.set('html', msg || 'An error has occurred, try again.');
		if (!this.errorDiv.isDisplayed()) this.errorDiv.slide('hide').show().slide('in');
		this.errorDiv.highlight();
		return this;
	},

	_hideError: function(){
		if (this.errorDiv.isDisplayed()) this.errorDiv.slide('out');
		else this.errorDiv.slide('hide').show();
		return this;
	},

	_getFileID: function(el){
		var type = $type(el);
		if (type == 'number' || type == 'string') return 'file-' + el; // add prefix
		else if (el) return el.get('id').replace('file-', ''); // strip prefix
		else return null;
	},

	_setupAddFileBtn: function(){
		return new Element('span', {
			id: 'add-media-file',
			'class': 'box-head-sec clickable',
			title: 'Add another file to this media',
			text: 'Add File'
		}).inject(this.container.getElement('.box-head'), 'top')
	},

	_setupLi: function(li){
		li.getElements('input[type=submit]').each(function(el){
			el.addEvent('click', this.editFile.bind(this));
		}.bind(this));
	}

});

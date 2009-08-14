var ManevolentMediaOverlord = new Class({
	metaForm: null,
	metaFormPodcastID: null,
	statusForm: null,
	files: null,
	uploader: null,
	isNew: null,

	initialize: function(metaForm, files, uploader, statusForm, albumArtUploader, albumArtImg, isNew){
		this.metaForm = $(metaForm);
		this.metaFormPodcastID = this.metaForm.podcast.value;
		this.statusForm = statusForm;
		this.files = files;
		this.uploader = uploader;
		this.albumArtUploader = albumArtUploader;
		this.albumArtUploader.uploader.addEvent('fileComplete', this.onAlbumArtUpload.bind(this));
		this.isNew = !!isNew;
		this.reinFire();
	},

	reinFire: function(){
		this.files.addEvents({
			fileAdded: this.onFileAdded.bind(this),
			fileEdited: this.onFileEdited.bind(this)
		});
		this.metaForm.podcast.addEvent('change', this.onPodcastChange.bind(this));
	},

	onFileAdded: function(json){
		this.updateFormActions(json.media_id);
		this.updateStatusForm(json.status_form);
		this.isNew = false;
	},
	
	onFileEdited: function(json){
		this.updateStatusForm(json.status_form);
	},

	updateFormActions: function(mediaID){
		var find = /\/new\//, repl = '/' + mediaID + '/';
		this.metaForm.action = this.metaForm.action.replace(find, repl);
		this.statusForm.form.action = this.statusForm.form.action.replace(find, repl);
		this.albumArtUploader.uploader.setOptions({
			url: this.albumArtUploader.uploader.options.url.replace(find, repl)
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

	onAlbumArtUpload: function(file){
		var json = JSON.decode(file.response.text, true);
		this.updateFormActions(json.id);
		this.isNew = false;
	},

	onPodcastChange: function(e){
		var podcastID = this.metaForm.podcast.value, oldPodcastID = this.metaFormPodcastID;
		if (podcastID && !oldPodcastID) {
			// enable toggle_feed
			console.log('enable');
		} else if (!podcastID && oldPodcastID) {
			// disable toggle_feed
			console.log('disable');
		} else {
			console.log('nuttin yo');
		}
		this.metaFormPodcastID = podcastID;
	},

});

var StatusForm = new Class({
	Extends: Options,

	options: {
		form: '',
		error: '',
		submitReq: {noCache: true}
	},

	form: null,
	submitReq: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.saveStatus.bind(this));
	},

	saveStatus: function(e){
		e = new Event(e).stop();
		if (!this.submitReq) {
			var submitOpts = $extend({url: this.form.action}, this.options.submitReq);
			this.submitReq = new Request.JSON(submitOpts).addEvents({
				success: this.updateForm.bind(this),
				failure: this._displayError.bind(this, ['A connection problem occurred, try again.'])
			});
		}
		this.submitReq.send(this.form);
	},

	updateForm: function(json){
		json = json || {};
		if (!json.success) return this._displayError(json.message);
		this.form.set('html', json.status_form);
	},

	_displayError: function(msg){
		var errorBox = $(this.options.error);
		errorBox.set('html', msg || 'An error has occurred, try again.');
		if (!errorBox.isDisplayed()) errorBox.slide('hide').show().slide('in');
		errorBox.highlight();
	}
});


/**
 * A picky sorter -- only starts the drag if left clicking on the base element
 * which happens to be the li in this case, not the any of the buttons/links.
 */
var FickleSortables = new Class({

	Extends: Sortables,

	addItems: function(){
		Array.flatten(arguments).each(function(element){
			this.elements.push(element);
			var start = element.retrieve('sortables:start', this.fireStart.bindWithEvent(this, element));
			(this.options.handle ? element.getElement(this.options.handle) || element : element).addEvent('mousedown', start);
		}, this);
		return this;
	},

	fireStart: function(e, el){
		e = new Event(e);
		if (!e.rightClick && $(e.target) == $(el)) this.start(e, el);
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
		saveOrderUrl: '',
		errorPlaceholder: '.box-error',
		sortable: {
			constrain: true,
			clone: true,
			opacity: .6,
			revert: true
		}
	/*	onFileAdded: function(json)
	 *	onFileEdited: function(json, buttonClicked), */
	},

	container: null,
	list: null,
	sortable: null,
	addForm: null,
	uploader: null,

	initialize: function(container, addForm, uploader, opts){
		this.setOptions(opts);
		this.container = $(container);
		this.uploader = this._setupUploader(uploader);

		this.list = $(this.container.getElement('ol'));
		this.list.getChildren().each(this._setupLi.bind(this));
		this.sortable = new FickleSortables(this.list, this.options.sortable).addEvents({
			start: this.dragStart.bind(this),
			complete: this.dragComplete.bind(this)
		});

		this.addForm = $(addForm).addEvent('submit', this.addFile.bind(this));
		this.addForm.url.addEvent('focus', this.addForm.url.select);
		var addFileBtn = this._setupAddFileBtn();
		addFileBtn.addEvent('click', this.addForm.slide.bind(this.addForm, ['toggle']));
	},

	dragStart: function(el, clone){
		el.addClass('file-drag');
		if (clone) {
			var firstEl = clone.addClass('file-drag-clone');
		} else {
			var firstEl = el;
		}
		el.store('prevFileID', this._getFileID(firstEl.getPrevious()));
	},

	dragComplete: function(el){
		el.removeClass('file-drag');
		var prevID = this._getFileID(el.getPrevious());
		var prevIDatStart = el.retrieve('prevFileID');
		if (prevIDatStart && prevID != prevIDatStart) {
			this.saveOrder(this._getFileID(el), prevID);
		}
	},

	saveOrder: function(fileID, prevID){
		var error = this._displayError.bind(this, ['Transport error occurred']);
		var r = new Request.JSON({
			url: this.options.saveOrderUrl,
			onComplete: this.orderSaved.bind(this),
			onFailure: this._displayError.bind(this, ['A connection problem occurred.'])
		}).send(new Hash({file_id: fileID, prev_id: prevID}).toQueryString());
	},

	orderSaved: function(json){
		json = json || {};
		if (!json.success) return this._displayError(json.message);
	},

	addFile: function(e){
		e = new Event(e).preventDefault();
		var form = $(e.target), r = new Request.JSON({
			url: form.get('action'),
			onComplete: this.fileAdded.bind(this),
			onFailure: this._displayError.bind(this, ['A connection problem occurred.'])
		}).send(form.toQueryString());
	},

	fileAdded: function(json){
		json = json || {};
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
			this.sortable.addItems(li);
		}.bind(this)}).slide('in').highlight();
		this._setupLi(li);
		return this.fireEvent('fileAdded', [json]);
	},

	editFile: function(e){
		e = new Event(e).stop();
		var button = $(e.target), form = button.form, data = new Hash();
		button.parentNode.addClass('spinner');
		button.blur();
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
		}).send(data.toQueryString());
	},

	fileEdited: function(json, button){
		json = json || {};
		if (!json.success) return this._displayError(json.message);
		if (json.success && json.field == 'delete') {
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
		return uploader.uploader.addEvent('fileComplete', function(file){
			var response = JSON.decode(file.response.text, true);
			self.fileAdded(response);
		}.bind(this));
	},

	_displayError: function(msg){
		var errorBox = $(this.container).getElement(this.options.errorPlaceholder);
		errorBox.set('html', msg || 'An error has occurred, try again.');
		if (!errorBox.isDisplayed()) errorBox.slide('hide').show().slide('in');
		errorBox.highlight();
		return this;
	},

	_getFileID: function(el){
		var type = $type(el);
		if (type == 'number' || type == 'string') return 'file-' + el; // add prefix
		else return el ? el.get('id').replace('file-', '') : null; // strip prefix
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

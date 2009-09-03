/**
 * A picky sorter -- only starts the drag if left clicking on the base element
 * which happens to be the li in this case, not the any of the buttons/links.
 */
var SortableFiles = new Class({

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


var FileManager = new Class({

	Extends: Options,

	options: {
		saveOrderUrl: '',
		sortable: {
			constrain: true,
			clone: true,
			opacity: .6,
			revert: true
		}
	},

	container: null,
	list: null,
	sortable: null,
	addForm: null,

	initialize: function(container, addForm, opts){
		this.setOptions(opts);
		this.container = $(container);

		this.list = $(this.container.getElement('ol'));
		this.list.getChildren().each(this._setupLi.bind(this));
		this.sortable = new SortableFiles(this.list, this.options.sortable).addEvents({
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
		var r = new Request.JSON({
			url: this.options.saveOrderUrl,
			onComplete: this.orderSaved.bind(this)
		}).send(new Hash({file_id: fileID, prev_id: prevID}).toQueryString());
	},

	orderSaved: function(resp){
		console.log('Order saved!');
		console.log(resp);
	},

	addFile: function(e){
		e = new Event(e).preventDefault();
		var form = $(e.target), r = new Request.JSON({
			url: form.get('action'),
			onComplete: this.fileAdded.bind(this)
		}).send(form.toQueryString());
	},

	fileAdded: function(json){
		// for some reason request.html returns an array with textnodes at the start/end
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
			onComplete: this.fileEdited.bindWithEvent(this, [button])
		}).send(data.toQueryString());
	},

	fileEdited: function(json, button){
		if (json.field == 'delete') {
			var li = button.getParent('li');
			li.set('slide', {onComplete: li.destroy.bind(li)}).slide('out');
			return;
		}
		var field = button.form.getElement('input[name=' + json.field + ']');
		var span = button.parentNode;
		field.set('value', json.value);
		if (json.value) {
			span.addClass('file-toggle-on');
		} else {
			span.removeClass('file-toggle-on');
		}
		span.removeClass('spinner');
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
	},

});

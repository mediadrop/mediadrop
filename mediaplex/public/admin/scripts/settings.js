/**
 * @requires confirm.js
 */
var CategoryMgr = new Class({
	Implements: Options,

	options:{
		categoryName: 'Topic',
		table: 'category-table',
		formSelector: 'form.edit-category-form',
		emptyRow: 'empty-category',
		nameField: 'input.category-name',
		slugField: 'input.category-slug',
		deleteButton: 'input.delete-category',
		cancelButton: 'input.cancel-category',
		saveButton: 'input.save-category',
	},

	categories: [],

	initialize: function(opts) {
		this.setOptions(opts);
		var emptyRow = $(this.options.emptyRow);

		var tbody = $(this.options.table).getChildren('tbody')[0];
		tbody.getChildren('tr').each(function(row){
			if(row.get('id') == this.options.emptyRow){
				category = new NewCategory(row, this.options);
			} else {
				category = new Category(row, this.options);
			}
			this.categories.extend(category);
		}.bind(this));
	},
});

var Category = new Class({
	Implements: Options,

	options: null,

	row: null,
	form: null,
	formCell: null,
	countCell: null,

	dummyRow: null,
	nameCell: null,
	slugCell: null,
	editLink: null,
	deleteButton: null,
	cancelButton: null,
	formVisible: true,

	initialize: function(row, options){
		this.setOptions(options);
		this.row = row;
		this.form = this.row.getElement(this.options.formSelector);
		if(this.form == null){
			alert('form is null! ' + this.row.getChildren());
			return;
		}
		this.formCell = this.form.getParent();
		this.countCell = this.formCell.getNext();

		this.dummyRow = new Element('tr').setStyle('display', 'none');
		this.dummyRow.inject(this.row, 'after');

		// Set up the Save button
		var saveButton = this.form.getElement(this.options.saveButton);
		saveButton.addEvent('click', this.handleSave.bind(this));

		// Create a cancel button and insert it into the beginning of the row.
		this.cancelButton = new Element('button', {'class': 'mo cancel-category'});
		this.cancelButton.addEvent('click', this.toggleForm.bind(this));
		var cancelParent = new Element('td', {'class': 'form-field form-field-resetbutton'});
		cancelParent.grab(this.cancelButton);
		saveButton.parentNode.parentNode.grabTop(cancelParent);


		// Set up the edit and delete buttons
		this.deleteButton = this.form.getElement(this.options.deleteButton);
		if (this.deleteButton != null) {
			this.editLink = new Element('a', {'class': 'mo edit-category', href: '#', title: 'Edit this ' + this.options.categoryName})
				.addEvent('click', this.toggleForm.bind(this));
			this.editLink.grab(new Element('span', {html: 'edit'}));
			this.deleteButton.parentNode.grab(this.editLink, 'top');
		}


		// create two cells to replace the form cell
		nameField = this.form.getElement(this.options.nameField)
		slugField = this.form.getElement(this.options.slugField);
		nameSpan = new Element('span', {html: nameField.get('value')});
		slugSpan = new Element('span', {html: slugField.get('value')});
		this.nameCell = new Element('td').grab(nameSpan);
		this.slugCell = new Element('td').grab(slugSpan);
		nameSpan.setStyles({overflow: 'hidden', width: '193px'});
		slugSpan.setStyle('overflow', 'hidden');

		nameField.addEvent('change', this.updateSlug.bind(this));

		this.toggleForm()

		if (this.deleteButton != null) {
			this.requestConfirmDelete();
		}
	},

	toggleForm: function(){
		var displayEditAndDelete;
		var displayInputs;
		var colspan;
		var show;
		var hide;
		if (Browser.Engine.gecko) {
			show = 'table-cell';
		} else {
			show = 'inline-block';
		}
		hide = 'none';

		if(this.formVisible){
			colspan = '1';
			displayEditAndDelete = show;
			displayInputs = hide;

			this.row.adopt(this.formCell, this.nameCell, this.slugCell, this.countCell);
		} else {
			// show the form
			colspan = '3';
			displayEditAndDelete = hide;
			displayInputs = show;

			this.dummyRow.adopt(this.nameCell, this.slugCell);
			this.row.adopt(this.formCell, this.countCell);
		}

		this.formCell.set('colspan', colspan);

		this.form.getElements('input').each(function(elem){
			elem.parentNode.setStyle('display', displayInputs);
		});

		this.cancelButton.parentNode.setStyle('display', displayInputs);
		if (this.deleteButton != null) {
			this.deleteButton.parentNode.setStyle('display', displayEditAndDelete);
		}

		this.formVisible = !this.formVisible;
		return false;
	},

	updateSlug: function(){
		var name = this.form.getElement(this.options.nameField).get('value');
		var slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
		this.form.getElement(this.options.slugField).set('value', slug);
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr({
			onConfirm: this.handleDelete.bind(this),
			header: 'Confirm Delete',
			msg: this.getDeleteMsg.bind(this)
		});
		if (this.deleteButton != null) {
			// really, it should never be null, if this method is called.
			this.deleteButton.addEvent('click',
				confirmMgr.openConfirmDialog.bind(confirmMgr));
		}
		return this;
	},

	getDeleteMsg: function(){
		name = new String(this.form.getElement(this.options.nameField).get('value')).trim();
		return 'Are you sure you want to delete the ' + this.options.categoryName + ' <strong>' + name + '</strong>?'
	},

	handleDelete: function(){
		// manually constructing the Request rather than form.send()
		// to avoid issues with the two Submit buttons
		request = new Request({
			url: this.form.get('action'),
			onSuccess: this.deleteSuccess.bind(this),
			onFailure: this.deleteFailure.bind(this)
		}).send(new Hash({'delete': true}).toQueryString());
		return false;
	},

	deleteSuccess: function(responseText, responseXML){
		this.row.destroy();
	},

	deleteFailure: function(xhr){
		alert('Error deleting '+this.options.categoryName);
	},

	handleSave: function(){
		this.toggleForm();
		// manually constructing the Request rather than form.send()
		// to avoid issues with the two Submit buttons
		request = new Request({
			url: this.form.get('action'),
			onSuccess: this.saveSuccess.bind(this),
			onFailure: this.saveFailure.bind(this)
		}).send(
			new Hash({
				name: this.form.getElement(this.options.nameField).get('value'),
				slug: this.form.getElement(this.options.slugField).get('value')
			}).toQueryString());
		return false;
	},

	saveSuccess: function(responseText, responseXML){
		response = JSON.decode(responseText);
		var category = response.category;
		this.nameCell.set('html', category.name);
		this.slugCell.set('html', category.slug);
	},

	saveFailure: function(xhr){
		alert('Error saving changes to '+this.options.categoryName);
	},
});

var NewCategory = new Class({
	Extends: Category,

	dummyTable: null,

	initialize: function(row, opts) {
		this.parent(row, opts);

		$(this.options.table).getPrevious().getElement('a').addEvent('click', this.toggleForm.bind(this));
	},

	toggleForm: function(){
		if(this.dummyTable == null){
			this.dummyTable = new Element('table');
		}
		if(this.formVisible){
			this.dummyTable.grab(this.row);
		} else {
			var tbody = $(this.options.table).getElement('tbody');
			this.row.inject(tbody, 'top');
		}
		this.formVisible = !this.formVisible;
		return false;
	},

	saveSuccess: function(responseText, responseXML){
		window.location.reload(true);
	},

	saveFailure: function(xhr){
		alert('Error saving new '+this.options.categoryName);
	},
});

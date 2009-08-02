/**
 * @requires confirm.js
 */
var CategoryMgr = new Class({
	Implements: Options,

	options:{
		categoryName: 'Topic',
		table: 'category-table',
		formSelector: 'form.edit-category-form',
		cancelLink: 'a.cancel-category',
		deleteLink: 'a.delete-category',
		emptyRow: 'empty-category',
		nameField: 'input.category-name',
		slugField: 'input.category-slug'
	},

	dummyTable: null,
	emptyRow: null,

	initialize: function(opts) {
		this.setOptions(opts);
		var table = $(this.options.table);
		this.emptyRow = $(this.options.emptyRow);
		this.dummyTable = new Element('table');

		var cancelButton = this.emptyRow.getElement('input.cancel-category');
		cancelButton.addEvent('click', this.stashEmptyRow.bind(this));
		this.emptyRow.getElement('input.save-category').addEvent('click', this.handleNewSave.bind(this));
		var formCell = this.emptyRow.getElement('form').getParent();
		formCell.getPrevious().dispose();
		formCell.set('colspan', '3');

		formCell.getElement(this.options.nameField)
			.addEvent('change', this.updateSlug.bind(this));

		table.getPrevious().getElement('a').addEvent('click', this.addCategory.bind(this));
		this.stashEmptyRow();

		this.processRows(table.getElements('tbody > tr'));
	},

	processRows: function(rows) {
		$$(rows).each(function(row){
			var category = new Category(row, this.options);
		}.bind(this));
	},

	stashEmptyRow: function() {
		this.dummyTable.grab(this.emptyRow);
	},

	addCategory: function() {

		var tbody = $(this.options.table).getElement('tbody');
		this.emptyRow.inject(tbody, 'top');
		return false;
	},

	handleNewSave: function(){
		this.emptyRow.getElement('form').set('send', {onComplete: function(response) {
			if(JSON.decode(response) != null) {
				window.location.reload(true);
			} else {
				alert('Error saving new '+this.options.categoryName);
			}
		}.bind(this)});
		this.emptyRow.getElement('form').send();
		return false;
	},

	updateSlug: function(){
		var name = this.emptyRow.getElement(this.options.nameField).get('value');
		var slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
		this.emptyRow.getElement(this.options.slugField).set('value', slug);
	},

});

var Category = new Class({
	Implements: Options,

	options: null,

	row: null,
	dummyRow: null,
	deleteLink: null,

	buttonCell: null,
	formCell: null,
	nameCell: null,
	slugCell: null,
	countCell: null,
	form: null,
	editLink: null,
	formVisible: true,

	initialize: function(row, options){
		this.setOptions(options);
		this.row = row;
		this.dummyRow = new Element('tr').setStyle('display', 'none');
		this.dummyRow.inject(this.row, 'after');
		this.deleteLink = row.getElement(this.options.deleteLink);
		this.form = row.getElement(this.options.formSelector);
		this.formCell = this.form.getParent();
		this.formCell.set('colspan', '3');
		this.buttonCell = this.formCell.getPrevious();
		this.countCell = this.formCell.getNext();

		// add Edit button before Delete button in buttonCell
		this.editLink = new Element('a', {'class': 'mo edit-category', href: '#', title: 'Edit this ' + this.options.categoryName})
			.addEvent('click', this.toggleForm.bind(this));
		this.editLink.grab(new Element('span', {html: 'edit'}));
		this.buttonCell.grab(this.editLink, 'top');

		// add events to Save and Cancel buttons
		var saveButton = this.form.getElement('input.save-category');
		saveButton.addEvent('click', this.saveEditForm.bind(this));
		var cancelButton = this.form.getElement('input.cancel-category');
		cancelButton.addEvent('click', this.toggleForm.bind(this));

		// create two cells to replace the form cell
		nameField = this.form.getElement(this.options.nameField)
		slugField = this.form.getElement(this.options.slugField);
		this.nameCell = new Element('td', {html: nameField.get('value')});
		this.slugCell = new Element('td', {html: slugField.get('value')});

		nameField.addEvent('change', this.updateSlug.bind(this));

		this.toggleForm()

		if (this.deleteLink != null) this.requestConfirmDelete();
	},

	updateSlug: function(){
		var name = this.form.getElement(this.options.nameField).get('value');
		var slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
		this.form.getElement(this.options.slugField).set('value', slug);
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr({
			onConfirm: this.doConfirm.pass([this.deleteLink.href, this.updateDeleted.bind(this)], this),
			header: 'Confirm Delete',
			msg: 'Are you sure you want to delete the ' + this.options.categoryName + ' <strong>' + this.getName() + '</strong>?'
		});
		this.deleteLink.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	doConfirm: function(href, successAction){
		var r = new Request.HTML({url: href, onSuccess: successAction}).get();
		return this;
	},

	updateDeleted: function(){
		this.row.destroy();
		return this;
	},

	getName: function(){
		return new String(this.form.getElement(this.options.nameField).get('value')).trim();
	},

	toggleForm: function(){
		if(this.formVisible){
			// show the display view
			this.dummyRow.adopt(this.formCell);
			this.row.adopt(this.buttonCell, this.nameCell, this.slugCell, this.countCell);

		} else {
			// show the form
			this.dummyRow.adopt(this.buttonCell, this.nameCell, this.slugCell);
			this.row.adopt(this.formCell, this.countCell);
		}
		this.formVisible = !this.formVisible;
		return this;
	},

	saveEditForm: function(){
		this.toggleForm();
		this.form.set('send', {onComplete: function(response) {
			response = JSON.decode(response);
			if(response == null) {
				alert('Error saving changes to '+this.options.categoryName);
			} else {
				var category = response.category;
				this.nameCell.set('html', category.name);
				this.slugCell.set('html', category.slug);
			}
		}.bind(this)});
		this.form.send();
		return false;
	}
});


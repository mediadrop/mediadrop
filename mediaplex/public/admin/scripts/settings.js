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
		deleteLink: 'a.delete-category'
	},

	initialize: function(opts) {
		this.setOptions(opts);
		this.processRows($(this.options.table).getElements('tbody > tr'));
	},

	processRows: function(rows) {
		$$(rows).each(function(row){
			var category = new Category(row, this.options);
		}.bind(this));
	}
});

var Category = new Class({
	Implements: Options,

	options: null,

	row: null,
	dummyRow: null,
	name: null,
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
		this.name = this.form.getElement('input.category-name').get('value');
		var slug = this.form.getElement('input.category-slug').get('value');
		this.nameCell = new Element('td', {html: this.name});
		this.slugCell = new Element('td', {html: slug});
		this.cancelCell = new Element('td').grab(cancelButton);

		this.toggleForm()

		if (this.deleteLink != null) this.requestConfirmDelete();
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
		return new String(this.name).trim();
	},

	toggleForm: function(){
		if(this.formVisible){
			// show the display view
			this.dummyRow.adopt(this.cancelCell, this.formCell);
			this.row.adopt(this.buttonCell, this.nameCell, this.slugCell, this.countCell);

		} else {
			// show the form
			this.dummyRow.adopt(this.buttonCell, this.nameCell, this.slugCell);
			this.row.adopt(this.cancelCell, this.formCell, this.countCell);
		}
		this.formVisible = !this.formVisible;
		return this;
	},

	saveEditForm: function(){
		this.toggleForm();
		this.form.set('send', {onComplete: function(response) {
			this.nameCell.set('html', JSON.decode(response).category.name);
			this.slugCell.set('html', JSON.decode(response).category.slug);
		}.bind(this)});
		this.form.send();
		return false;
	}
});


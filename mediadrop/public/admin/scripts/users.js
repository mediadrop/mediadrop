/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * @requires confirm.js
 */
var UserMgr = new Class({
	Implements: Options,

	options:{
		table: 'user-table',
		deleteForm: 'form.delete-user-form',
		deleteConfirmMgr: {
			header: 'Confirm Delete',
			msg: 'Are you sure you want to delete this user?',
			confirmButtonText: 'Delete',
			confirmButtonClass: 'btn red f-rgt',
			cancelButtonText: 'Cancel',
			cancelButtonClass: 'btn f-lft',
			focus: 'cancel'
		}
	},

	initialize: function(opts){
		this.setOptions(opts);

		var rows = $(this.options.table).getElements('tbody > tr');
		$$(rows).each(function(row){
			if(row.getChildren().length != 1)
				var user = new User(row, this.options);
		}.bind(this));
	}
});

var User = new Class({
	Implements: Options,

	options: null,

	row: null,
	deleteForm: null,

	initialize: function(row, options){
		this.setOptions(options);
		this.row = row;
		this.deleteForm = row.getElement(this.options.deleteForm);

		if (this.deleteForm) this.requestConfirmDelete();
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr(this.options.deleteConfirmMgr)
			.addEvent('confirm', this.doConfirm.pass(this.deleteForm, this));
		$(this.deleteForm.elements['delete']).addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	doConfirm: function(form){
		// manually constructing the Request rather than form.send()
		var r = new Request({
			url: this.deleteForm.get('action'),
			onSuccess: this.updateDeleted.bind(this),
			onFailure: this.deleteFailure.bind(this)
		}).send();
		return false;
	},

	updateDeleted: function(){
		this.row.destroy();
		return this;
	},

	deleteFailure: function(xhr){
		alert('Error deleting User');
	}
});


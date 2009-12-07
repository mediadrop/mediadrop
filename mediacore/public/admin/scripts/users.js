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
/**
 * @requires confirm.js
 */
var UserMgr = new Class({
	Implements: Options,

	options:{
		table: 'user-table',
		deleteForm: 'form.delete-user-form'
	},

	initialize: function(opts){
		this.setOptions(opts);
		this.processRows($(this.options.table).getElements('tbody > tr'));
	},

	processRows: function(rows) {
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

		if (this.deleteForm != null) this.requestConfirmDelete();
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr({
			onConfirm: this.doConfirm.pass(this.deleteForm, this),
			header: 'Confirm Delete',
			msg: 'Are you sure you want to delete this user?'
		});
		this.deleteForm.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	doConfirm: function(form){
		// manually constructing the Request rather than form.send()
		request = new Request({
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


/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * Editable Tables
 *
 * Requires:
 *  - Element.Delegation
 *  - Element.Shortcuts
 *  - Selectors
 *
 * @author Nathan Wright <nathan@mediacore.com>
 */
var TableManager = new Class({

	Implements: [Options, Events],

	options: {
	/*	onInsertRow: $empty,
		onUpdateRow: $empty,
		onRemoveRow: $empty, */
		prefix: 'row-'
	},

	table: null,

	initialize: function(table, opts){
		this.table = $(table);
		this.setOptions(opts);
		this.init();
		this.attach();
	},

	init: $empty,
	attach: $empty,

	insertRow: function(resp){
		var row = Elements.from(resp.row).inject(this.table.getElement('tbody'), 'top');
		this.fireEvent('insertRow', [row, resp]);
		return row.highlight();
	},

	updateRow: function(resp){
		var row = Elements.from(resp.row).replaces(this.options.prefix + resp.id);
		this.fireEvent('updateRow', [row, resp]);
		return row.highlight();
	},

	removeRow: function(resp){
		var row = this.table.getElementById(this.options.prefix + resp.id);
		this.fireEvent('removeRow', [row, resp]);
		if (row) row.destroy();
	},

	toElement: function(){
		return this.table;
	},

	isPaginated: function(){
		return !!this.table.getElement('tfoot div.pager');
	},

	_getId: function(rowId){
		return rowId.substr(this.options.prefix.length).toInt();
	}

});

var BulkTableManager = new Class({

	Extends: TableManager,

	attach: function(){
		this.toggler = this.table.getElement('input.bulk-toggle');
		if (!this.toggler) return;
		this.toggler.getParent('th').addEvent('click', this.onToggleCheckboxes.bind(this));
		this.table.addEvent('click:relay(td[headers=h-bulk])', this.onToggleCheckbox.bind(this));
		var toggleOff = this.toggler.set.bind(this.toggler, ['checked', false]);
		this.addEvents({
			insertRow: toggleOff,
			updateRow: toggleOff,
			removeRow: toggleOff
		});
	},

	getCheckedRows: function(){
		return this.table.getElements('input.bulk-checkbox:checked').getParent('tr');
	},

	getCheckedIds: function(){
		return this.getCheckedRows().get('id').map(this._getId, this);
	},

	onToggleCheckbox: function(e){
		var target = this._toggleTarget(e);
		if (!target.checked && this.toggler.checked) this.toggler.checked = false;
	},

	onToggleCheckboxes: function(e){
		var target = this._toggleTarget(e);
		this.table.getElements('input.bulk-checkbox').set('checked', this.toggler.checked);
	},

	_toggleTarget: function(e){
		var target = $(new Event(e).target);
		if (['td', 'th'].contains(target.get('tag'))) {
			target = target.getElement('input');
			target.checked = !target.checked;
		}
		return target;
	}

});

var CrudTable = new Class({

	Extends: BulkTableManager,

	options: {
		addButton: 'add-btn',
		addModal: 'add-box',
		addModalOptions: {
			ajax: true,
			focus: 'name',
			slugifyField: 'name',
			resetOnComplete: true
		},
		editModal: 'edit-box',
		editModalOptions: {
			ajax: true,
			focus: 'name'
		},
		deleteModal: 'delete-box',
		deleteModalOptions: {
			ajax: true,
			focus: 'cancel',
			extraData: {'delete': 1}
		}
	},

	addModal: null,
	editModal: null,
	deleteModal: null,

	init: function(){
		this.addModal = new ModalForm(this.options.addModal, this.options.addModalOptions);
		this.editModal = new ModalForm(this.options.editModal, this.options.editModalOptions);
		this.deleteModal = new ModalForm(this.options.deleteModal, this.options.deleteModalOptions);
	},

	attach: function(){
		this.parent();
		$(this.options.addButton).addEvent('click', this.addModal.open.bind(this.addModal));
		this.table.addEvents({
			'click:relay(.btn-inline-edit)': this.editModal.open.bind(this.editModal),
			'click:relay(.btn-inline-delete)': this.deleteModal.open.bind(this.deleteModal)
		});
		this.addModal.addEvent('open', this.addModal.setValues.bind(this.addModal, [{}]));
		this.addModal.addEvent('complete', this.insertRow.bind(this));
		this.editModal.addEvent('complete', this.updateRow.bind(this));
		this.deleteModal.addEvent('complete', this.removeRow.bind(this));
	}

});

var TagTable = CrudTable;

var CategoryTable = new Class({

	Extends: CrudTable,

	options: {
		prefix: 'cat-',
		liStyles: ['disc', 'circle', 'square', 'circle'],
		depthPattern: /depth-([0-9]+)/
	},

	attach: function(){
		this.parent();
		this.addEvents({
			'insertRow': this.updateParentSelects.bind(this),
			'updateRow': this.updateParentSelects.bind(this),
			'removeRow': this.updateParentSelects.bind(this)
		});
		this.editModal.addEvent('open', this.disableCircularParentOptions.bind(this));
	},

	insertRow: function(resp){
		var newParent = resp.parent_id ? this.table.getElementById(this.options.prefix + resp.parent_id) : null;
		var newRow = Elements.from(resp.row)[0];
		this.injectUnderParent(newRow, newParent);
		this.fireEvent('updateRow', [newRow, resp]);
		return newRow.highlight();
	},

	updateRow: function(resp){
		var oldRow = $(this.options.prefix + resp.id);
		var oldParent = this.getParent(oldRow);
		var newParent = resp.parent_id ? this.table.getElementById(this.options.prefix + resp.parent_id) : null;
		var newRow = Elements.from(resp.row)[0];
		newRow.replaces(oldRow);
		if (newParent != oldParent) this.injectUnderParent(newRow, newParent);
		else if (this.getDepth(newRow) == this.getDepth(newRow.getPrevious())) newRow.removeClass('first-child');
		this.fireEvent('updateRow', [newRow, resp]);
		return newRow.highlight();
	},

	removeRow: function(resp){
		var row = this.table.getElementById(this.options.prefix + resp.id);
		var toDelete = [row].extend(this.getDescendants(row));
		if (row.hasClass('first-child')) {
			var rowSibling = toDelete[toDelete.length - 1].getNext();
			if (this.getDepth(row) == this.getDepth(rowSibling)) rowSibling.addClass('first-child');
		}
		this.fireEvent('removeRow', [row, resp]);
		toDelete.each(function(r){
			if (r) r.destroy();
		});
	},

	getDepth: function(row){
		if (!row) return null;
		var m = this.options.depthPattern.exec(row.className);
		if (m) return m[1].toInt();
	},

	getDescendants: function(row){
		var desc = [], next = row.getNext();
		// look at the next row down because the depth class for the given row may have changed already
		if (next && next.hasClass('first-child')) {
			var limit = this.getDepth(next);
			do {
				desc.push(next);
				next = next.getNext();
			} while (next && this.getDepth(next) >= limit);
		}
		return desc;
	},

	getParent: function(row){
		var depth = this.getDepth(row);
		if (depth == 0) return null;
		return row.getPrevious('tr.depth-' + (depth - 1));
	},

	injectUnderParent: function(row, newParent) {
		if (newParent) {
			var where = 'after';
			var next = newParent.getNext();
			if (next && next != row) next.removeClass('first-child'); // may or may not be applicable
		} else {
			var where = 'top';
			newParent = this.table.getElement('tbody');
		}
		var desc = this.getDescendants(row);
		if (desc.length) {
			var oldBaseDepth = this.getDepth(desc[0]), newBaseDepth = this.getDepth(row) + 1;
			var diff = oldBaseDepth - newBaseDepth;
			for (var descRow, i = desc.length; i--; ) {
				descRow = desc[i].inject(newParent, where);
				this.setDepthStyling(descRow, this.getDepth(descRow) - diff);
			}
		}
		row.inject(newParent, where);
	},

	setDepthStyling: function(row, depth){
		row.swapClass('depth-' + this.getDepth(row), 'depth-' + depth);
		row.setStyle('background-color', [
			(255 * Math.pow(0.915, depth)).toInt(),
			(255 * Math.pow(0.945, depth)).toInt(),
			(255 * Math.pow(0.955, depth)).toInt()
		].rgbToHex());
		var ul = row.getElement('td ul').setStyle('margin-left', (18 + 25 * depth) + 'px');
		ul.getElement('li').setStyle('list-style-type', this.options.liStyles[(depth - 1) % this.options.liStyles.length]);
		return row;
	},

	updateParentSelects: function(row, resp){
		var newSelect = Elements.from(resp.parent_options);
		var oldSelects = [this.addModal.form.elements['parent_id'], this.editModal.form.elements['parent_id']];
		oldSelects.each(function(select){
			newSelect.clone().replaces(select);
		});
	},

	disableCircularParentOptions: function(target, content, form){
		// don't allow users to set the parent cat to be the row they're editing, or any of its children
		var rowID = target.getParent('tr').id.replace(new RegExp(this.options.prefix.escapeRegExp()), '').toInt();
		var select = $(form.elements['parent_id']);
		var previouslyDisabledOpts = select.getElements('option:disabled').each(function(opt){
			opt.set('disabled', false);
		});
		var option = select.getElement('option[value=' + rowID + ']');
		var baseIndent = option.get('text').match(/^\s+/);
		var minIndent = (baseIndent ? baseIndent[0].length : 0) + 1;
		do {
			option = option.set('disabled', true).getNext();
			var m = option && option.get('text').match(/^\s+/);
			var indent = m ? m[0].length : 0;
		} while (indent >= minIndent);
	}

});

var BulkAction = new Class({

	Implements: [Events, Options],

	options: {
	/*	onClick: $empty,
		onConfirm: $empty,
		onComplete: $empty, */
		confirmMgr: false,
		saveUrl: null,
		saveData: {}
	},

	initialize: function(mgr, opts){
		this.mgr = mgr;
		this.setOptions(opts);
	},

	onClick: function(e){
		var numRows = this.mgr.getCheckedRows().length;
		if (this.options.confirmMgr === false) return this.sendRequest();
		if (!this.confirmMgr) {
			this.confirmMgr = new ConfirmMgr(this.options.confirmMgr)
				.addEvent('confirm', this.onConfirm.bind(this));
		}
		this.confirmMgr.openConfirmDialog(numRows);
	},

	onConfirm: function(){
		this.fireEvent('confirm');
		this.sendRequest();
	},

	onComplete: function(json){
		this.fireEvent('complete', [json]);
	},

	onError: function(){
		alert('An error occurred, please try again.');
	},

	sendRequest: function(){
		if (!this.options.saveUrl) return;
		var ids = this.mgr.getCheckedIds();
		if (!ids.length) return;
		if (!this.request) {
			this.request = new Request.JSON({
				url: this.options.saveUrl,
				onSuccess: this.onComplete.bind(this),
				onFailure: this.onError.bind(this)
			});
		}
		var data = $merge(this.options.saveData, {ids: ids});
		this.request.send(new Hash(data).toQueryString());
	}

});

var BulkEdit = new Class({

	Extends: BulkAction,

	onComplete: function(json){
		if (json.rows) {
			new Hash(json.rows).each(function(row, id){
				this.mgr.updateRow({id: id, row: row});
			}, this);
		}
		this.parent(json);
	}

});

var BulkDelete = new Class({

	Extends: BulkAction,

	options: {
		confirmMgr: {
			header: 'Confirm Delete',
			msg: function(num){ return 'Are you sure you want to delete these ' + num + ' items?'; },
			confirmButtonText: 'Delete',
			confirmButtonClass: 'btn red f-rgt',
			cancelButtonText: 'Cancel',
			cancelButtonClass: 'btn f-lft',
			focus: 'cancel'
		},
		refresh: false,
		refreshWhenPaginated: false
	},

	onComplete: function(json){
		json.ids.each(function(id){
			this.mgr.removeRow($merge(json, {id: id}));
		}, this);
		if (this.options.refresh || (this.options.refreshWhenPaginated && this.mgr.isPaginated())) window.location = window.location;
		this.parent(json);
	}

});

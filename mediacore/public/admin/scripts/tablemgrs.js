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
 * Editable Tables
 *
 * Requires:
 *  - Element.Delegation
 *  - Element.Shortcuts
 *  - Selectors
 *
 * @author Nathan Wright <nathan@simplestation.com>
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
	},

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
	}

});

var CrudTable = new Class({

	Extends: TableManager,

	options: {
		prefix: 'tag-',
		addButton: 'add-btn',
		addModal: 'add-box',
		addModalOptions: {
			ajax: true,
			focus: 'name',
			slugifyField: 'name'
		},
		editModal: 'edit-box',
		editModalOptions: {
			ajax: true,
			focus: 'name'
		},
		deleteModal: 'delete-box',
		deleteModalOptions: {
			ajax: true,
			focus: 'delete',
			extraData: {'delete': 1}
		},
	},

	addModal: null,
	editModal: null,
	deleteModal: null,

	initialize: function(table, opts){
		this.parent(table, opts);
		this.addModal = new ModalForm(this.options.addModal, this.options.addModalOptions);
		this.editModal = new ModalForm(this.options.editModal, this.options.editModalOptions);
		this.deleteModal = new ModalForm(this.options.deleteModal, this.options.deleteModalOptions);
		this.attach();
	},

	attach: function(){
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
		depthPattern: /depth-([0-9]+)/,
		bgDepthFactor: .95
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
		var intensity = (255 * Math.pow(this.options.bgDepthFactor, depth)).toInt();
		row.setStyle('background-color', [intensity, intensity, intensity].rgbToHex());
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

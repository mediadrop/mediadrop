/**
 * Confirm Delete Dialogue Script
 *
 * @requires   mootools-1.2-core.js
 * @requires   squeezebox.js
 *
 * @author     Anthony Theocharis <anthony@simplestation.com>
 * @version    $Id$
 * @copyright  Copyright (c) 2008, Simple Station Inc.
 */

var DeleteManager = new Class({

	initialize: function() {
		var links = $$('a.trash-comment');
		links.each(function(el) {
			el.addEvent('click', this.onClick.bind(this));
		}.bind(this));
		return this;
	},

	onClick: function(e) {
		e = new Event(e).stop();
		// The name is the content of the first TD in the row
		var row = e.target.parentNode.parentNode;
		var rowMgr = new RowManager(row, e.target.href);
		var author = row.getChildren()[1].getChildren()[0].textContent;

		// Set up the dialog box
		var box = new Element('div', {class: 'box'});
		var head = new Element('h1', {html: 'Confirm Delete',class: 'box-head'}).inject(box);
		var text = new Element('p', {html: 'Are you sure you want to delete <strong>' + author + '</strong>&#8217;s comment?'}).inject(box);
		var buttons = new Element('div', {class: 'box-foot'}).inject(box);
		var no = new Element('button', {class:'btn-no', html: 'No', events:{click:function(){SqueezeBox.close();}}}).inject(buttons);
		var yes = new Element('button', {class:'btn-yes',html: 'Yes', events:{click:function(){rowMgr.deleteRow();SqueezeBox.close();}}}).inject(buttons);

		SqueezeBox.fromElement(box, {handler: 'adopt', size: {y: '117px'}});

		return false;
	},
});

var RowManager = new Class({
	row: null,
	deleteUrl: null,

	initialize: function(row, deleteUrl){
		this.row = row;
		this.deleteUrl = deleteUrl;
	},

	deleteRow: function() {
		var req = new Request.HTML({url: this.deleteUrl});
		req.addEvent('success', this.removeRow.bind(this));
		req.get();
		return this;
	},
	
	removeRow: function() {
		this.row.destroy();
		return this;
	}
});

var EditText = new Class({
	initialize: function() {
		var editLinks = $$('a.edit-text');
		editLinks.each(function(link) {
			link.addEvent('click', this.onClick.bind(this));
		}.bind(this));
		return this;
	},

	onClick: function(e){
		e = new Event(e).stop();
		return false;
	}
});


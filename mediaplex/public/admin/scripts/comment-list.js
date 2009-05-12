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


var ConfirmManager = new Class({
	Implements: [Options, Events],

	options: {
		height: '117px'
		//onNo: $empty, (e.target)
		//onYes: $empty (e.target)
	},

	initialize: function(linkSelector, opts) {
		this.setOptions(opts);

		var links = $$(linkSelector);
		links.each(function(el) {
			el.addEvent('click', this.onClick.bind(this));
		}.bind(this));
		return this;
	},

	onClick: function(e) {
		e = new Event(e).stop();
		var a = $(e.target);

		// Set up the dialog box
		var box = new Element('div', {class: 'box'});
		var head = new Element('h1', {html: this.getHeaderText(a),class: 'box-head'}).inject(box);
		var text = new Element('p', {html: this.getPText(a)}).inject(box);
		var buttons = new Element('div', {class: 'box-foot'}).inject(box);
		var no = new Element('button', {class:'btn-no',html:'No',events:{click:function(){this.fireEvent('onNo',[a]);SqueezeBox.close();}.bind(this)}}).inject(buttons);
		var yes = new Element('button', {class:'btn-yes',html:'Yes',events:{click:function(){this.fireEvent('onYes',[a]);SqueezeBox.close();}.bind(this)}}).inject(buttons);

		SqueezeBox.fromElement(box, {handler: 'adopt', size: {y: this.options.height}});

		return false;
	},

	getHeaderText: function(a) {
		return 'Confirm';
	},

	getPText: function(a) {
		return 'Are you sure?';
	}
});

var DeleteManager = new Class({
	Extends: ConfirmManager,

	initialize: function(opts) {
		if(!$chk(opts)){opts = {};}
		opts.onYes = function(a){
			new RowManager(a).deleteRow();
		};
		this.parent('a.trash-comment', opts);
		return this;
	},

	getHeaderText: function(a) {
		return 'Confirm Delete';
	},

	getPText: function(a) {
		return 'Are you sure you want to delete <strong>' + new RowManager(a).getAuthor() + '</strong>&#8217;s comment?';
	},
});

var PublishManager = new Class({
	Extends: ConfirmManager,

	initialize: function(opts) {
		if(!$chk(opts)){opts = {};}
		opts.onYes = function(a){
			new RowManager(a).publishRow();
		};
		this.parent('a.review-comment', opts);
		return this;
	},

	getHeaderText: function(a) {
		return 'Confirm Publish';
	},

	getPText: function(a) {
		return 'Are you sure you want to publish <strong>' + new RowManager(a).getAuthor() + '</strong>&#8217;s comment?';
	},
});

var RowManager = new Class({
	row: null,
	actionUrl: null,

	initialize: function(a){
		this.row = a.parentNode.parentNode;
		this.actionUrl = a.href;
	},

	deleteRow: function() {
		var req = new Request.HTML({url: this.actionUrl});
		req.addEvent('success', this.removeRow.bind(this));
		req.get();
		return this;
	},

	publishRow: function() {
		var req = new Request.HTML({url: this.actionUrl});
		req.addEvent('success', this.grayRow.bind(this));
		req.get();
		return this;
	},

	grayRow: function() {
		this.row.addClass('tr-gray');
		return this;
	},

	removeRow: function() {
		this.row.destroy();
		return this;
	},

	getAuthor: function() {
		var author = this.row.getChildren('td.author').get('text');
		return author;
	}
});

//var EditText = new Class({
//	initialize: function() {
//		var editLinks = $$('a.edit-text');
//		editLinks.each(function(link) {
//			link.addEvent('click', this.onClick.bind(this));
//		}.bind(this));
//		return this;
//	},
//
//	onClick: function(e){
//		e = new Event(e).stop();
//		return false;
//	}
//});
//

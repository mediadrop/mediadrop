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

	options:{
		cancelButtonText: 'no',
		confirmButtonText: 'yes',
		confirmButtonClass: 'submitbutton btn-yes f-rgt',
		cancelButtonClass: 'submitbutton btn-no f-rgt',
		header: 'Confirm',
		msg: 'Are you sure?'
		//onConfirm: $empty (e.target)
	},


	initialize: function(linkSelector, opts){
		this.setOptions(opts);

		var links = $$(linkSelector);
		links.each(function(el) {
			el.addEvent('click', this.openConfirmDialog.bind(this));
		}.bind(this));
	},

	openConfirmDialog: function(e){
		e = new Event(e).stop();
		var target = $(e.target);

		// Set up the dialog box
		var header = $type(this.options.header) == 'function' ? this.options.header(target) :this.options.header;
		var msg = $type(this.options.msg) == 'function' ? this.options.msg(target) : this.options.msg;

		var box = new Element('div', {'class': 'box'});
		var head = new Element('h1', {'class': 'box-head', html: header}).inject(box);
		var text = new Element('p', {html: msg}).inject(box);
		var buttons = new Element('div', {'class': 'box-foot'}).inject(box);
		var confirmButton = new Element('button', {'class':this.options.confirmButtonClass, html: this.options.confirmButtonText}).inject(buttons);
		var cancelButton = new Element('button', {'class': this.options.cancelButtonClass, html: this.options.cancelButtonText}).inject(buttons);

		cancelButton.addEvent('click', this.cancel.pass(target, this));
		confirmButton.addEvent('click', this.confirm.pass(target, this));

		SqueezeBox.fromElement(box, {handler: 'fittedAdopt'});

		confirmButton.focus();
	},

	cancel: function(target){
		SqueezeBox.close();
	},

	confirm: function(target){
		SqueezeBox.close();
		this.fireEvent('onConfirm', [target]);
	},

});

var DeleteManager = new Class({

	Extends: ConfirmManager,

	initialize: function(linkSelector, opts) {
		this.addEvent('confirm', function(target){
			new Comment(target).deleteComment();
		});
		if(!$chk(opts.header)){
			opts.header = 'Confirm Delete';
		}
		if(!$chk(opts.msg)){
			opts.msg = function(target){
				return 'Are you sure you want to delete <strong>' + new Comment(target).getAuthor() + '</strong>&#8217;s comment?';
			};
		}
		this.parent(linkSelector, opts);
	},
});

var PublishManager = new Class({
	Extends: ConfirmManager,

	initialize: function(linkSelector, opts) {
		this.addEvent('confirm', function(target){
			new Comment(target).publishComment();
		});
		if(!$chk(opts.header)){
			opts.header = 'Confirm Publish';
		}
		if(!$chk(opts.msg)){
			opts.msg = function(target){
				return 'Are you sure you want to publish <strong>' + new Comment(target).getAuthor() + '</strong>&#8217;s comment?';
			};
		}
		this.parent(linkSelector, opts);
	}

});

var Comment = new Class({

	row: null,
	actionUrl: null,

	initialize: function(a){
		this.row = a.parentNode.parentNode;
		this.actionUrl = a.href;
	},

	deleteComment: function(){
		var req = new Request.HTML({url: this.actionUrl});
		req.addEvent('success', this.updateDeleted.bind(this));
		req.get();
		return this;
	},

	publishComment: function(){
		var req = new Request.HTML({url: this.actionUrl});
		req.addEvent('success', this.updatePublished.bind(this));
		req.get();
		return this;
	},

	updateDeleted: function(){
		this.row.destroy();
		return this;
	},

	updatePublished: function(){
		this.row.removeClass('tr-white').addClass('tr-gray');
		var unpublished = this.row.getElement('a.review-comment');
		var published = new Element('span', {class: 'published-comment', html: 'published'});
		published.replaces(unpublished);
		return this;
	},

	getAuthor: function(){
		var author = this.row.getChildren('.author').get('text');
		return new String(author).trim();
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

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


var ConfirmMgr = new Class({

	Implements: [Options, Events],

	options:{
		cancelButtonText: 'no',
		confirmButtonText: 'yes',
		confirmButtonClass: 'submitbutton btn-yes f-rgt',
		cancelButtonClass: 'submitbutton btn-no f-rgt',
		header: 'Confirm',
		msg: 'Are you sure?',
		overlayOpacity: 0.4
		//onConfirm: $empty (e.target)
	},

	initialize: function(opts){
		this.setOptions(opts);
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

		SqueezeBox.fromElement(box, {handler: 'fittedAdopt', overlayOpacity: this.options.overlayOpacity});

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

var CommentMgr = new Class({
	Implements: Options,

	options:{
		table: 'comment-table',
		formSelector: 'form.edit-comment-form',
		deleteLink: 'a.trash-comment',
		publishLink: 'a.review-comment'
	},

	initialize: function(opts) {
		this.setOptions(opts);
		this.processRows($(this.options.table).getElements('tbody > tr'));
	},

	processRows: function(rows) {
		$$(rows).each(function(row){
			var comment = new Comment(row, this.options);
		}.bind(this));
	}
});

var Comment = new Class({
	Implements: Options,

	options: null,

	row: null,
	publishLink: null,
	deleteLink: null,

	form: null,
	body: null,
	editLink: null,
	formVisible: true,

	initialize: function(row, options){
		this.setOptions(options);
		this.row = row;
		this.publishLink = row.getElement(this.options.publishLink);
		this.deleteLink = row.getElement(this.options.deleteLink);
		this.form = this.row.getElement(this.options.formSelector);

		if(this.publishLink != null) this.requestConfirmPublish();
		if(this.deleteLink != null) this.requestConfirmDelete();

		var td = this.form.getParent();
		var text = this.form.getElement('textarea').get('value');
		this.body = new Element('blockquote').grab(new Element('p', {html: text}));
		td.grab(this.body);
		this.editLink = new Element('a', {'class': 'edit-text', html: 'Edit Text'})
			.addEvent('click', this.toggleForm.bind(this));
		var span = td.getElement('span.comment-submitted').appendText(' | ').grab(this.editLink);
		var cancelButton = this.form.getElement('input.btn-cancel');
		cancelButton.addEvent('click', this.toggleForm.bind(this));

		var saveButton = this.form.getElement('input.btn-save');
		saveButton.addEvent('click', this.saveEditForm.bind(this));
		this.toggleForm();
	},

	requestConfirmPublish: function(){
		var confirmMgr = new ConfirmMgr({
			onConfirm: this.doConfirm.pass([this.publishLink.href, this.updatePublished.bind(this)], this),
			header: 'Confirm Publish',
			msg: 'Are you sure you want to publish <strong>' + this.getAuthor() + '</strong>&#8217;s comment?'
		});
		this.publishLink.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr({
			onConfirm: this.doConfirm.pass([this.deleteLink.href, this.updateDeleted.bind(this)], this),
			header: 'Confirm Delete',
			msg: 'Are you sure you want to delete <strong>' + this.getAuthor() + '</strong>&#8217;s comment?'
		});
		this.deleteLink.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	doConfirm: function(href, successAction){
		var opts = {url: href, onSuccess: successAction}
		new Request.HTML(opts).get();
		return this;
	},

	updatePublished: function(){
		this.row.removeClass('tr-white').addClass('tr-gray');
		var unpublished = this.row.getElement('a.review-comment');
		var published = new Element('span', {class: 'published-comment', html: 'published'});
		published.replaces(unpublished);
		return this;
	},

	updateDeleted: function(){
		this.row.destroy();
		return this;
	},

	getAuthor: function(){
		var author = this.row.getElement('.author').getChildren('strong').get('text');
		return new String(author).trim();
	},

	toggleForm: function(){
		if(this.formVisible){
			this.body.setStyle('display', 'block');
			this.form.setStyle('display', 'none');
			this.editLink.set('html', 'Edit Text');
		} else {
			this.form.setStyle('display', 'block');
			this.body.setStyle('display', 'none');
			this.editLink.set('html', 'Cancel Edit');
		}
		this.formVisible = !this.formVisible;
		return this;
	},

	saveEditForm: function(){
		this.toggleForm();
		this.body.set('html', this.form.getElement('textarea').get('value'));
		this.form.send();
		return false;
	}
});

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
var CommentMgr = new Class({
	Implements: Options,

	options:{
		editText: 'Edit Text',
		editCancel: 'Cancel Edit',
		table: 'comment-table',
		editFormSelector: 'form.edit-comment-form',
		statusFormSelector: 'form.comment-status-form',
		deleteBtn: 'button.btn-inline-delete',
		publishBtn: 'button.btn-inline-approve',
		deleteConfirmMgr: {}
	},

	initialize: function(opts) {
		this.setOptions(opts);

		var rows = $(this.options.table).getElements('tbody > tr');
		var options = this.options;

		rows.each(function(row){
			if(row.getChildren().length != 1){
				var comment = new Comment(row, options);
			}
		});
	}
});

var Comment = new Class({
	Implements: Options,

	options: null,

	row: null,
	statusForm: null,
	publishBtn: null,
	deleteBtn: null,

	editForm: null,
	body: null,
	editLink: null,
	editFormVisible: true,

	initialize: function(row, options){
		this.setOptions(options);
		this.row = row;
		this.publishBtn = row.getElement(this.options.publishBtn);
		this.deleteBtn = row.getElement(this.options.deleteBtn);
		this.statusForm = row.getElement(this.options.statusFormSelector);
		this.editForm = row.getElement(this.options.editFormSelector);

		this.setupStatusForm();
		this.setupEditForm();

		setCommentInstance(row, this);
	},

	setupStatusForm: function() {
		// Use AJAX (json) to intercept submission of the status form.

		// Set up a confirm manager, and response handler for the delete button.
		if (this.deleteBtn) {
			var confirmMgr = new ConfirmMgr(this.options.deleteConfirmMgr);
			confirmMgr.addEvent('confirm', this.saveStatusForm.pass([this.deleteBtn], this));
			confirmMgr.options.msg = confirmMgr.options.msg(this.getAuthor());
			this.deleteBtn.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		}

		// Set up a response handler for the publish button.
		if (this.publishBtn) {
			this.publishBtn.addEvent('click', this.saveStatusForm.bind(this));
		}
	},

	setupEditForm: function() {
		var td = this.editForm.getParent();
		var text = this.editForm.getElement('textarea').get('value');
		this.body = new Element('blockquote', {html: text});
		td.grab(this.body);
		this.editLink = new Element('span', {'class': 'edit-text clickable', text: this.options.editText});
		this.editLink.addEvent('click', this.toggleEditForm.bind(this));
		var span = td.getElement('div.comment-submitted').appendText(' | ').grab(this.editLink);
		var cancelButton = this.editForm.getElement('button.btn-cancel');
		if (cancelButton)
			cancelButton.addEvent('click', this.toggleEditForm.bind(this));

		this.editForm.addEvent('submit', this.saveEditForm.bind(this));
		this.toggleEditForm();
	},

	updatePublished: function(){
		this.row.removeClass('tr-white').addClass('tr-gray');
		if (this.publishBtn) {
			var publishedBtn = new Element('span', {
				'class': 'btn table-row published btn-inline-approve middle f-lft',
				html: '<span></span>'
			});
			publishedBtn.replaces(this.publishBtn);
			this.publishBtn = null;
		}
		return this;
	},

	updateDeleted: function(){
		this.row.destroy();
		return this;
	},

	getAuthor: function(){
		var author = this.row.getElement('.author-name').get('text');
		return new String(author).trim();
	},

	toggleEditForm: function(){
		if(this.editFormVisible){
			this.body.setStyle('display', 'block');
			this.editForm.setStyle('display', 'none');
			this.editLink.set('text', this.options.editText);
		} else {
			this.editForm.setStyle('display', 'block');
			this.body.setStyle('display', 'none');
			this.editLink.set('text', this.options.editCancel);
		}
		this.editFormVisible = !this.editFormVisible;
		return this;
	},

	saveEditForm: function(e){
		// Stop submission of the form
		e = new Event(e).stop();

		// Submit via ajax (json)
		this.toggleEditForm();
		this.editForm.set('send', {
			onComplete: function(response) {
				this.body.set('html', JSON.decode(response).body);
			}.bind(this)
		});
		this.editForm.send();
	},

	saveStatusForm: function(e){
		// Determine which button was used to submit the form:
		if ($type(e) == 'event') {
			e = new Event(e).stop();
			var submitBtn = $(e.target);
		} else {
			var submitBtn = e;
		}

		if (submitBtn.get('tag') != 'button') submitBtn = submitBtn.getParent('button');

		// Choose the appropriate onSuccess action:
		if (submitBtn == this.deleteBtn) {
			var successAction = this.updateDeleted.bind(this);
		} else if (submitBtn == this.publishBtn) {
			var successAction = this.updatePublished.bind(this);
		} else {
			// If it's not a publish or delete request, this manager doesn't know
			// how to deal with it.
			throw Error('unrecognized submit button');
		}

		// Submit the form, including the information on which button was clicked.
		var opts = {
			data: {},
			onSuccess: successAction,
			url: this.statusForm.action,
			method: this.statusForm.method
		}
		opts.data[submitBtn.name] = submitBtn.value;
		var r = new Request.JSON(opts);
		r.send()
	}
});

function getCommentInstance(row) {
	return row.commentInstance;
}
function setCommentInstance(row, comment) {
	row.commentInstance = comment;
}

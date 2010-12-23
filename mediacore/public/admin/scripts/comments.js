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
var CommentMgr = new Class({
	Implements: Options,

	options:{
		editText: 'Edit Text',
		editCancel: 'Cancel Edit',
		table: 'comment-table',
		formSelector: 'form.edit-comment-form',
		deleteLink: 'a.btn-inline-delete',
		publishLink: 'a.btn-inline-approve',
		bulkPublishBtnClass: 'btn btn-inline-approve f-lft',
		bulkDeleteBtnClass: 'btn btn-inline-delete f-rgt',
		deleteConfirmMgr: {}
	},

	bulkMgr: null,

	initialize: function(opts) {
		this.setOptions(opts);
		this.processRows($(this.options.table).getElements('tbody > tr'));
	},

	processRows: function(rows) {
		$$(rows).each(function(row){
			if(row.getChildren().length != 1)
				var comment = new Comment(row, this.options);
		}.bind(this));
	},

	_bulkSubmit: function(action, errorMsg) {
		var r = new Request.HTML({url: action, onSuccess: function(){location.reload();}})
			.send(new Hash({'ids': ''+this._getSelectedCommentIds()}).toQueryString());
		return this;
	},

	_getSelectedCommentIds: function() {
		return this.bulkMgr.getSelectedRows().map(function(row){
			return row.get('id');
		});
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
		this.form = row.getElement(this.options.formSelector);

		if (this.publishLink != null) this.requestConfirmPublish();
		if (this.deleteLink != null) this.requestConfirmDelete();

		var td = this.form.getParent();
		var text = this.form.getElement('textarea').get('value');
		this.body = new Element('blockquote', {html: text});
		td.grab(this.body);
		this.editLink = new Element('span', {'class': 'edit-text clickable', text: this.options.editText})
			.addEvent('click', this.toggleForm.bind(this));
		var span = td.getElement('div.comment-submitted').appendText(' | ').grab(this.editLink);
		var cancelButton = this.form.getElement('button.btn-cancel');
		cancelButton.addEvent('click', this.toggleForm.bind(this));

		this.form.addEvent('submit', this.saveEditForm.bind(this));
		this.toggleForm();
	},

	requestConfirmPublish: function(){
/*		var confirmMgr = new ConfirmMgr({
			onConfirm: this.doConfirm.pass([this.publishLink.href, this.updatePublished.bind(this)], this),
			header: 'Confirm Publish',
			confirmButtonText: 'Publish',
			confirmButtonClass: 'btn green f-rgt',
			cancelButtonText: 'Cancel',
			msg: 'Are you sure you want to publish <strong>' + this.getAuthor() + '</strong>&#8217;s comment?'
		});
		this.publishLink.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));*/
		this.publishLink.addEvent('click', function(e){
			e = new Event(e).stop();
			this.doConfirm(this.publishLink.href, this.updatePublished.bind(this));
		}.bind(this));
		return this;
	},

	requestConfirmDelete: function(){
		var confirmMgr = new ConfirmMgr(this.options.deleteConfirmMgr)
			.addEvent('confirm', this.doConfirm.pass([this.deleteLink.href, this.updateDeleted.bind(this)], this));
		confirmMgr.options.msg = confirmMgr.options.msg(this.getAuthor());

		this.deleteLink.addEvent('click', confirmMgr.openConfirmDialog.bind(confirmMgr));
		return this;
	},

	doConfirm: function(href, successAction){
		var r = new Request.HTML({url: href, onSuccess: successAction}).get();
		return this;
	},

	updatePublished: function(){
		this.row.removeClass('tr-white').addClass('tr-gray');
		var unpublished = this.row.getElement('a.btn-inline-approve');
		var published = new Element('span', {'class': 'btn table-row published unclickable btn-inline-approved f-lft', html: '<span>published</span>'});
		published.replaces(unpublished);
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

	toggleForm: function(){
		if(this.formVisible){
			this.body.setStyle('display', 'block');
			this.form.setStyle('display', 'none');
			this.editLink.set('text', this.options.editText);
		} else {
			this.form.setStyle('display', 'block');
			this.body.setStyle('display', 'none');
			this.editLink.set('text', this.options.editCancel);
		}
		this.formVisible = !this.formVisible;
		return this;
	},

	saveEditForm: function(e){
		this.form.fireEvent('beforeAjax');
		this.toggleForm();
		this.form.set('send', {onComplete: function(response) {
			this.body.set('html', JSON.decode(response).body);
		}.bind(this)});
		this.form.send();
		return false;
	}
});

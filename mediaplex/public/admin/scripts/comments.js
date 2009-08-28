/**
 * @requires confirm.js
 */
var CommentMgr = new Class({
	Implements: Options,

	options:{
		table: 'comment-table',
		formSelector: 'form.edit-comment-form',
		deleteLink: 'a.trash-comment',
		publishLink: 'a.review-comment',
		bulkPublishBtnClass: 'bulk-publish-btn mo',
		bulkDeleteBtnClass: 'bulk-delete-btn mo',
	},

	bulkMgr: null,

	initialize: function(bulkApproveAction, bulkDeleteAction, opts) {
		this.setOptions(opts);
		this.processRows($(this.options.table).getElements('tbody > tr'));

		var publishBtn = new Element('a', {href: '#', 'class': this.options.bulkPublishBtnClass})
			.grab(new Element('span', {html: 'Publish'}));
		var publishConfirmMgr = new ConfirmMgr({
			onConfirm: this._bulkSubmit.pass([bulkApproveAction, 'Unable to publish the selected comments'], this),
			header: 'Confirm Publish',
			msg: 'Are you sure you want to publish these comments?'
		});
		publishBtn.addEvent('click', publishConfirmMgr.openConfirmDialog.bind(publishConfirmMgr));

		var deleteBtn = new Element('a', {href: '#', 'class': this.options.bulkDeleteBtnClass})
			.grab(new Element('span', {html: 'Delete'}));
		var deleteConfirmMgr = new ConfirmMgr({
			onConfirm: this._bulkSubmit.pass([bulkDeleteAction, 'Unable to delete the selected comments'], this),
			header: 'Confirm Delete',
			msg: 'Are you sure you want to delete these comments?'
		});
		deleteBtn.addEvent('click', deleteConfirmMgr.openConfirmDialog.bind(deleteConfirmMgr));

		var trs = $(this.options.table).getElement('tbody').getElements('tr');
		if(trs.length != 1 || trs[0].getElements('td').length != 1) {
			/* Only show if there are comments -- not if there is the single row with a single cell 'None Found' */
			var h1 = $(this.options.table).getPrevious().getElement('h1');
			this.bulkMgr = new BulkMgr(h1, $(this.options.table), [publishBtn, deleteBtn]);
		}
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
	},

});

var BulkMgr = new Class({
	Implements: Options,

	options:{
		bulkDivClass: 'bulk-div f-lft',
		bulkBtnClass: 'bulk-btn mo',
		selectDivClass: 'select-div f-rgt',
		selectAllClass: 'select-all',
		selectNoneClass: 'select-none',
		dividerClass: 'select-divider',
		userActionDivClass: 'bulk-user-action-div f-rgt',
		selectCol: 0,
		checkedColClass: 'checkbox-col'
	},

	slidingDiv: null,
	slidingDivWidth: null,
	bulkBtn: null,
	bulkActionDiv: null,
	actionsVisible: true,
	table: null,

	initialize: function(h1, table, actions, opts) {

		this.table = table;

		var bulkDiv = new Element('div', {'class': this.options.bulkDivClass});
		bulkDiv.inject(h1.getParent(), 'after');
		bulkDiv.setStyle('position', 'relative');

		// build bulk button
		this.bulkBtn = new Element('a', {href: '#', 'class': this.options.bulkBtnClass})
			.addEvent('click', this._toggleBulk.bind(this));
		this.bulkBtn.grab(new Element('span', {html: 'Bulk mode'}));
		this.bulkBtn.set('styles', {
			'position': 'absolute',
			'top': '0',
			'left': '0',
			'z-index': '1'
		});

		// build div to hold actions
		var selectAll = new Element('a', {href: '#', html: 'Select All', 'class': this.options.selectAllClass})
			.addEvent('click', this._select.pass(true, this));
		var divider = new Element('span', {html: '|', 'class': this.options.dividerClass});
		var selectNone = new Element('a', {href: '#', html: 'Select None', 'class': this.options.selectNoneClass})
			.addEvent('click', this._select.pass(false,this));
		this.selectDiv = new Element('div', {'class': this.options.selectDivClass});
		this.selectDiv.adopt(selectAll, divider, selectNone);

		var userActionDiv = new Element('div', {'class': this.options.userActionDivClass});
		for(var i=0; i < actions.length; i++){
			userActionDiv.grab(actions[i]);
		}

		this.slidingDiv = new Element('div', {'class': 'sliding-div'});
		this.slidingDiv.set('styles', {
			'overflow': 'hidden',
			'position': 'absolute',
			'top': '0',
			'left': '50px',
			'z-index': '0'
		});
		this.slidingDiv.adopt(userActionDiv, this.selectDiv);
		bulkDiv.adopt(this.bulkBtn, this.slidingDiv);

		this.slidingDivWidth = this.slidingDiv.offsetWidth + 10;
		this.slidingDiv.setStyle('width', '0');

		this.table.getElement('tbody').getElements('tr').each(function(row){
			var checkTd = new Element('td', {'class': this.options.checkedColClass})
				.setStyle('display', 'none');
			var selectCol = row.getChildren()[this.options.selectCol];
			checkTd.inject(selectCol, 'after');
			checkTd.grab(new Element('input', {'type': 'checkbox', 'value': '?', 'checked': false}));
		}.bind(this));

		this._toggleBulk();
	},

	_toggleBulk: function() {
		var hideCol = this.options.selectCol;
		var showCol = this.options.selectCol;

		if(this.actionsVisible) {
			// hide actions
			this.bulkBtn.removeClass('reverse-mo');
			this.bulkBtn.addClass('mo');
			this.slidingDiv.get('tween').start('width', this.slidingDiv.offsetWidth, '0');
			hideCol++;
		} else {
			// show actions
			this.bulkBtn.removeClass('mo');
			this.bulkBtn.addClass('reverse-mo');
			this.slidingDiv.get('tween').start('width', this.slidingDiv.offsetWidth, this.slidingDivWidth);
			showCol++;
		}

		this.table.getElement('tbody').getElements('tr').each(function(row){
			row.getChildren()[hideCol].setStyle('display', 'none');
			row.getChildren()[showCol].setStyle('display', '');
		}.bind(this));

		this.actionsVisible = !this.actionsVisible;
	},

	_select: function(toCheck){
		$$('td.'+this.options.checkedColClass+' > input[type=checkbox]').set('checked', toCheck);
	},

	getSelectedRows: function() {
		return $$('td.'+this.options.checkedColClass+' > input[type=checkbox]:checked').map(function(input){
			return input.getParent('tr');
		});
	},
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
		this.editLink = new Element('span', {'class': 'edit-text clickable', text: 'Edit Text'})
			.addEvent('click', this.toggleForm.bind(this));
		var span = td.getElement('div.comment-submitted').appendText(' | ').grab(this.editLink);
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
		var r = new Request.HTML({url: href, onSuccess: successAction}).get();
		return this;
	},

	updatePublished: function(){
		this.row.removeClass('tr-white').addClass('tr-gray');
		var unpublished = this.row.getElement('a.review-comment');
		var published = new Element('span', {'class': 'published-comment', text: 'published'});
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
			this.editLink.set('text', 'Edit Text');
		} else {
			this.form.setStyle('display', 'block');
			this.body.setStyle('display', 'none');
			this.editLink.set('text', 'Cancel Edit');
		}
		this.formVisible = !this.formVisible;
		return this;
	},

	saveEditForm: function(){
		this.toggleForm();
		this.form.set('send', {onComplete: function(response) {
			this.body.set('html', JSON.decode(response).body);
		}.bind(this)});
		this.form.send();
		return false;
	}
});

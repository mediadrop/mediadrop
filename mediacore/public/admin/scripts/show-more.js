/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

var ShowMore = new Class({
	Implements: [Options, Events],

	options: {
	//	onMore: $empty,
		table: null,
		fetchUrl: '', // If no URL is passed the current URL is used
		page: 1,
		lastPage: 1,
		numColumns: null,
		request: {method: 'get'}
	},

	table: null,
	tbody: null,
	button: null,
	buttonWrapper: null,

	fetchReq: null,
	fetchUrl: null,
	lastLoadedPage: 1,
	fxTween: null,

	initialize: function(opts){
		this.setOptions(opts);
		if (this.options.page != this.options.lastPage) {
			this.table = $(this.options.table);
			this.tbody = this.table.getElement('tbody').setStyle('overflow', 'hidden');
			this.lastLoadedPage = this.options.page;
			this._setupButton();
		}
	},

	fetchMore: function(){
		if (!this.fetchReq) {
			this.fetchUrl = new URI(this.options.fetchUrl ? this.options.fetchUrl : window.location);
			this.fetchReq = new Request.HTML(this.options.request).addEvent('success', this.injectMore.bind(this));
		}
		this.lastLoadedPage += 1;
		this.fetchReq.send({url: this.fetchUrl.setData({page: this.lastLoadedPage}, true).toString()});
		if (!this.fxTween) {
			var unlockHeight = function(){ this.tbody.setStyle('height', 'auto'); }.bind(this);
			this.fxTween = this.tbody.get('tween').addEvent('complete', unlockHeight, true);
		}
		return this;
	},

	injectMore: function(tableTree){
		// temporarily lock the height of the table while we inject the new rows
		var newHeight = origHeight = this.tbody.getHeight();
		this.tbody.setStyle('height', origHeight);

		// inject the tables rows, adding up their heights as they're rendered outside the overflow
		var newRows = $$(tableTree)[0].getChildren('tbody').getChildren('tr');
		for (var i = 0, l = newRows.length; i < l; i++) {
			newHeight += newRows[i].inject(this.tbody).getHeight();
		}
		this.fireEvent('more', [newRows]);

		// animate the increase in height then remove the height lock after
		this.fxTween.start('height', origHeight, newHeight);

		if (this.lastLoadedPage >= this.options.lastPage) {
			this._removeButton();
		}
	},

	_setupButton: function(){
		this.button = new Element('span', {text: 'show more', 'class': 'show-more clickable'})
			.addEvent('click', this.fetchMore.bind(this));
		var numCols = this.options.numColumns;
		if (numCols == null) {
			numCols = this.table.getChildren('thead')[0].getChildren('tr')[0].getChildren('th').length;
		}
		this.buttonWrapper = new Element('tfoot').grab(
			new Element('tr').grab(
				new Element('td', {colspan: numCols, 'class': 'box-foot center'}).grab(this.button)
			)
		).inject(this.table);
	},

	_removeButton: function(){
		this.buttonWrapper.dispose();
	}
});

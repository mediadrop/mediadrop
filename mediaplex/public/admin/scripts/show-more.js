var ShowMore = new Class({

	Extends: Options,

	options: {
		table: null,
		pageNum: 1,
		lastPage: 1,
		searchString: null,
		fetchPageUrl: ''
	},

	lastLoadedPage: 1,

	initialize: function(opts){
		this.setOptions(opts);

		if (this.options.pageNum != this.options.lastPage) {
			this._setupButtons();
		}
		this.lastLoadedPage = this.options.pageNum;
	},

	_setupButtons: function(){
		var table = $(this.options.table);
		var tbody = table.getChildren('tbody')[0];
		tbody.setStyles({'height': tbody.getHeight(), overflow: 'hidden'});

		var showMore = new Element('span', {text: 'show more', 'class': 'show-more clickable'});
		showMore.addEvent('click', this.loadMore.bind(this));
		var numCols = table.getChildren('thead')[0].getChildren('tr')[0].getChildren('th').length;
		var tfoot = new Element('tfoot').grab(
			new Element('tr').grab(
				new Element('td', {colspan: numCols, 'class': 'box-foot center'}).grab(showMore)
			)
		).inject(table);
	},

	loadMore: function(){
		this.lastLoadedPage += 1;
		this.fetchRows.delay(0, this, [this.lastLoadedPage]);
		return this;
	},

	fetchRows: function(i){
		var req = new Request.HTML({url: this.options.fetchPageUrl});
		req.addEvent('success', this.injectRows.bind(this));
		req.get({page_num: i, searchquery: this.options.searchString});
		return this;
	},

	injectRows: function(tree, els, xhtml){
		var table = $(this.options.table);
		var tbody = table.getChildren('tbody')[0];

		var trs = els.filter('tr');
		trs.each(function(row){
			row.inject(tbody);
		});
		var tbodyHeight = tbody.getHeight().toInt();
		var trsHeight = trs.length.toInt()*40;
		var heightSum = tbodyHeight + trsHeight;
		tbody.tween('height', heightSum);

		if (this.lastLoadedPage >= this.options.lastPage) {
			table.getChildren('tfoot')[0].dispose();
		}
		return this;
	}
});

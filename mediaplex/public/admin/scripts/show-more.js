var ShowMore = new Class({
	Extends: Options,

	options: {
		pageNum: 1,
		lastPage: 1,
		searchString: null
	},

	lastLoadedPage: 1,

	/* Requires table id to be passed in */
	initialize: function(opts){
		this.setOptions(opts);

		if(this.options.pageNum != this.options.lastPage) {
			this._setupButtons();
		}
		this.lastLoadedPage = this.options.pageNum;
	},

	_setupButtons: function(){
		table = $(this.options.tableId);
		var tbody = table.getChildren('tbody')[0];

		tbody.setStyles({'height': tbody.getHeight(), 'overflow': 'hidden'});
		var showMore = new Element('span',{'text':'show more', 'class': 'show-more'});
		showMore.addEvent('click', this.loadMore.bind(this));
		var numCols = table.getChildren('thead')[0].getChildren('tr')[1].getChildren('th').length;
		var tfoot = new Element('tfoot').grab(new Element('tr').grab(new Element('td', {'colspan':numCols}).grab(showMore))
		).inject(table);
		var next = table.getNext();
		if(next.get('tag') == 'div' && next.hasClass('rounded-bottom-white')) {
			next.removeClass('rounded-bottom-white').addClass('rounded-bottom-beige');
		}
	},

	loadMore: function(){
		this.lastLoadedPage += 1;
		this.fetchRows.delay(0, this, [this.lastLoadedPage]);
		return this;
	},

	fetchRows: function(i){
		var req = new Request.HTML({url: this.options.fetchPageUrl});
		req.addEvent('success', this.injectRows.bind(this));
		req.get({page_num: i, search_string: this.options.searchString});
		return this;
	},

	injectRows: function(tree, els, xhtml){
		var table = $(this.options.tableId);
		var tbody = table.getChildren('tbody')[0];

		var trs = els.filter('tr');
		trs.each(function(row){
			row.inject(tbody);
		});
		var tbodyHeight = tbody.getHeight().toInt();
		var trsHeight = trs.length.toInt()*40;
		var heightSum = tbodyHeight + trsHeight;
		tbody.tween('height', heightSum);

		if(this.lastLoadedPage >= this.options.lastPage){
			table.getChildren('tfoot')[0].dispose();
			var next = table.getNext();

			if(next.get('tag') == 'div' && next.hasClass('rounded-bottom-beige')) {
				next.removeClass('rounded-bottom-beige').addClass('rounded-bottom-white');
			}
		}
		return this;
	}
});

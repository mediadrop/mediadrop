var Mediaflow = new Class({
	Extends: Options,

	options: {
		totalPageCount: 0,
		container: 'mediaflow',
		pageElement: 'div',
		pageClass: 'mediaflow-page',
		pageLoadingClass: 'mediaflow-page-loading',
		itemSelector: 'a',
		itemHighlightClass: 'active',
		labelContainer: 'mediaflow-label',
		ctrlsContainer: null,
		pageWidth: 0,
		pageHeight: 0,
		pageMargin: 30,
		fetchPageUrl: '/video/ajax',
		numPagesPerFetch: 2,
		fx: {
			duration: 550,
			transition: Fx.Transitions.Quad.easeInOut,
			wheelStops: false
		}
	},

	pages: [],
	pageIndex: 0,
	highlightedItem: null,

	fxScroll: null,
	label: null,

	initialize: function(opts){
		this.setOptions(opts);

		var container = $(this.options.container);
		var pageSelector = this.options.pageElement + '.' + this.options.pageClass;

		if (!this.options.pageWidth)  { this.options.pageWidth  = container.getStyle('width').toInt(); }
		if (!this.options.pageHeight) { this.options.pageHeight = container.getStyle('height').toInt(); }

		this.pages = container.getElements(pageSelector).map(this._setupPageStyles, this);
		this.pages.map(this._setupPageItems, this);

		this.fxScroll = new Fx.Scroll(container, this.options.fx);

		this._setupButtons();
		this._setupHighlight();
	},

	slideToNext: function(){
		this.slideToPage(this.pageIndex + 1);
		return this;
	},

	slideToPrev: function(){
		this.slideToPage(this.pageIndex - 1);
		return this;
	},

	slideToPage: function(i){
		if (i >= this.options.totalPageCount) { i = this.options.totalPageCount - 1; }
		else if (i < 0) { i = 0; }

		if (this.pages[i] == undefined) {
			this.injectPage(i, this.createPagePlaceholder());
			// request the next page in a separate thread
			this.fetchPages.delay(0, this, [i]);
		} else if (this.pages[i].hasClass('loading')) {
			// do nothing if the request has already been made and they've clicked again
			return this;
		}

		this.pageIndex = i;
		this.fxScroll.toElement(this.pages[this.pageIndex]);
		this.highlightItem(null, null, '', '');
		return this;
	},

	fetchPages: function(i){
//		var spr = new Spinner({request: req}).el.inject(page);
		var req = new Request.HTML({url: this.options.fetchPageUrl});
		req.addEvent('success', this.injectPages.bind(this));
		req.get({page: i + 1, pages_at_once: this.options.numPagesPerFetch});
		return this;
	},

	injectPages: function(tree, els, xhtml){
		var loadingPageIndex = this.pages.length - 1;
		els.filter(this.options.pageElement + '.' + this.options.pageClass)
		   .each(function(page, i){
			var pageIndex = loadingPageIndex + (i*1);
			this._setupPageStyles(page, pageIndex);
			this._setupPageItems(page);
			if (this.pages[pageIndex] != undefined) {
				this.pages[pageIndex].destroy();
			}
			this.pages[pageIndex] = page.inject(this.pages[pageIndex - 1], 'after');
		}, this);
	},

	createPagePlaceholder: function(){
		return new Element(this.options.pageElement, {
			'class': [this.options.pageClass, this.options.pageLoadingClass].join(' '), 
			'text': 'Loading...'
		});
	},

	injectPage: function(i, page){
		this.pages[i] = this._setupPageStyles(page, i).inject(this.pages[i - 1], 'after');
		return this;
	},

	_setupPageStyles: function(page, i){
		return page.setStyles({
			overflow: 'hidden',
			position: 'absolute',
			height: this.options.pageHeight + 'px',
			width: this.options.pageWidth + 'px',
			marginRight: this.options.pageMargin + 'px',
			top: 0,
			left: i * (this.options.pageWidth + this.options.pageMargin) + 'px'
		});
	},

	_setupPageItems: function(page){
		var items = page.getElements(this.options.itemSelector);
		items.each(this._setupItem, this);
		return this;
	},

	_setupItem: function(el){
		var info = el.get('title');
		var pos = info.indexOf(':');
		var title = info.substring(0, pos);
		var desc = info.substring(pos + 2);
		el.addEvent('mouseover', this.highlightItem.bindWithEvent(this, [el, title, desc]));
	},

	_setupButtons: function(){
		var container = $(this.options.ctrlsContainer);
		var next = new Element('span', {'id': 'mediaflow-next', 'class': 'clickable'})
			.grab(new Element('span', {'text': 'Next'})).inject(container, 'top');
		var prev = new Element('span', {'id': 'mediaflow-prev', 'class': 'clickable'})
			.grab(new Element('span', {'text': 'Previous'})).inject(container, 'top');
		next.addEvent('click', this.slideToNext.bind(this));
		prev.addEvent('click', this.slideToPrev.bind(this));
	},

	_setupHighlight: function(){
		var container = $(this.options.labelContainer);
		container.addClass('box-bottom-grey').removeClass('box-bottom');
		this.label = container.set('html', '&#160;');
	},

	highlightItem: function(e, el, title, desc){
		if (this.highlightedItem == el) {
			return; // dont reupdate when rolling over the inner <img>
		}
		if (this.highlightedItem) {
			this.highlightedItem.removeClass(this.options.itemHighlightClass); 
		}
		if (el == null) {
			this.label.set('html', '&#160;');
		} else {
			this.highlightedItem = el.addClass(this.options.itemHighlightClass);
			this.label.set('html', '<strong>' + title + '</strong>: ' + desc);
		}
	}
});

var Videoflow = new Class({
	Extends: Mediaflow,

	_setupButtons: function(){
		this.parent();
	}
});

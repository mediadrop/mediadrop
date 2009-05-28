var Mediaflow = new Class({

	Extends: Options,

	options: {
		totalPageCount: 0,
		container: 'mediaflow-body',
		pageElement: 'div',
		pageClass: 'mediaflow-page',
		pageLoadingClass: 'mediaflow-page-loading',
		itemSelector: 'a',
		itemHighlightClass: 'active',
		labelContainer: 'mediaflow-label',
		ctrlsContainer: 'mediaflow-ctrls',
		pageWidth: 0,
		pageHeight: 0,
		pageMargin: 30,
		fetchUrl: '',
		numPagesPerFetch: 2,
		fx: {
			duration: 550,
			transition: Fx.Transitions.Quad.easeInOut,
			wheelStops: false
		}
	},

	container: null,
	pages: [],
	pageIndex: 0,

	fxScroll: null,

	label: null,
	highlightedItem: null,

	initialize: function(opts){
		this.setOptions(opts);

		this.container = $(this.options.container).setStyle('overflow', 'hidden');
		var pageSelector = this.options.pageElement + '.' + this.options.pageClass;

		if (!this.options.pageWidth)  { this.options.pageWidth  = this.container.getStyle('width').toInt(); }
		if (!this.options.pageHeight) { this.options.pageHeight = this.container.getStyle('height').toInt(); }

		this.pages = this.container.getElements(pageSelector).map(this._setupPageStyles, this);
		this.pages.map(this._setupPageItems, this);

		this.fxScroll = new Fx.Scroll(this.container, this.options.fx);

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
		if (i >= this.options.totalPageCount) { i = 0; }
		else if (i < 0) { i = 0; }

		if (this.pages[i] == undefined) {
			this.injectPage(i, this.createPagePlaceholder());
			this.fetchPages.delay(0, this, [i]);
		} else if (this.pages[i].hasClass('loading')) {
			return this; // do nothing until the current page is loaded
		}

		this.pageIndex = i;
		this.fxScroll.toElement(this.pages[this.pageIndex]);
		this.highlightItem(null, null, '', '');
		return this;
	},

	fetchPages: function(i){
		var req = new Request.HTML({url: this.options.fetchUrl})
			.addEvent('success', this.injectPages.bind(this))
			.get({page: i + 1, pages_at_once: this.options.numPagesPerFetch});
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
		container.addClass('mediaflow-label');
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

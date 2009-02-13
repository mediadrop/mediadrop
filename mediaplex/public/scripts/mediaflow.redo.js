var Mediaflow = new Class({
	Extends: Options,

	options: {
		totalPageCount: 0,
		container: 'mediaflow',
		pageElement: 'div',
		pageClass: 'mediaflow-page',
		itemSelector: 'a',
		itemHighlightClass: 'active',
		labelContainer: 'mediaflow-label',
		ctrlsContainer: null,
		pageWidth: 0,
		pageHeight: 0,
		pageMargin: 30,
		fetchPageUrl: '/videos/ajax/',
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

		this.pages = container.getElements(pageSelector).map(this._setupPageStyles, this)
		this.pages.map(this._setupPageItems, this);

		this.fxScroll = new Fx.Scroll(container, this.options.fx);

		this._setupButtons();
	},

	slideToPage: function(i){
		if (i > this.options.totalPageCount) { i = this.options.totalPageCount; }
		else if (i < 0) { i = 0; }

		if (this.pages[i] == undefined) {
			this.fetchPage(i);
		}

		this.pageIndex = i;
		this.fxScroll.toElement(this.pages[this.pageIndex]);
		return this;
	},

	slideToNext: function(){
		this.slideToPage(this.pageIndex + 1);
		return this;
	},

	slideToPrev: function(){
		this.slideToPage(this.pageIndex - 1);
		return this;
	},

	fetchPage: function(i){
		var page = this.createPagePlaceholder();
		this.injectPage(i, page);

		var req = new Request.HTML({update: page, url: this.options.fetchPageUrl});
//		var spr = new Spinner({request: req}).el.inject(page);
		req.get({page: i + 1});
	},

	createPagePlaceholder: function(){
		return new Element(this.options.pageElement, {'class': this.options.pageClass, text: 'loading...'});
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

	highlightItem: function(e, el, title, desc){
		if (this.highlightedItem == el) { 
			return; // dont reupdate when rolling over the inner <img>
		}
		if (this.highlightedItem) { 
			this.highlightedItem.removeClass(this.options.itemHighlightClass); 
		}
		this.highlightedItem = el.addClass(this.options.itemHighlightClass);
		console.log(title + ' - ' + desc);
	}
});

var Videoflow = new Class({
	Extends: Mediaflow,

	_setupButtons: function(){
		this.parent();
	}
});

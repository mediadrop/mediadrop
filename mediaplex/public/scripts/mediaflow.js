var MediaflowPage = new Class({
	manager: null,
	element: null,
	covers: [],
	activeCover: 0,

	initialize: function(element, manager){
		this.element = $(element);
		this.manager = manager;
		this.covers = this.element.getElements('li').map(this._setupCover, this);
	},
	
	_setupCover: function(li){
		var titleEl = li.getFirst('.media-title');
		var descEl = li.getFirst('.media-desc');
		var cover = {
			'element': li,
			'title': titleEl.get('text'),
			'desc': descEl.get('text')
		};
		titleEl.destroy();
		descEl.destroy();
		li.addEvent('mouseover', this._activateCover.pass(cover, this));
		return cover;
	},

	_activateCover: function(cover){
		if (this.activeCover) { this.activeCover.element.removeClass('active'); }
		this.activeCover = cover;
		cover.element.addClass('active');

		this.manager.display.run([cover.title, cover.desc], this.manager);
	}
});

var Mediaflow = new Class({
	Extends: Options,

	options: {
		'fx': {
			'duration': 550,
			'transition': Fx.Transitions.Quad.easeInOut,
			'wheelStops': false
		},
		'pageContainer': 'mediaflow',
		'pageSelector': 'div.mediaflow-page',
		'pageMargin': 30,
		'labelContainer': 'mediaflow-label',
		'nextButton': null,
		'prevButton': null,
		'ctrlsContainer': null
	},

	pageContainer: null,
	currentPage: 0,
	pages: [],
	fxScroll: null,
	label: null,

	_pageClass: MediaflowPage,

	initialize: function(options){
		this.setOptions(options);

		this.pageContainer = $(this.options.pageContainer);
		this.pages = this._setupPages(this.pageContainer.getElements(this.options.pageSelector));

		this.fxScroll = new Fx.Scroll(this.pageContainer, this.options.fx);

		this.label = $(this.options.labelContainer)
			.addClass('box-bottom-grey').removeClass('box-bottom');

		this._setupBtnEle(this.options.nextButton, 'Next').addEvent('click', this.next.bind(this));
		this._setupBtnEle(this.options.prevButton, 'Back').addEvent('click', this.prev.bind(this));
	},

	next: function(e){
		new Event(e).stop();
		this.slideTo(this.currentPage + 1);
		return this;
	},

	prev: function(e){
		new Event(e).stop();
		this.slideTo(this.currentPage - 1);
		return this;
	},

	slideTo: function(page){
		this.currentPage = page % this.pages.length;
		if (this.currentPage < 0) { this.currentPage += this.pages.length; }
		this.fxScroll.toElement(this.pages[this.currentPage].element);
		return this;
	},

	display: function(title, desc){
		this.label.empty().grab(
			new Element('p').grab(
				new Element('strong', {'text': title})).appendText(' — ' + desc));
		return this;
		
	},

	_setupContainer: function(container){
		return $(container).setStyles({'position': 'relative', 'overflow': 'hidden'});
	},

	_setupPages: function(pageEls){
		var width  = this.pageContainer.getStyle('width').toInt();
		var height = this.pageContainer.getStyle('height');
		var pages  = pageEls.map(function(page, i){
			page.setStyles({
				'overflow': 'hidden',
				'position': 'absolute',
				'height': height + 'px',
				'width': width + 'px',
				'marginRight': this.options.pageMargin + 'px',
				'top': 0,
				'left': i * (width + this.options.pageMargin) + 'px'
			});
			return new this._pageClass(page, this);
		}, this);

		return pages;
	},

	_setupBtnEle: function(button, defaultText){
		var el = $(button);
		if (!el && $type(button) == 'string') {
			el = new Element('span', {'id': button, 'class': 'clickable'})
				.grab(new Element('span', {'text': defaultText}))
				.inject($(this.options.ctrlsContainer), 'top');
		}
		return el;
	}
});

window.addEvent('domready', function(){
	var searchLbl = $('nav-search-input');
	if (searchLbl) var l = new OverText(searchLbl, {wrap: true, positionOptions: {x: 14, y: 12}});
});

window.addEvent('domready', function(){
	var likeBtns = $$('a.meta-likes');
	if (likeBtns) {
		likeBtns.addEvent('click', function(e){
			var btn = new Event(e).stop().target;
			if (btn.get('tag') != 'a') btn = btn.getParent('a');
			var req = new Request({url: btn.get('href')}).addEvent('complete', function(resp){
				if (resp) new Element('span', {'html': resp.toInt() + ' <strong>Like this</strong>', 'class': btn.className}).replaces(btn);
			}).send();
		});
	}
});

var MetaHover = new Class({

	Implements: Events,

	initialize: function(wrapper){
		this.wrapper = $(wrapper);
		if (!this.wrapper) return;
		this.hover = this.wrapper.getElement('div.meta-hover').set('opacity', 0);
		this.btn = this.wrapper.getElement('.meta').addEvent('click', this.toggle.bind(this));
		this.input = this.hover.getElement('input').addEvent('focus', function(e){
			e.target.select();
		});
		this.wrapper.addEvent('mouseleave', this.hide.bind(this));
		this.hover.addEvent('mouseleave', this.hide.bind(this));
	},

	toggle: function(){
		this.hover.setStyle('display', 'block').fade('toggle');
		this.fireEvent('toggle');
	},

	hide: function(){
		this.hover.fade('out');
	}
});

var ShareHover = new Class({

	Extends: MetaHover,

	initialize: function(wrapper){
		this.parent(wrapper);
		this.hover.getElements('a').addEvent('click', function(e){
			if (/^mailto:/.test(e.target.href)) return true;
			window.open(e.target.href);
			return false;
		});
	}

});

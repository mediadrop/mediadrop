var roundBoxes = function(){
	$$('div.box').each(function(el){
		var round = new Element('div', {'class': 'box-round'})
			.wraps(el)
			.grab(new Element('div', {'class': 'box-round-top-lft'}))
			.grab(new Element('div', {'class': 'box-round-top-rgt'}))
			.grab(new Element('div', {'class': 'box-round-bot-lft'}))
			.grab(new Element('div', {'class': 'box-round-bot-rgt'}));
	});
};
window.addEvent('domready', roundBoxes);


var QuickSearch = new Class({
	Extends: Options,

	options: {
		label: 'SEARCH...',
		field: 'quicksearch-query'
	},

	field: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.field = $(this.options.field);
		this.field.addEvent('change', this.refreshLabel.bind(this));
		this.field.addEvent('blur', this.refreshLabel.bind(this));
		this.field.addEvent('focus', this.removeLabel.bind(this));
		this.refreshLabel();
	},

	removeLabel: function(){
		if (this.field.get('value') == this.options.label) {
			this.field.set('value', '');
		}
	},

	refreshLabel: function(){
		if (!this.field.get('value')) {
			this.field.set('value', this.options.label);
		}
	}
});
window.addEvent('domready', function(){ 
	if ($(QuickSearch.prototype.options.field)) { new QuickSearch(); }
});

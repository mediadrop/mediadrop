var ThumbRater = new Class({
	Extends: Options,

	options: {
		upButton: null,
		upCounter: null,
		downButton: null,
		downCounter: null,
		ensureVisible: null // perhaps some parent object you want hidden until a rating occurs
	},

	upButton: null,
	upCounter: null,
	downButton: null,
	downCounter: null,
	ensureVisible: null,

	initialize: function(options) {
		this.setOptions(options);

		this.upButton = $(this.options.upButton);
		this.upCounter = $(this.options.upCounter);
		this.downButton = $(this.options.downButton);
		this.downCounter = $(this.options.downCounter);
		this.ensureVisible = $(this.options.ensureVisible);

		if (this.upButton) this.upButton.addEvent('click', this.rateUp.bind(this));
		if (this.downButton) this.downButton.addEvent('click', this.rateDown.bind(this));
	},

	rateUp: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.upButton.get('href'));
		this.upButton.set('href', '#').removeEvents('click');
		return this;
	},

	rateDown: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.downButton.get('href'));
		this.downButton.set('href', '#').removeEvents('click');
		return this;
	},

	_rate: function(url) {
		var r = new Request.JSON({
			url: url,
			onComplete: this.rated.bind(this)
		}).send();
	},

	rated: function(responseJSON) {
		if (!responseJSON.success) return;
		this.upCounter.set('text', responseJSON.upRating);
		if (this.downCounter && responseJSON.downRating != undefined) {
			this.downCounter.set('text', responseJSON.downRating);
		}
		if (this.ensureVisible) this.ensureVisible.setStyle('visibility', 'visible');
	}
});

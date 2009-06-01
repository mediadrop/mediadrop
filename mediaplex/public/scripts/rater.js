var ThumbRater = new Class({
	Extends: Options,

	options: {
		upButton: null,
		upCounter: null,
		downButton: null,
		downCounter: null,
	},

	upButton: null,
	upCounter: null,

	initialize: function(options) {
		this.setOptions(options);

		this.upButton = $(this.options.upButton);
		this.upCounter = $(this.options.upCounter);
		this.downButton = $(this.options.downButton);
		this.downCounter = $(this.options.downCounter);

		if (this.upButton) this.upButton.addEvent('click', this.rateUp.bind(this));
		if (this.downButton) this.downButton.addEvent('click', this.rateDown.bind(this));
	},

	rateUp: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.upButton.get('href'));
		this.upButton.set('href', '#').removeEvents('click');
	},

	rateDown: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.downButton.get('href'));
		this.downButton.set('href', '#').removeEvents('click');
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
		if (responseJSON.downRating != undefined) {
			this.downCounter.set('text', responseJSON.downRating);
		}
	}
});

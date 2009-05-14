var ThumbRater = new Class({
	element: null,
	rating: null,
	up: null,
	down: null,

	initialize: function(element, id) {
		this.element = $(element);

		this.rating = this._getRating();
		this.up = this.element.getElement('a.up');
		this.down = this.element.getElement('a.down');
		console.log(this.rating, this.up, this.down)

		this.up.addEvent('click', this.rateUp.bind(this));
		this.down.addEvent('click', this.rateDown.bind(this));
		console.log('wat');
	},

	rateUp: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.up.get('href'));
	},

	rateDown: function(e) {
		if (e != undefined) new Event(e).stop();
		this._rate(this.down.get('href'));
	},

	_rate: function(url) {
		/* TODO: Remove click event so they can't re-vote */

		console.log('Saving users rating of ' + (url[url.length-1]=='1' ? 'thumbs up' : 'thumbs down'));
		console.log(url);

		var r = new Request.JSON({
			url: url,
			onComplete: this.rated.bind(this)
		}).send();
	},

	rated: function(responseJSON) {
		if (responseJSON.success) {
			this.element.getFirst().set('text', responseJSON.rating);
		}
		console.log(responseJSON);
	},

	_getRating: function() {
		return this.element.getFirst().get('text');
	},
});

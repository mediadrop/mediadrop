var FiveStarRater = new Class({
	element: null,
	elementCoords: null,

	rating: null,
	displayedRating: null,

	_boundUpdateHoverFunc: null,

	initialize: function(element) {
		this.element = $(element);

		this.rating = this.displayedRating = this._getRating();

		this._boundUpdateHoverFunc = this.updateHover.bind(this);

		this.element.addEvent('click', this.rate.bind(this))
		            .addEvent('mouseenter', this.startHover.bind(this))
		            .addEvent('mouseleave', this.resetHover.bind(this));
	},

	startHover: function(e) {
		if (!this.elementCoords) { this.elementCoords = this.element.getCoordinates(); }
		this.updateHover(e);
		this.element.addEvent('mousemove', this._boundUpdateHoverFunc);
	},

	updateHover: function(e) {
		e = new Event(e);

		var offset = e.page.x - this.elementCoords.left;
		var percent = offset / this.elementCoords.width;
		var rating = Math.ceil(percent * 5);

		if (rating != this.displayedRating) {
			this.element.addClass(this._getRatingClass(rating))
			            .removeClass(this._getRatingClass(this.displayedRating));
			this.displayedRating = rating;
		}
	},

	resetHover: function(e) {
		this.element.removeEvent(this._boundUpdateHoverFunc);

		if (this.rating != this.displayedRating) {
			this.element.addClass(this._getRatingClass(this.rating))
			            .removeClass(this._getRatingClass(this.displayedRating));
			this.displayedRating = this.rating;
		}
	},

	rate: function(e) {
		new Event(e).stop();
		console.log('Saving users rating of ' + this.displayedRating);

		var postData = new Hash({
			rating: this.displayedRating,
			/* TODO: Copy django.contrib.comments comment-post-form techniques */
			app: null,
			model: null,
			object_id: null,
			security_hash: null
		});

		var r = new Request.JSON({
			url: '/ratings/rate/',
			onComplete: this.rated.bind(this)
		}).send(postData.toQueryString());
		/* TODO: Remove click event so they can't re-vote */
	},

	rated: function(responseJSON) {
		console.log(responseJSON);
	},

	_getRating: function() {
		return this.element.getFirst().get('text');
	},
	_getRatingClass: function(rating) {
		return 'rating-' + rating * 10;
	}
});

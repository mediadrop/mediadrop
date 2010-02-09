/**
 * This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
 *
 * MediaCore is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * MediaCore is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
// FIXME: UPDATE NAMING
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
		var href = this.upButton.getAttributeNode('href');
		this._rate(href.nodeValue);
		this.upButton.removeAttributeNode(href);
		this.upButton.removeEvents('click');
		return this;
	},

	rateDown: function(e) {
		if (e != undefined) new Event(e).stop();
		var href = this.downButton.getAttributeNode('href');
		this._rate(href.nodeValue);
		this.downButton.removeAttributeNode(href);
		this.downButton.removeEvents('click');
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

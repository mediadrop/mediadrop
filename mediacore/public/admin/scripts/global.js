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
window.addEvent('domready', function() {
	if (Browser.Engine.gecko) {
		$$('form').each(function(form) {
			// FIXME: This is totally not standards compliant.
			// I have chosen to put it in the javascript to at least
			// allow the javascript-free version to be XHTML compliant.
			// This must be the first domready event fired.

			// This is here to avoid a firefox bug with dynamically modified forms
			// when multiple form elements have the same name attribute.
			// It is related to the bug described here:
			// http://drupal.org/node/344445
			form.setAttribute('autocomplete', 'off');
		});
	}
});

// Round the corners of all boxes by wrapping it in another div
var roundBoxes = function(){
	$$('.box').each(function(el){
		var skippable = ['for-sbox', 'fitted-sbox'];
		for (var i in skippable) if (el.hasClass(skippable[i])) return;

		var round = new Element('div', {'class': 'box-round'})
			.wraps(el)
			.grab(new Element('div', {'class': 'box-round-top-lft'}))
			.grab(new Element('div', {'class': 'box-round-top-rgt'}))
			.grab(new Element('div', {'class': 'box-round-bot-lft'}))
			.grab(new Element('div', {'class': 'box-round-bot-rgt'}));
	});
};
window.addEvent('domready', roundBoxes);


// Search box label handler
var QuickSearch = new Class({
	Extends: Options,

	options: {
		field: 'search'
	},

	initialize: function(opts){
		this.setOptions(opts);
		new QSOverText($(this.options.field), {
			poll: true,
			pollInterval: 400
		});
	}
});

var QSOverText = new Class({
	Extends: OverText,
	
	getLabelElement: function() {
		var els = $$('label[for='+this.element.id+']');
		if (els.length > 0) {
			return els[0];
		} else {
			return undefined;
		}
	},

	attach: function() {
		this.text = this.getLabelElement();
		if ($defined(this.text)) {
			// Element exists!
			this.text.addEvent('click', this.hide.pass(true, this))
			this.element.addEvents({
				focus: this.focus,
				blur: this.assert,
				change: this.assert
			}).store('OverTextDiv', this.text);
			window.addEvent('resize', this.reposition.bind(this));
			/* Sometimes there's a race condition that prevents the
			 * elements from getting displayed correctly (they're positioned
			 * too far up the page). This should reset them after 1 second. */
			this.assert.delay(1000, this);
			this.reposition.delay(1300, this);
		} else {
			// label element doesn't exist. fall back to
			// regular OverText behaviour and create one.
			parent();
		}
	}

});

window.addEvent('domready', function(){
	if ($(QuickSearch.prototype.options.field)) { new QuickSearch(); }
});

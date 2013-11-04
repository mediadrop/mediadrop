/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

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
		if (el.hasClass('hidden')) {
			// this box will soon be a modal dialog, and adding rounded corners
			// will just mess up the layout.
			return;
		}
		var round = new Element('div', {'class': 'box-round'})
			.wraps(el)
			.grab(new Element('div', {'class': 'box-round-top-lft'}))
			.grab(new Element('div', {'class': 'box-round-top-rgt'}))
			.grab(new Element('div', {'class': 'box-round-bot-mid'}))
			.grab(new Element('div', {'class': 'box-round-bot-lft'}))
			.grab(new Element('div', {'class': 'box-round-bot-rgt'}));
	});
};
window.addEvent('domready', roundBoxes);

// Make nav buttons hold their active status after clicking -- lets hope no one stops their browser.
window.addEvent('domready', function(){
	$('nav').addEvent('click:relay(a)', function(e, el){
		el.addClass('active');
	});
});

/**
 * Override Hash.toQueryString to make it work the same as Element.toQueryString when possible.
 * IE: {a: [1,2,3]} should be "a=1&a=2&a=3" not "a[0]=1&a[1]=2&a[2]=3"
 */
Class.refactor(Hash, {

	toQueryString: function(base){
		var queryString = [];
		Hash.each(this, function(value, key){
			if (base) key = base + '[' + key + ']';
			var result = [];
			switch ($type(value)) {
				case 'object': result = [Hash.toQueryString(value, key)]; break;
				case 'array':
					var containsComplexTypes = value.some(function(val){ return ['object', 'array'].contains($type(val)); });
					if (containsComplexTypes) {
						var qs = {};
						value.each(function(val, i){
							qs[i] = val;
						});
						result = [Hash.toQueryString(qs, key)];
					} else {
						value.each(function(val){
							if (typeof val != 'undefined') result.push(key + '=' + encodeURIComponent(val));
						});
					}
					break;
				default: result = [key + '=' + encodeURIComponent(value)];
			}
			if (value != undefined) queryString.extend(result);
		});
		return queryString.join('&');
	}

});

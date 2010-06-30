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
var OverTextManager = new Class({
	form: null,
	ots: [],

	initialize: function(form) {
		this.form = $(form);
		this.ots = this.form.getElements('input[type=text], textarea').map(function(el) {
			return new CustomOverText(el, {
				poll: true,
				pollInterval: 400,
				wrap: true
			});
		});
	}
});

var CustomOverText = new Class({
	Extends: OverText,
	
	getLabelElement: function() {
		var els = $$('label[for='+this.element.id+']');
		if (els.length > 0) {
			return els[0];
		} else {
			return undefined;
		}
	},

	modifyForm: function() {
		var oldParent = $(this.text.parentNode);
		var newParent = $(this.element.parentNode);
		oldParent.removeChild(this.text);
		this.text.inject(this.element, 'after');
		oldParent.destroy();
		newParent.removeClass('form-field');
		newParent.addClass('form-field-wide');
	},

	attach: function() {
		this.text = this.getLabelElement();
		if ($defined(this.text)) {
			// Element exists!
			this.modifyForm();
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
			this.parent();
		}
	}
});

var displayCommentFlashMsg = function(){
	var flashMsg = Cookie.read('comment_posted');
	if (flashMsg) {
		var flash = $('comment-flash');
		var json = JSON.decode(flashMsg);
		var content = new Element('div').inject(flash.getElement('.comment-content'));
		if (json.title) content.grab(new Element('strong', {text: json.title}));
		if (json.success != undefined) content.addClass(json.success ? 'success' : 'error');
		content.appendText(' ' + json.text);
		flash.show();
		Cookie.dispose('comment_posted', {path: '/'});
	}
};

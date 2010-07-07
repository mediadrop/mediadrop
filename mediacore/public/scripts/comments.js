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

	initialize: function(form) {
		this.form = $(form);
		this.ots = this.form.getElements('input[type=text], textarea').map(function(el){
			return new CustomOverText(el);
		});
	}

});

var CustomOverText = new Class({

	Extends: OverText,

	getLabelElement: function(){
		var form = this.element.getParent('form');
		return (form ? form.getElement('label[for='+this.element.id+']') : null);
	},

	modifyForm: function(){
		var labelDiv = this.text.getParent();
		var fieldDiv = this.element.getParent();
		fieldDiv.adopt(this.text).removeClass('form-field').addClass('form-field-wide');
		labelDiv.destroy();
		return this;
	},

	attach: function(){
		this.text = this.getLabelElement();
		if (!this.text) return this.parent(); // label element doesn't exist. fall back to regular OverText behaviour and create one.
		this.modifyForm();
		this.text.addEvent('click', this.hide.pass(true));
		this.element.addEvents({
			focus: this.focus,
			blur: this.assert,
			change: this.assert
		}).store('OverTextDiv', this.text);
		window.addEvent('resize', this.reposition);
		this.assert(true);
		return this.reposition();
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

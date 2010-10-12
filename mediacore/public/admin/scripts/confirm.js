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
/**
 * Confirm Dialogue Script
 *
 * @requires   mootools-1.2-core.js
 * @requires   squeezebox.js
 *
 * @author     Mel Wright <mel@simplestation.com>
 * @version    $Id$
 * @copyright  Copyright (c) 2009, Simple Station Inc.
 */
var ConfirmMgr = new Class({

	Implements: [Options, Events],

	options:{
		cancelButtonText: 'No',
		confirmButtonText: 'Yes',
		confirmButtonClass: 'btn red f-rgt',
		cancelButtonClass: 'btn f-rgt',
		header: 'Confirm',
		msg: 'Are you sure?',
		overlayOpacity: 0.4,
		focus: 'confirm'
		//onConfirm: $empty (e.target)
	},

	initialize: function(opts){
		this.setOptions(opts);
	},

	openConfirmDialog: function(e){
		e = new Event(e).stop();
		var target = $(e.target);

		// Set up the dialog box
		var header = $type(this.options.header) == 'function' ? this.options.header(target) :this.options.header;
		var msg = $type(this.options.msg) == 'function' ? this.options.msg(target) : this.options.msg;

		var box = new Element('div', {'class': 'box'});
		var head = new Element('h1', {'class': 'box-head', html: header}).inject(box);
		var text = new Element('p', {'class': 'box-content', html: msg}).inject(box);
		var buttons = new Element('div', {'class': 'box-foot'}).inject(box);
		var confirmButton = new Element('button', {'class': this.options.confirmButtonClass, html: '<span>' + this.options.confirmButtonText + '</span>'}).inject(buttons);
		var cancelButton = new Element('button', {'class': this.options.cancelButtonClass, html: '<span>' + this.options.cancelButtonText + '</span>'}).inject(buttons);

		cancelButton.addEvent('click', this.cancel.pass(target, this));
		confirmButton.addEvent('click', this.confirm.pass(target, this));

		SqueezeBox.fromElement(box, {
			size: {x: 630, y: 400},
			handler: 'fittedAdopt',
			overlayOpacity: this.options.overlayOpacity,
			onOpen: function(){
				// FIXME: This event fires before the content is actually displayed.
				//        Content is displayed by SqueezeBox.applyContent w/ a timer,
				//        so we do our best to match that delay and hope that the user
				//        isn't super quick at hitting enter.
				switch (this.options.focus) {
					case 'cancel':
						cancelButton.focus.delay(SqueezeBox.presets.overlayFx.duration || 250, cancelButton);
						break;
					case 'confirm':
						confirmButton.focus.delay(SqueezeBox.presets.overlayFx.duration || 250, confirmButton);
						break;
				}
			}.bind(this)
		});
	},

	cancel: function(target){
		SqueezeBox.close();
	},

	confirm: function(target){
		SqueezeBox.close();
		this.fireEvent('onConfirm', [target]);
	}

});

var DeleteConfirmMgr = new Class({

	Extends: ConfirmMgr,

	options: {
		header: 'Confirm Delete',
		msg: 'Are you sure you want to delete this?',
		confirmButtonText: 'Delete',
		confirmButtonClass: 'btn red f-rgt',
		cancelButtonText: 'Cancel',
		cancelButtonClass: 'btn f-rgt',
		focus: 'cancel'
	},

	initialize: function(opts){
		this.parent(opts);
		this.addEvent('confirm', this.submitForm.bind(this));
	},

	submitForm: function(target){
		var form = target.getParent('form');
		form.set('action', form.get('action') + '?delete=1');
		form.submit();
	}

});

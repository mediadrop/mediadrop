/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * Confirm Dialogue Script
 *
 * @requires   mootools-1.2-core.js
 * @requires   squeezebox.js
 *
 * @author     Mel Wright <mel@mediacore.com>
 * @version    $Id$
 */
var ConfirmMgr = new Class({

	Implements: [Options, Events],

	options:{
		cancelButtonText: 'No',
		confirmButtonText: 'Yes',
		confirmButtonClass: 'btn red f-rgt',
		cancelButtonClass: 'btn f-lft',
		header: 'Confirm',
		msg: 'Are you sure?',
		overlayOpacity: 0.4,
		wrapParagraph: true,
		focus: 'confirm'
		//onConfirm: $empty (e.target)
	},

	initialize: function(opts){
		this.setOptions(opts);
	},

	openConfirmDialog: function(e){
		if ($type(e) == 'event') {
			e = new Event(e).stop();
			var target = $(e.target);
		} else {
			var target = e;
		}

		// Set up the dialog box
		var header = $type(this.options.header) == 'function' ? this.options.header(target) :this.options.header;
		var msg = $type(this.options.msg) == 'function' ? this.options.msg(target) : this.options.msg;
		if (this.options.wrapParagraph) {
			msg = '<p>' + msg + '</p>';
		}

		var box = new Element('div', {'class': 'box'});
		var head = new Element('h1', {'class': 'box-head', html: header}).inject(box);
		var text = new Element('div', {'class': 'box-content', html: msg}).inject(box);
		var buttons = new Element('div', {'class': 'box-foot'}).inject(box);
		var cancelButton = new Element('button', {'class': this.options.cancelButtonClass, html: '<span>' + this.options.cancelButtonText + '</span>'}).inject(buttons);
		var confirmButton = new Element('button', {'class': this.options.confirmButtonClass, html: '<span>' + this.options.confirmButtonText + '</span>'}).inject(buttons);

		cancelButton.addEvent('click', this.cancel.pass(target, this));
		confirmButton.addEvent('click', this.confirm.pass(target, this));

		this.openDialogHook(target, box, head, text, buttons, cancelButton, confirmButton)

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

	openDialogHook: function(box, head, text, buttons, cancelButton, confirmButton) {
		// Only implemented in subclasses.
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
		cancelButtonClass: 'btn f-lft',
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

var ResetConfirmMgr = new Class({

	Extends: ConfirmMgr,

	options: {
		header: 'Confirm Reset',
		msg: 'Are you sure you want to reset your settings to the default?',
		confirmButtonText: 'Reset',
		confirmButtonClass: 'btn red f-rgt',
		cancelButtonText: 'Cancel',
		cancelButtonClass: 'btn f-lft',
		focus: 'cancel'
	},

	initialize: function(opts){
		this.parent(opts);
		this.addEvent('confirm', this.submitForm.bind(this));
	},

	submitForm: function(target){
		var form = target.getParent('form');
		form.set('action', form.get('action') + '?reset=1');
		form.submit();
	}

});

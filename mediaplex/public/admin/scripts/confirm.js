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
		cancelButtonText: 'no',
		confirmButtonText: 'yes',
		confirmButtonClass: 'mo submitbutton btn-yes f-rgt',
		cancelButtonClass: 'mo submitbutton btn-no f-rgt',
		header: 'Confirm',
		msg: 'Are you sure?',
		overlayOpacity: 0.4
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
		var text = new Element('p', {html: msg}).inject(box);
		var buttons = new Element('div', {'class': 'box-foot'}).inject(box);
		var confirmButton = new Element('button', {'class':this.options.confirmButtonClass, html: this.options.confirmButtonText}).inject(buttons);
		var cancelButton = new Element('button', {'class': this.options.cancelButtonClass, html: this.options.cancelButtonText}).inject(buttons);

		cancelButton.addEvent('click', this.cancel.pass(target, this));
		confirmButton.addEvent('click', this.confirm.pass(target, this));

		SqueezeBox.fromElement(box, {handler: 'fittedAdopt', overlayOpacity: this.options.overlayOpacity});

		confirmButton.focus();
	},

	cancel: function(target){
		SqueezeBox.close();
	},

	confirm: function(target){
		SqueezeBox.close();
		this.fireEvent('onConfirm', [target]);
	},

});



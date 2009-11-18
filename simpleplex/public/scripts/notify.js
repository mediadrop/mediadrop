/**
 * Notification Script
 *
 * @requires   mootools-1.2-core.js
 * @requires   squeezebox.js
 *
 * @author     Mel Wright <mel@simplestation.com>
 * @version    $Id$
 * @copyright  Copyright (c) 2009, Simple Station Inc.
 */
var NotificationManager = new Class({

	Implements: [Options, Events],

	options:{
		notifyWidgetSelector: 'notifier',
		notifyOnEvent: 'click',
		header: 'Notify',
		headerClass: '',
		msg: '',
		divClass: '',
		footerClass: '',
		okButtonClass: '',
		okButtonText: 'OK',
		overlayOpacity: 0.4
		//onClose: $empty (e.target)
	},

	msg: null,

	initialize: function(opts){
		this.setOptions(opts);

		if(this.options.notifyOnEvent == null || this.options.notifyWidgetSelector == null)
			return;

		$$(this.options.notifyWidgetSelector).each(function(widget){
			widget.addEvent(this.options.notifyOnEvent, this.openNotify.bind(this));
		}.bind(this));
	},

	openNotify: function(e){
		var target = e == null ? null : $(e.target);

		// Set up the dialog box
		var header = $type(this.options.header) == 'function' ? this.options.header(target) :this.options.header;
		var msg = $type(this.options.msg) == 'function' ? this.options.msg(target) : this.options.msg;

		var box = new Element('div', {'class': this.options.divClass});
		var head = new Element('h1', {'class': this.options.headerClass, html: header}).inject(box);
		var text = new Element('p', {html: msg}).inject(box);
		var buttons = new Element('div', {'class': this.options.footerClass}).inject(box);
		var okButton = new Element('button', {'class':this.options.okButtonClass, html: this.options.okButtonText}).inject(buttons);

		okButton.addEvent('click', this.closeNotify.pass(target, this));

		SqueezeBox.fromElement(box, {
			handler: 'fittedAdopt',
			overlayOpacity: this.options.overlayOpacity,
			onOpen: function(){
				// FIXME: This event fires before the content is actually displayed.
				//        Content is displayed by SqueezeBox.applyContent w/ a timer,
				//        so we do our best to match that delay and hope that the user
				//        isn't super quick at hitting enter.
				okButton.focus.delay(SqueezeBox.presets.overlayFx.duration || 250, okButton);
			}
		});
		return true;
	},

	closeNotify: function(target){
		SqueezeBox.close();
		this.fireEvent('onClose', [target]);
	}
});

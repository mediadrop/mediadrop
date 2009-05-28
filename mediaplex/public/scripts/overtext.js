var OverTextManager = new Class({
	form: null,
	ots: [],

	initialize: function(form) {
		this.form = $(form);
		this.ots = this.form.getElements('input[type=text], textarea').map(function(el) {
			return new CustomOverText(el, {
				poll: true,
				pollInterval: 400
			});
		});
	},
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
		console.log(this.text, this.text.parentNode);
		var oldParent = this.text.parentNode;
		oldParent.removeChild(this.text);
		this.text.inject(this.element, 'after');
		oldParent.destroy();
		console.log(this.element.getStyle('margin'), this.element.getStyle('padding'));
		this.element.parentNode.removeClass('form-field');
		this.element.parentNode.addClass('form-field-wide');
		console.log(this.text, this.text.parentNode);
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
		} else {
			// label element doesn't exist. fall back to
			// regular OverText behaviour and create one.
			parent();
		}
	}

});

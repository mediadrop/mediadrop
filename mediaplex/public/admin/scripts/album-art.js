SqueezeBox.handlers.extend({
	clone: function(el) {
		if (el) return el.clone().setStyle('display', 'block');
		return this.onError();
	},

	fittedClone: function(el) {
		el = this.handlers.clone(el);
		var origY = this.options.size.y;
		this.setOptions({
			size: {y: el.getSize().h}, // set this contents height to be the new default
			onClose: function(e, origY){
				// reset the default height to the original setting & unset this event
				this.setOptions({size: {y: origY}, onClose: $empty});
			}.bindWithEvent(this, [origY])
		});
		return el;
	},
});


window.addEvent('domready', function(){
	var button = $('edit-album-art').addEvent('click', function(){
		SqueezeBox.fromElement($('album-art-box'), {
			handler: 'fittedClone'
		});
	});

/*$('album-art-wrapper').getParent('form').addEvent('submit', function(){
		
	});*/
});

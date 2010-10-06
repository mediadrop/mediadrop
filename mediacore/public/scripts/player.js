Element.NativeEvents.error = 2;

var MediaPlayer = new Class({

	Implements: Options,

	Binds: ['showFlash', 'onError'],

	options: {
		errorText: 'Your browser is incapable of playing this media.',
		swiff: null,
		preferFlash: false
	},

	initialize: function(element, opts){
		this.element = $(element);
		this.setOptions(opts);
		this.detect();
	},

	detect: function(){
		// detect html5 support
		this.html5 = this.element.getElement('audio, video');
		if (this.html5 && !this.html5.canPlayType) {
			this.html5 = this.options.preferFlash = null;
		}

		// just display flash if preferred and the client supports it
		if (this.options.preferFlash && this.showFlash()) return;

		// if any html5 sources are worth trying to play, listen for failure
		if (this.html5 && this.attachFallback()) return;

		this.showFlash() || this.showError();
	},

	attachFallback: function(){
		var sources = [], html5 = this.html5;
		html5.getElements('source').each(function(el){
			if (el.type && !html5.canPlayType(el.type)) return el.destroy();
			sources.push(el);
		});
		if (!sources.length) return false;
		this.html5LastSrc = sources[sources.length - 1].src;
		html5.addEvent('error', this.onError);
		return true;
	},

	onError: function(){
		if (this.html5.currentSrc.match(this.html5LastSrc)) this.showFlash() || this.showError();
	},

	showFlash: function(){
		if (Browser.Plugins.Flash.version && this.options.swiff) {
			var el = $(this.options.swiff);
			this.element.empty().grab(el);
			return true;
		}
		return false;
	},

	showError: function(){
		this.element.empty().set('text', this.options.errorText);
	},

	toElement: function(){
		return this.element;
	}

});

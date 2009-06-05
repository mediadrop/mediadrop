/**
 * Slider that operates on the elements of a container one after another.
 *
 * Each element can have different Fx.Slide options which can also change
 * depending on whether the slider is opening (sliding 'in' to view) or
 * closing (sliding 'out' of view).
 *
 * @author Nathan Wright
 */
var ButtonFlyout = new Class({

	Implements: [Options, Chain],

	options: {
		button: '',
		buttonActiveClass: '',
		elements: '', // elements that slide out
		startHidden: true,
		fx: {}, // defaults overridden by openFx & closeFx
		openFx: [], // on open fx options per element
		closeFx: [] // on close fx options per element
	},

	button: null,
	elements: null,
	fx: [],
	open: true,

	initialize: function(opts){
		this.setOptions(opts);
		this.elements = $$(this.options.elements);
		for (var i = this.elements.length; i--; i) {
			this.fx[i] = this.elements[i].get('slide', this.options.closeFx[i] || this.options.fx)
				.addEvent('complete', this.callChain.bind(this));
		}
		this.button = $(this.options.button).addEvent('click', this.toggle.bind(this));
		if (this.options.startHidden) this.hide();
	},

	/** Slide 'in' or 'out' of view */
	slide: function(how){
		this.clearChain();
		if (how == 'in') {
			for (var i = 0; i < this.fx.length; i++) this.chain(this._startFx.bind(this, [i, how]));
			this._setOpen(true);
		} else {
			for (var i = this.fx.length; i--; i) this.chain(this._startFx.bind(this, [i, how]));
			this.chain(this._setOpen.bind(this, [false, true]));
		}
		this.chain(this._swapFxOptions.bind(this))
		    .callChain();
		return this;
	},

	toggle: function(e){
		if (e != undefined) new Event(e).preventDefault();
		if (this.open) return this.slide('out');
		else return this.slide('in');
	},

	show: function(e){
		if (e != undefined) new Event(e).preventDefault();
		return this._showHide('show');
	},

	hide: function(e){
		if (e != undefined) new Event(e).preventDefault();
		return this._showHide('hide');
	},

	_showHide: function(how){
		this.clearChain();
		for (var i = this.fx.length; i--; i) this.fx[i][how]();
		return this._setOpen(how == 'show')
		           ._swapFxOptions();
	},

	_setOpen: function(flag, callChain){
		this.open = !!flag;
		if (this.open) {
			this.button.addClass(this.options.buttonActiveClass);
		} else {
			this.button.removeClass(this.options.buttonActiveClass);
		}
		if (callChain) this.callChain();
		return this;
	},

	_startFx: function(i, mode){
		var thisFx = this.fx[i];
		thisFx.start.run(mode, thisFx);
	},

	_swapFxOptions: function(){
		var opts = this.open ? this.options.closeFx : this.options.openFx;
		for (var i = this.fx.length; i--; i) this.fx[i].setOptions(opts[i] || this.options.fx);
		return this;
	}
});

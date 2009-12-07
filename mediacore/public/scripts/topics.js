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
 * Slider that operates on the elements of a container one after another.
 *
 * Each element can have different Fx.Slide options which can also change
 * depending on whether the slider is opening (sliding 'in' to view) or
 * closing (sliding 'out' of view).
 *
 * @author Nathan Wright
 */
var ButtonFlyout = new Class({

	Implements: [Options, Chain, Events],

	options: {
		button: '',
		buttonActiveClass: '',
		elements: '', // elements that slide out
		startHidden: true,
		fx: {}, // defaults overridden by openFx & closeFx
		openFx: [], // on open fx options per element
		closeFx: [] // on close fx options per element,
	/*	onStart: $empty,
		onComplete: $empty ,
		onOpen: $empty,
		onClose: $empty*/
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
		this.clearChain()
		    .fireEvent('start', [how, this]);
		if (how == 'in') {
			for (var i = 0; i < this.fx.length; i++) this.chain(this._startFx.bind(this, [i, how]));
			this._setOpen(true);
		} else {
			for (var i = this.fx.length; i--; i) this.chain(this._startFx.bind(this, [i, how]));
			this.chain(this._setOpen.bind(this, [false, true]));
		}
		this.chain(this._swapFxOptions.bind(this, [true]))
		    .chain(this.fireEvent.bind(this, ['complete', how, this]))
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
			this.fireEvent('open', [this]);
		} else {
			this.button.removeClass(this.options.buttonActiveClass);
			this.fireEvent('close', [this]);
		}
		if (callChain) this.callChain();
		return this;
	},

	_startFx: function(i, mode){
		var thisFx = this.fx[i];
		thisFx.start.run(mode, thisFx);
	},

	_swapFxOptions: function(callChain){
		var opts = this.open ? this.options.closeFx : this.options.openFx;
		for (var i = this.fx.length; i--; i) this.fx[i].setOptions(opts[i] || this.options.fx);
		if (callChain) this.callChain();
		return this;
	}
});

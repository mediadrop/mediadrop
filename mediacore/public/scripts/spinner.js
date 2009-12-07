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
var Spinner = new Class({
	Implements: [Events, Options],

	options: {
		tag: 'span',
		startClass: 'spinner',
		startMsg: 'Processing...',
		stopClass: 'success',
		stopMsg: 'Action successful',
		errorClass: 'error',
		errorMsg: 'Unexpected error occurred',
		request: null
	},

	el: null,

	initialize: function(opts){
		if (opts) { this.setOptions(opts); }
		if (this.options.request) {
			this.options.request.addEvents({
				request: this.start.bind(this),
				success: this.stop.bind(this),
				error: this.error.bind(this)
			});
			this.el = this.createElement();
		} else {
			this.start();
		}
	},

	createElement: function(){
		return new Element(this.options.tag);
	},

	updateElement: function(msg, klass){
		if (!this.el) { this.el = this.createElement(); }
		this.el.set('text', msg).set('class', klass);
		return this;
	},

	start: function(e){
		this.updateElement(this.options.startClass, this.options.startMsg);
		this.fireEvent('start');
		return this;
	},

	stop: function(e){
		this.updateElement(this.options.stopClass, this.options.stopMsg);
		this.fireEvent('stop');
		return this;
	},

	error: function(e){
		this.updateElement(this.options.errorClass, this.options.errorMsg);
		this.fireEvent('fail');
		return this;
	}
});








/*
var Spinner = function(className, parent, startMessage, stopMessage, errorMessage) {
	this._class = className;
	this._parent = parent;
	this._defaultStartMessage = startMessage;
	this._defaultStopMessage  = stopMessage;
	this._defaultErrorMessage = errorMessage;
}

Spinner.prototype = {
	_spinnerSpan: {},

	_fadeOut: function(instance, spanID) {
		// uses 'instance' instead of 'this' because scope is lost when using as a callback
		var a = new YAHOO.util.Anim(
			instance._spinnerSpan[spanID],
			{opacity: {to: 0}},
			.75, YAHOO.util.Easing.easeIn
		);
		
		a.onComplete.subscribe(function() {
			instance._parent.removeChild(instance._spinnerSpan[spanID]); // remove the spinner element
			delete(instance._spinnerSpan[spanID]);
		});
		a.animate(); // fade the spinner out
	},

	start: function(spanID, message) {
		this._spinnerSpan[spanID] = document.createElement('span');
		this._spinnerSpan[spanID].className = 'spinner ' + this._class;
		this._spinnerSpan[spanID].innerHTML = this._defaultStartMessage;
		this._parent.appendChild(this._spinnerSpan[spanID]);
	},

	stop: function(spanID, success, message) {
		if (success) {
			this._spinnerSpan[spanID].className = 'success ' + this._class;
			this._spinnerSpan[spanID].innerHTML = message ? message : this._defaultStopMessage;
		} else {
			this._spinnerSpan[spanID].className = 'failure ' + this._class;
			this._spinnerSpan[spanID].innerHTML = message ? message : this._defaultErrorMessage;
		}
		// Set the callback for fade out. Need to assign a new varible to hold 'this' to maintain scope.
		var instance = this;
		setTimeout(function(){instance._fadeOut(instance, spanID)}, 2000);
	}
}
*/

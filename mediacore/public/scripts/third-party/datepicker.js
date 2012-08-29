/*
---

name: Datepicker

description: MooTools Datepicker class

authors:
  - MonkeyPhysics.com
  - Arian Stolwijk
  - MadmanMonty (Chris Baxter)
  - marfillaster (Ken Marfilla)
  - eerne (Enrique Erne)

license:
  - MIT License

requires:
  - Core/Class.Extras
  - Core/Browser
  - Core/Element.Event
  - Core/Element.Style
  - Core/Element.Dimensions
  - Core/Fx.Tween
  - More/Date
  - More/MooTools.lang

provides: [DatePicker]

...
*/


/**
 * datepicker.js - MooTools Datepicker class
 *
 * by MonkeyPhysics.com
 *
 * Source/Documentation available at:
 * http://www.monkeyphysics.com/mootools/script/2/datepicker
 *
 * --
 *
 * Smoothly animating, very configurable and easy to install.
 * No Ajax, pure Javascript. 4 skins available out of the box.
 *
 * --
 *
 * MIT License
 *
 */

var DatePicker = new Class({

	Implements: [Options, Events],

	// working date, which we will keep modifying to render the calendars
	/*d: null,*/

	// just so that we need not request it over and over
	today: '',

	// current user-choice in date object format
	choice: {},

	// size of body, used to animate the sliding
	bodysize: {},

	// to check availability of next/previous buttons
	limit: {},

	// element references:
	/*picker: null,      // main datepicker container
	slider: null,      // slider that contains both oldContents and newContents, used to animate between 2 different views
	oldContents: null, // used in animating from-view to new-view
	newContents: null, // used in animating from-view to new-view
	input: null,*/       // original input element (used for input/output)

	options: {
		pickerClass: 'datepicker',
		dayShort: 2,
		monthShort: 3,
		startDay: 1, // Sunday (0) through Saturday (6) - be aware that this may affect your layout, since the days on the right might have a different margin
		timePicker: false,
		timePickerOnly: false,
		yearPicker: true,
		yearsPerPage: 20,
		allowEmpty: true,
		animationDuration: 400,
		useFadeInOut: !Browser.Engine.trident, // dont animate fade-in/fade-out for IE
		startView: 'month', // allowed values: {time, month, year, decades}
		positionOffset: {x: 0, y: 0},
		/*minDate: null, // Date object or a string
		maxDate: null, // same as minDate
		toggleElements: null, // deprecated
		toggle: null,*/
		draggable: true,
		timeWheelStep: 1 // 10,15,20,30
		/*,

		// i18n
		months: null,
		days: null,
		format: null,
		selectTimeTitle: null,
		timeConfirmButton: null,


		// and some event hooks:
		onShow: $empty,   // triggered when the datepicker pops up
		onClose: $empty,  // triggered after the datepicker is closed (destroyed)
		onSelect: $empty,  // triggered when a date is selected
		onNext: $empty,  // triggered when changing to next month
		onPrevious: $empty  // triggered when changing to previous month */
	},

	initialize: function(attachTo, options){
		// Localization
		var localeGet = MooTools.lang.get;
		this.setOptions({
			days: localeGet('Date', 'days'),
			months: localeGet('Date', 'months'),
			format: localeGet('Date', 'shortDate'),
			selectTimeTitle: localeGet('DatePicker', 'select_a_time'),
			timeConfirmButton: localeGet('DatePicker', 'time_confirm_button')
		});

		var defaultFormat = this.options.format;
		this.setOptions(options);
		if (this.options.timePicker && this.options.format == defaultFormat){
			var timeFormat = localeGet('Date', 'shortTime');
			this.options.format = this.options.timePickerOnly ? timeFormat : this.options.format + ' ' + timeFormat;
		}

		// Support for deprecated toggleElements
		if (this.options.toggleElements) this.options.toggle = document.getElements(this.options.toggleElements);

		this.attach(attachTo, this.options.toggle);

		if (this.options.timePickerOnly){
			this.options.timePicker = true;
			this.options.startView = 'time';
		}

		if (this.options.minDate){
			if (!(this.options.minDate instanceof Date)) this.options.minDate = Date.parse(this.options.minDate);
		}
		if (this.options.maxDate){
			if (!(this.options.maxDate instanceof Date)) this.options.maxDate = Date.parse(this.options.maxDate);
			// Include the maxDate day
			this.options.maxDate.increment('day', 1);
		}

		document.addEvent('mousedown', function(event){
			if (
				!(this.elems && this.elems.contains(event.target)) &&
				this.picker &&
				event.target != this.picker &&
				!this.picker.hasChild(event.target)
			){
				this.close.call(this);
			}
		}.bind(this));
	},

	attach: function(attachTo, toggle){

		//don't bother trying to attach when not set
		if (!attachTo) return this;

		// toggle the datepicker through a separate element?
		if (toggle){
			var togglers = $type(toggle) == 'array' ? toggle : [document.id(toggle)];
			document.addEvent('keydown', function(event){
				var target = document.id(event.target);
				if (
					event.key == 'tab' &&
					!target.hasClass('hour') &&
					!target.hasClass('minutes') &&
					!target.hasClass('ok')
				){
					this.close();
				}
			}.bind(this));
		}

		// see what is being attached and get an array suitable for it
		var elems = this.elems = $type(attachTo) == 'array' ? attachTo : [document.id(attachTo)];

		// attach functionality to the inputs
		elems.each(function(item, index){
			// never double attach
			if (item.retrieve('datepicker')) return;

			item.store('datepicker', true); // to prevent double attachment...

			// events
			if (toggle && togglers){
				var self = this;
				var events = {click: function(e){
					if (e) e.stop();
					self.show(item, togglers[index]);
				}};
				var toggler = togglers[index]
					.setStyle('cursor', 'pointer')
					.addEvents(events);
				item.store('datepicker:toggler', toggler)
					.store('datepicker:events', events);
			} else {
				var events = {
					keydown: function(e){
						// prevent the user from typing in the field
						if (this.options.allowEmpty && (e.key == 'delete' || e.key == 'backspace')){
							item.set('value', '');
							this.close();
						} else if (e.key == 'tab'){
							this.close();
						} else {
							e.stop();
						}
					}.bind(this),
					focus: this.show.pass(item, this),
					click: this.show.pass(item, this)
				};

				item.addEvents(events).store('datepicker:events', events);
			}
		}.bind(this));

		return this;
	},

	detach: function(detach){
		var elems = $type(detach) == 'array' ? detach : [document.id(detach)];

		elems.each(function(item){
			// Only when the datepicker is attached
			if (!item.retrieve('datepicker')) return;
			item.store('datepicker', false);

			var toggler = item.retrieve('datepicker:toggler');
			var events = item.retrieve('datepicker:events');
			// Detach the Events
			(toggler || item).removeEvents(events);
		});

		return this;
	},

	show: function(input, toggler, timestamp){
		input = document.id(input);

		// Cannot show the picker if its not attached
		if (!input.retrieve('datepicker')) return;

		// Determine the date that should be opened
		if (timestamp){
			this.d = new Date(timestamp);
		} else {
			this.d = input.retrieve('datepicker:value') || input.get('value');
			if (!this.d){
				this.d = new Date();
			} else if (!(this.d instanceof Date)){
				this.d = Date.parse(this.d);
			}
		}
		if (!this.d.isValid()) this.d = new Date();

		// Min/max date
		if (this.options.maxDate && this.options.maxDate.isValid() && this.d > this.options.maxDate)
			this.d = this.options.maxDate.clone();
		if (this.options.minDate && this.options.minDate.isValid() && this.d < this.options.minDate)
			this.d = this.options.minDate.clone();

		this.input = input;
		var inputCoords = (document.id(toggler) || input).getCoordinates();
		var position = {
			left: inputCoords.left + this.options.positionOffset.x,
			top: inputCoords.top + inputCoords.height + this.options.positionOffset.y
		};
		var maxTopPosition = (window.innerHeight + window.pageYOffset) - (135+2*14) - 10;
		if (position.top > maxTopPosition)
		    // in case the picker should appear at the end of the page, move it up
		    // otherwise it might happen that the picker is displayed in strange places
		    // e.g. at the top of the page
		    position.top = maxTopPosition;
		this.fireEvent('show');

		this.today = new Date();
		this.choice = this.d.toObject();
		this.mode = (this.options.startView == 'time' && !this.options.timePicker) ? 'month' : this.options.startView;

		this.render();
		this.position({
			x: position.left,
			y: position.top
		});

		if (this.options.draggable && $type(this.picker.makeDraggable) == 'function'){
			this.dragger = this.picker.makeDraggable();
			this.picker.setStyle('cursor', 'move');
		}

		if (Browser.Engine.trident) this.shim();

		return this;
	},

	close: function(){
		if (!document.id(this.picker)) return this;

		if (this.options.useFadeInOut) this.picker.fade(0);
		else this.destroy();

		return this;
	},

	// Protected/Private methods

	shim: function(){
		var coords = this.picker.setStyle('zIndex', 1000).getCoordinates();
		var frame = this.frame = new Element('iframe', {
			src: 'javascript:false;document.write("");',
			styles: {
				position: 'absolute',
				zIndex: 999,
				height: coords.height, width: coords.width,
				left: coords.left, top: coords.top
			}
		}).inject(document.body);
		frame.style.filter = 'progid:DXImageTransform.Microsoft.Alpha(style=0,opacity=0)';

		this.addEvent('close', function(){frame.destroy()});

		if (this.dragger){
			this.dragger.addEvent('drag', function(){
				var coords = this.picker.getCoordinates();
				frame.setStyles({left: coords.left, top: coords.top});
			}.bind(this));
		}
	},

	position: function(position){
		var size = window.getSize(),
			scroll = window.getScroll(),
			pickerSize = this.picker.getSize(),
			max_y = (size.y + scroll.y) - pickerSize.y,
			max_x = (size.x + scroll.x) - pickerSize.x,
			inputCoords = this.input.getCoordinates();

		if (position.x > max_x) position.x = inputCoords.right - this.options.positionOffset.x - pickerSize.x;
		if (position.y > max_y) position.y = inputCoords.top - this.options.positionOffset.y - pickerSize.y;

		this.picker.setStyles({
			left: position.x,
			top: position.y
		});
	},

	render: function(fx){
		if (!this.picker){
			this.constructPicker();
		} else {
			// swap contents so we can fill the newContents again and animate
			var old = this.oldContents;
			this.oldContents = this.newContents;
			this.newContents = old;
			this.newContents.empty();
		}

		// remember current working date
		var startDate = new Date(this.d.getTime());

		// intially assume both left and right are allowed
		this.limit = {right: false, left: false};

		// render! booty!
		if (this.mode == 'decades'){
			this.renderDecades();
		} else if (this.mode == 'year'){
			this.renderYear();
		} else if (this.mode == 'time'){
			this.renderTime();
			this.limit = {right: true, left: true}; // no left/right in timeview
		} else {
			this.renderMonth();
		}

		this.picker.getElement('.previous').setStyle('visibility', this.limit.left ? 'hidden' : 'visible');
		this.picker.getElement('.next').setStyle('visibility', this.limit.right ? 'hidden' : 'visible');
		this.picker.getElement('.titleText').setStyle('cursor', this.allowZoomOut() ? 'pointer' : 'default');

		// restore working date
		this.d = startDate;

		this.picker.fade(1);

		// animate
		if (fx) this.fx(fx);
	},

	fx: function(fx){
		if (fx == 'right'){
			this.oldContents.setStyles({left: 0, opacity: 1});
			this.newContents.setStyles({left: this.bodysize.x, opacity: 1});
			this.slider.setStyle('left', 0).tween('left', 0, -this.bodysize.x);
		} else if (fx == 'left'){
			this.oldContents.setStyles({left: this.bodysize.x, opacity: 1});
			this.newContents.setStyles({left: 0, opacity: 1});
			this.slider.setStyle('left', -this.bodysize.x).tween('left', -this.bodysize.x, 0);
		} else if (fx == 'fade'){
			this.slider.setStyle('left', 0);
			this.oldContents.setStyle('left', 0).set('tween', {duration: this.options.animationDuration / 2}).tween('opacity', 1, 0);
			this.newContents.setStyles({opacity: 0, left: 0}).set('tween', {duration: this.options.animationDuration}).tween('opacity', 0, 1);
		}
	},

	constructPicker: function(){
		this.picker = new Element('div', {
			'class': this.options.pickerClass
		}).inject(document.body);

		if (this.options.useFadeInOut){
			this.picker.setStyle('opacity', 0).set('tween', {
				duration: this.options.animationDuration,
				link: 'cancel',
				onComplete: function(){
					if (this.picker.getStyle('opacity') < 1) this.destroy();
				}.bind(this)
			});
		}

		var h = new Element('div', {'class': 'header'}).inject(this.picker);
		var titlecontainer = new Element('div', {'class': 'title'}).inject(h);
		new Element('div', {'class': 'previous'}).addEvent('click', this.previous.bind(this)).set('text', '«').inject(h);
		new Element('div', {'class': 'next'}).addEvent('click', this.next.bind(this)).set('text', '»').inject(h);
		new Element('div', {'class': 'closeButton'}).addEvent('click', function(event){
			this.close.call(this);
		}.bind(this)).set('text', 'x').inject(h);
		new Element('span', {'class': 'titleText'}).addEvent('click', this.zoomOut.bind(this)).inject(titlecontainer);

		var b = new Element('div', {'class': 'body'}).inject(this.picker);
		this.bodysize = b.getSize();
		this.slider = new Element('div', {styles: {position: 'absolute', top: 0, left: 0, width: 2 * this.bodysize.x, height: this.bodysize.y}})
					.set('tween', {duration: this.options.animationDuration, transition: Fx.Transitions.Quad.easeInOut}).inject(b);
		this.oldContents = new Element('div', {styles: {position: 'absolute', top: 0, left: this.bodysize.x, width: this.bodysize.x, height: this.bodysize.y}}).inject(this.slider);
		this.newContents = new Element('div', {styles: {position: 'absolute', top: 0, left: 0, width: this.bodysize.x, height: this.bodysize.y}}).inject(this.slider);
	},

	renderTime: function(){
		var container = new Element('div', {'class': 'time'}).inject(this.newContents);

		this.picker.getElement('.titleText').set('html', this.options.timePickerOnly ? this.options.selectTimeTitle : this.d.format('%d %B, %Y'));

		// Init Values for minutes & hours
		var initMinutes = (this.d.getMinutes() / this.options.timeWheelStep).round() * this.options.timeWheelStep,
			initHours = this.d.getHours();

		if (initMinutes >= 60){
			initMinutes = 0;
			initHours = initHours + 1;
			if (initHours > 23) initHours = 0;
		}

		new Element('input', { type: 'text', 'class': 'hour', 'title': MooTools.lang.get('DatePicker', 'use_mouse_wheel')})
			.set('value', this.leadZero(initHours))
			.addEvents({
				click: function(e){
					e.target.focus();
					e.stop();
				}.bind(this),
				mousewheel: function(e){
					var i = e.target, v = i.get('value').toInt();
					i.focus();
					if (e.wheel > 0){
						v = (v < 23) ? v + 1 : 0;
					} else {
						v = (v > 0) ? v - 1 : 23;
					}
					i.set('value', this.leadZero(v));
					e.stop();
				}.bind(this)
			})
			.set('maxlength', 2)
			.inject(container);

		new Element('input', { type: 'text', 'class': 'minutes', 'title': MooTools.lang.get('DatePicker', 'use_mouse_wheel')})
			.set('value', this.leadZero(initMinutes))
			.addEvents({
				click: function(e){
					e.target.focus();
					e.stop();
				}.bind(this),
				mousewheel: function(e){
					var i = e.target, v = i.get('value').toInt();
					i.focus();
					if (e.wheel > 0){
						v = (v < 59) ? v + this.options.timeWheelStep : 0;
					} else {
						v = (v > 0) ? v - this.options.timeWheelStep : (60-this.options.timeWheelStep);
					}
					if (v == 60) v = 0;

					i.set('value', this.leadZero(v));
					e.stop();
				}.bind(this)
			})
			.set('maxlength', 2)
			.inject(container);

		new Element('div', {'class': 'separator'}).set('text', ':').inject(container);

		new Element('input', {type: 'submit', value: this.options.timeConfirmButton, 'class': 'ok'})
			.addEvents({
				click: function(e){
					e.stop();
					this.select($merge(this.d.toObject(), {hours: this.picker.getElement('.hour').get('value').toInt(), minutes: this.picker.getElement('.minutes').get('value').toInt()}));
				}.bind(this)
			})
			.set('maxlength', 2)
			.inject(container);
	},

	renderMonth: function(){
		var month = this.d.getMonth();

		this.picker.getElement('.titleText').set('html', this.options.months[month] + ' ' + this.d.getFullYear());

		var date = this.d.clone();

		date.setDate(1);
		while (date.getDay() != this.options.startDay)
			date.setDate(date.getDate() - 1);


		var container = new Element('div', {'class': 'days'}).inject(this.newContents);
		var titles = new Element('div', {'class': 'titles'}).inject(container);
		var day, i, classes, e, weekcontainer;

		for (day = this.options.startDay; day < (this.options.startDay + 7); day++){
			new Element('div', {'class': 'title day day' + (day % 7)}).set('text', this.options.days[(day % 7)].substring(0, this.options.dayShort)).inject(titles);
		}

		var available = false;
		var t = this.today.toDateString();
		var currentChoice = Date.fromObject(this.choice).toDateString();

		for (i = 0; i < 42; i++){
			classes = [];
			classes.push('day');
			classes.push('day' + date.getDay());
			if (date.toDateString() == t) classes.push('today');
			if (date.toDateString() == currentChoice) classes.push('selected');
			if (date.getMonth() != month) classes.push('otherMonth');

			if (i % 7 == 0){
				weekcontainer = new Element('div', {'class': 'week week' + (Math.floor(i / 7))}).inject(container);
			}

			e = new Element('div', {'class': classes.join(' ')}).set('text', date.getDate()).inject(weekcontainer);
			if (this.limited('date')){
				e.addClass('unavailable');
				if (available){
					if (month == date.getMonth() || date.getDate() == 1){
						this.limit.right = true;
					}
				} else {
					this.limit.left = true;
				}
			} else {
				available = true;
				e.addEvent('click', function(d){
					if (this.options.timePicker){
						date.setDate(d.day);
						date.setMonth(d.month);
						this.d.setDate(d.day);
						this.d.setMonth(d.month);
						this.mode = 'time';
						this.render('fade');
					} else {
						this.select(d);
					}
				}.pass([{day: date.getDate(), month: date.getMonth(), year: date.getFullYear()}], this));
			}
			date.setDate(date.getDate() + 1);
		}
		if (!available) this.limit.right = true;
	},

	renderYear: function(){
		var month = this.today.getMonth();
		var thisyear = this.d.getFullYear() == this.today.getFullYear();
		var selectedyear = this.d.getFullYear() == this.choice.year;

		this.picker.getElement('.titleText').set('text', this.d.getFullYear());
		this.d.setMonth(0);
		if (this.options.minDate){
			this.d.decrement('month', 1);
			this.d.set('date', this.d.get('lastdayofmonth'));
			if (this.limited('month')) this.limit.left = true;
			this.d.increment('month', 1);
		}
		this.d.set('date', this.d.get('lastdayofmonth'));
		var i, e;
		var available = false;
		var container = new Element('div', {'class': 'months'}).inject(this.newContents);

		for (i = 0; i <= 11; i++){
			e = new Element('div', {
				'class': 'month month' + (i + 1) + (i == month && thisyear ? ' today' : '') + (i == this.choice.month && selectedyear ? ' selected' : '')
			}).set('text', this.options.monthShort ? this.options.months[i].substring(0, this.options.monthShort) : this.options.months[i]).inject(container);

			if (this.limited('month')){
				e.addClass('unavailable');
				if (available) this.limit.right = true;
				else this.limit.left = true;
			} else {
				available = true;
				e.addEvent('click', function(d){
					this.d.set({date: 1, month: d});
					this.mode = 'month';
					this.render('fade');
				}.pass(i, this));
			}
			this.d.increment('month', 1);
			this.d.set('date', this.d.get('lastdayofmonth'));
		}
		if (!available) this.limit.right = true;
	},

	renderDecades: function(){
		// start neatly at interval (eg. 1980 instead of 1987)
		while (this.d.getFullYear() % this.options.yearsPerPage > 0){
			this.d.setFullYear(this.d.getFullYear() - 1);
		}

		this.picker.getElement('.titleText').set('text', this.d.getFullYear() + '-' + (this.d.getFullYear() + this.options.yearsPerPage - 1));

		var i, y, e;
		var available = false;
		var container = new Element('div', {'class': 'years'}).inject(this.newContents);

		if (this.options.minDate && this.d.getFullYear() <= this.options.minDate.getFullYear()){
			this.limit.left = true;
		}

		for (i = 0; i < this.options.yearsPerPage; i++){
			y = this.d.getFullYear();
			e = new Element('div', {'class': 'year year' + i + (y == this.today.getFullYear() ? ' today' : '') + (y == this.choice.year ? ' selected' : '') }).set('text', y).inject(container);

			if (this.limited('year')){
				e.addClass('unavailable');
				if (available) this.limit.right = true;
				else this.limit.left = true;
			} else {
				available = true;
				e.addEvent('click', function(d){
					this.d.setFullYear(d);
					this.mode = 'year';
					this.render('fade');
				}.pass(y, this));
			}
			this.d.setFullYear(this.d.getFullYear() + 1);
		}
		if (!available){
			this.limit.right = true;
		}
		if (this.options.maxDate && this.d.getFullYear() >= this.options.maxDate.getFullYear()){
			this.limit.right = true;
		}
	},

	limited: function(type){
		var cs = this.options.minDate;
		var ce = this.options.maxDate;
		if (!cs && !ce) return false;

		switch (type){
			case 'year':
				return (cs && this.d.getFullYear() < this.options.minDate.getFullYear()) || (ce && this.d.getFullYear() > this.options.maxDate.getFullYear());

			case 'month':
				// todo: there has got to be an easier way...?
				var ms = ('' + this.d.getFullYear() + this.leadZero(this.d.getMonth())).toInt();
				return cs && ms < ('' + this.options.minDate.getFullYear() + this.leadZero(this.options.minDate.getMonth())).toInt()
					|| ce && ms > ('' + this.options.maxDate.getFullYear() + this.leadZero(this.options.maxDate.getMonth())).toInt()

			case 'date':
				return (cs && this.d < this.options.minDate) || (ce && this.d > this.options.maxDate);
		}
	},

	allowZoomOut: function(){
		if (this.mode == 'time' && this.options.timePickerOnly) return false;
		if (this.mode == 'decades') return false;
		if (this.mode == 'year' && !this.options.yearPicker) return false;
		return true;
	},

	zoomOut: function(){
		if (!this.allowZoomOut()) return;
		if (this.mode == 'year') this.mode = 'decades';
		else if (this.mode == 'time') this.mode = 'month';
		else this.mode = 'year';
		this.render('fade');
	},

	previous: function(){
		if (this.mode == 'decades'){
			this.d.setFullYear(this.d.getFullYear() - this.options.yearsPerPage);
		} else if (this.mode == 'year'){
			this.d.setFullYear(this.d.getFullYear() - 1);
		} else if (this.mode == 'month'){
			this.d.setDate(1);
			this.d.setMonth(this.d.getMonth() - 1);
		}
		this.render('left');
		this.fireEvent('previous');
	},

	next: function(){
		if (this.mode == 'decades'){
			this.d.setFullYear(this.d.getFullYear() + this.options.yearsPerPage);
		} else if (this.mode == 'year'){
			this.d.setFullYear(this.d.getFullYear() + 1);
		} else if (this.mode == 'month'){
			this.d.setDate(1);
			this.d.setMonth(this.d.getMonth() + 1);
		}
		this.render('right');
		this.fireEvent('next');
	},

	destroy: function(){
		this.picker.destroy();
		this.picker = null;
		this.fireEvent('close');
	},

	select: function(values){
		this.choice = $merge(this.choice, values);
		var d = Date.fromObject(this.choice);
		this.input.set('value', d.format(this.options.format))
			.store('datepicker:value', d.strftime());
		this.fireEvent('select', d);
		this.input.fireEvent('change'); // call input onChange event

		this.close();
	},

	leadZero: function(v){
		return v < 10 ? '0' + v : v;
	}

});


Date.implement({

	toObject: function(){
		return {
			year: this.getFullYear(),
			month: this.getMonth(),
			day: this.getDate(),
			hours: this.getHours(),
			minutes: this.getMinutes(),
			seconds: this.getSeconds()
		};
	}

});

Date.extend({

	fromObject: function(values){
		values = values || {};
		var d = new Date();
		d.setDate(1);
		['year', 'month', 'day', 'hours', 'minutes', 'seconds'].each(function(type){
			var v = values[type];
			if (!v && v !== 0) return;
			switch (type){
				case 'day': d.setDate(v); break;
				case 'month': d.setMonth(v); break;
				case 'year': d.setFullYear(v); break;
				case 'hours': d.setHours(v); break;
				case 'minutes': d.setMinutes(v); break;
				case 'seconds': d.setSeconds(v); break;
			}
		});
		return d;
	}

});


/**
 * Translation
 *
 */
MooTools.lang.set('en-US', 'DatePicker', {
	select_a_time: 'Select a time',
	use_mouse_wheel: 'Use the mouse wheel to quickly change value',
	time_confirm_button: 'OK'
});

MooTools.lang.set('nl-NL', 'DatePicker', {
	select_a_time: 'Selecteer een tijd',
	use_mouse_wheel: 'Gebruik uw scrollwiel om door de tijd te scrollen',
	time_confirm_button: 'OK'
});

MooTools.lang.set('cs-CZ', 'DatePicker', {
	select_a_time: 'Vyberte čas',
	use_mouse_wheel: 'Použijte kolečko myši k rychlé změně hodnoty',
	time_confirm_button: 'Zvolte čas'
});

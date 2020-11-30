!function() {
Swiff.Uploader = new Class({

	Implements: [Options, Events],

	options: {
		container: null,

		multiple: true,
		queued: true,
		verbose: false,

		url: null,
		method: null,
		data: null,
		mergeData: true,
		fieldName: null,

		allowDuplicates: false,
		fileListMax: 0,

		instantStart: false,
		appendCookieData: false,

		fileClass: null,

	  	zIndex: 9999,
	},

	initialize: function (options) {
		this.setOptions(options);

		this.target = $(this.options.target);

		this.box = this.getBox().addEvents({
			'mouseenter': this.fireEvent.bind(this, 'buttonEnter'),
			'mouseleave': this.fireEvent.bind(this, 'buttonLeave')
		});

		this.createInput().inject(this.box);

		this.reposition();
		window.addEvent('resize', this.reposition.bind(this));

		this.box.inject(document.id(this.options.container) || document.body);

		this.uploading = 0;
		this.fileList = [];

		var target = document.id(this.options.target);
		if (target) this.attach(target);
	},

	createInput: function () {
		return this.input = new Element('input', {
			type: 'file',
			name: 'Filedata',
			multiple: this.options.multiple,
			styles: {
				margin: 0,
				padding: 0,
				border: 0,
				overflow: 'hidden',
				cursor: 'pointer',
				display: 'block',
				visibility: 'visible'
			},
			events: {
				change: this.select.bind(this),
				focus: function () {
					return false;
				},
				// mousedown: function () {
				// 	if (Browser.opera || Browser.chrome) return true;
				// 	(function () {
				// 		this.input.click();
				// 		this.fireEvent('buttonDown');
				// 	}).delay(10, this)
				// 	return false;
				// }.bind(this)
			}
		});
	},

	select: function () {
		var files = this.input.files, success = [], failure = [];
		//this.file.onchange = this.file.onmousedown = this.file.onfocus = null;
		this.fireEvent('beforeSelect');

		for (var i = 0, file; file = files[i++];) {
			var cls = this.options.fileClass || Swiff.Uploader.File;
			var ret = new cls;
			ret.setBase(this, file)
			if (!ret.validate()) {
				ret.invalidate()
				ret.render();
				failure.push(ret);
				continue;
			} else {
				this.fileList.push(ret);
				ret.render();
				success.push(ret)
			}
		}
		if (success.length) this.fireEvent('onSelectSuccess', [success]);
		if (failure.length) this.fireEvent('onSelectFailed', [failure]);

		this.input.value = '';
		if (this.options.instantStart) this.start();
	},

	start: function () {
		var queued = this.options.queued;
		queued = (queued) ? ((queued > 1) ? queued : 1) : 0;

		for (var i = 0, file; file = this.fileList[i]; i++) {
			if (this.fileList[i].status != Swiff.Uploader.STATUS_QUEUED) continue;
			this.fileList[i].start();
			if (queued && this.uploading >= queued) break;
		}
		return this;
	},

	stop: function () {
		for (var i = this.fileList.length; i--;) this.fileList[i].stop();
	},

	remove: function () {
		for (var i = this.fileList.length; i--;) this.fileList[i].remove();
	},

	setEnabled: function (status) {
		this.input.disabled = !!(status);
		if (status) this.fireEvent('buttonDisable');
	},

	getTargetRelayEvents: function() {
	  return {
		buttonEnter: this.targetRelay.bind(this, 'mouseenter'),
		buttonLeave: this.targetRelay.bind(this, 'mouseleave'),
		buttonDown: this.targetRelay.bind(this, 'mousedown'),
		buttonDisable: this.targetRelay.bind(this, 'disable')
	  }
	},
	
	getTargetEvents: function() {
	  if (this.targetEvents) return this.targetEvents;
	  this.targetEvents = {
		mousemove: this.reposition.bind(this),
		mouseenter: this.reposition.bind(this),
	  };
	  return this.targetEvents;
	},
	
	targetRelay: function(name) {
	  if (this.target) this.target.fireEvent(name);
	},
	
	attach: function(target) {
	  target = document.id(target);
	  if (!this.target) this.addEvents(this.getTargetRelayEvents());
	//   else this.detach();
	  this.target = target;
	  this.target.addEvents(this.getTargetEvents(this.target));
	},
	
	detach: function(target) {
	  if (!target) target = this.target;
	  target.removeEvents(this.getTargetEvents(target));
	  delete this.target;
	},
  
	reposition: function(coords) {
	  // update coordinates, manual or automatically
	  coords = coords || (this.target && this.target.offsetHeight)
		? this.target.getCoordinates(this.box.getOffsetParent())
		: {top: window.getScrollTop(), left: 0, width: 40, height: 40}
	  this.box.setStyles(coords);
	  this.fireEvent('reposition', [coords, this.box, this.target]);
	},
	
	getBox: function() {
	  if (this.box) return this.box;
	  var scroll = window.getScroll();
	  this.box = new Element('div').setStyles({
		position: 'absolute',
		opacity: 0.02,
		zIndex: this.options.zIndex,
		overflow: 'hidden',
		height: 100, width: 100,
		top: scroll.y, left: scroll.x
	  });
	  this.box.inject(document.id(this.options.container) || document.body);
	  return this.box;
	}
});

$extend(Swiff.Uploader, {

	STATUS_QUEUED: 0,
	STATUS_RUNNING: 1,
	STATUS_ERROR: 2,
	STATUS_COMPLETE: 3,
	STATUS_STOPPED: 4,

	log: function() {
		if (window.console && console.info) console.info.apply(console, arguments);
	},

	unitLabels: {
		b: [{min: 1, unit: 'B'}, {min: 1024, unit: 'kB'}, {min: 1048576, unit: 'MB'}, {min: 1073741824, unit: 'GB'}],
		s: [{min: 1, unit: 's'}, {min: 60, unit: 'm'}, {min: 3600, unit: 'h'}, {min: 86400, unit: 'd'}]
	},

	formatUnit: function(base, type, join) {
		var labels = Swiff.Uploader.unitLabels[(type == 'bps') ? 'b' : type];
		var append = (type == 'bps') ? '/s' : '';
		var i, l = labels.length, value;

		if (base < 1) return '0 ' + labels[0].unit + append;

		if (type == 's') {
			var units = [];

			for (i = l - 1; i >= 0; i--) {
				value = Math.floor(base / labels[i].min);
				if (value) {
					units.push(value + ' ' + labels[i].unit);
					base -= value * labels[i].min;
					if (!base) break;
				}
			}

			return (join === false) ? units : units.join(join || ', ');
		}

		for (i = l - 1; i >= 0; i--) {
			value = labels[i].min;
			if (base >= value) break;
		}

		return (base / value).toFixed(1) + ' ' + labels[i].unit + append;
	}

});

Swiff.Uploader.qualifyPath = (function() {
	
	var anchor;
	
	return function(path) {
		(anchor || (anchor = new Element('a'))).href = path;
		return anchor.href;
	};

})();

Swiff.Uploader.File = new Class({
	Implements: [Events, Options],

	options: {
		url: null,
		method: null,
		data: null,
		mergeData: true,
		fieldName: null
	},

	setBase: function (base) {
		this.base = base;
		this.target = base.target;
		if (this.options.fieldName == null)
			this.options.fieldName = this.base.options.fieldName;
		this.fireEvent('setBase', base);
		var args = Array.prototype.slice.call(arguments, 1);
		if (args.length) this.setData.apply(this, args);
		return this;
	},

	setData: function(file) {
		this.status = Swiff.Uploader.STATUS_QUEUED;
		this.dates = {};
		this.dates.add = new Date();
		this.file = file;
		this.setFile({name: file.name, size: file.size, type: file.type});
		  return this;
	},
	triggerEvent: function (name) {
		var args = Array.prototype.slice.call(arguments, 1);
		var augmented = [this].concat(args);
		this.base.fireEvent('file' + name.capitalize(), augmented);
		Swiff.Uploader.log('File::' + name, augmented);
		return this.fireEvent(name, args);
	},

	setProperties: function (properties) {
		return $extend(this, properties);
	},

	setFile: function (file) {
		if (file) this.setProperties(file);
		if (!this.name && this.filename) this.name = this.filename;
		this.fireEvent('setFile', this);
		if (this.name) this.extension = this.name.replace(/^.*\./, '').toLowerCase();
		return this;
	},

	render: function () {
		return this;
	},

	cancel: function () {
		if (this.base) this.stop();
		this.remove();
	},
	validate: function () {
		var base = this.base.options;

		if (!base.allowDuplicates) {
			var name = this.name;
			var dup = this.base.fileList.some(function (file) {
				return (file.name == name);
			});
			if (dup) {
				this.validationError = 'duplicate';
				return false;
			}
		}

		if (base.fileListSizeMax && (this.base.size + this.size) > base.fileListSizeMax) {
			this.validationError = 'fileListSizeMax';
			return false;
		}

		if (base.fileListMax && this.base.fileList.length >= base.fileListMax) {
			this.validationError = 'fileListMax';
			return false;
		}

		return true;
	},

	invalidate: function () {
		this.invalid = true;
		return this.triggerEvent('invalid');
	},

	onProgress: function (progress) {
		this.$progress = {
			bytesLoaded: progress.loaded,
			percentLoaded: progress.loaded / progress.total * 100,
			total: progress.total
		};
		this.triggerEvent('progress', this.$progress);
	},

	onFailure: function () {
		if (this.status != Swiff.Uploader.STATUS_RUNNING) return;

		this.status = Swiff.Uploader.STATUS_ERROR;
		delete this.xhr;

		this.triggerEvent('fail')
		console.error('failure :(', this, Array.from(arguments))
	},

	onSuccess: function (response) {
		if (this.status != Swiff.Uploader.STATUS_RUNNING) return;

		this.status = Swiff.Uploader.STATUS_COMPLETE;

		delete this.file;

		this.base.uploading--;
		this.dates.complete = new Date();
		this.response = response;

		this.triggerEvent('complete');
		this.base.start();

		delete this.xhr;
	},

	start: function () {
		if (this.status != Swiff.Uploader.STATUS_QUEUED) return this;

		var base = this.base.options, options = this.options;

		var merged = {};
		for (var key in base) {
			merged[key] = (this.options[key] != null) ? this.options[key] : base[key];
		}

		if (merged.data) {
			if (merged.mergeData && base.data && options.data) {
				if ($type(base.data) == 'string') merged.data = base.data + '&' + options.data;
				else merged.data = Object.merge(base.data, options.data);
			}
			var query = ($type(merged.data) == 'string') ? merged.data : Hash.toQueryString(merged.data);
		}

		var xhr = this.xhr = new XMLHttpRequest, self = this;
		xhr.upload.onprogress = this.onProgress.bind(this);
		xhr.upload.onload = function () {
			setTimeout(function () {
				if (xhr.readyState === 4) {
					try { var status = xhr.status } catch (e) { };
					self.response = { text: xhr.responseText }
					self[(status < 300 && status > 199) ? 'onSuccess' : 'onFailure'](self.response)
				} else setTimeout(arguments.callee, 15);
			}, 15);
		}
		xhr.upload.onerror = xhr.upload.onabort = this.onFailure.bind(this)

		this.status = Swiff.Uploader.STATUS_RUNNING;
		this.base.uploading++;

		xhr.open("post", (merged.url) + (query ? "?" + query : ""), true);
		xhr.setRequestHeader("Cache-Control", "no-cache");
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

		var data = new FormData();
		data.append(this.options.fieldName || "Filedata", this.file);
		if (data.fake) {
			xhr.setRequestHeader("Content-Type", "multipart/form-data; boundary=" + data.boundary);
			xhr.sendAsBinary(data.toString());
		} else {
			xhr.send(data);
		}

		this.dates.start = new Date();

		this.triggerEvent('start');

		return this;
	},

	requeue: function () {
		this.stop();
		this.status = Swiff.Uploader.STATUS_QUEUED;
		this.triggerEvent('requeue');
	},

	stop: function (soft) {
		if (this.status == Swiff.Uploader.STATUS_RUNNING) {
			this.status = Swiff.Uploader.STATUS_STOPPED;
			this.base.uploading--;
			this.base.start();
			this.xhr.abort();
			if (!soft) this.triggerEvent('stop');
		}
		return this;
	},

	remove: function () {
		this.stop(true);
		delete this.xhr;
		this.base.fileList.erase(this);
		this.triggerEvent('remove');
		return this;
	}
});

}.call(this);

/**
 * jwplayerControlbar component of the JW Player.
 *
 * @author jeroen
 * @version 1.0alpha
 * @lastmodifiedauthor zach
 * @lastmodifieddate 2010-04-11
 */
(function($) {
	var controlbars = {};

	/** Hooking the jwplayerControlbar up to jQuery. **/
	$.fn.jwplayerControlbar = function(player, domelement) {
		controlbars[player.id] = $.extend({}, $.fn.jwplayerControlbar.defaults, player.config.plugins.controlbar);
		buildElements(player, domelement);
		buildHandlers(player);
	};

	$.fn.jwplayerControlbar.positions = {
		BOTTOM: 'BOTTOM',
		TOP: 'TOP',
		OVER: 'OVER'
	};


	/** Map with config for the jwplayerControlbar plugin. **/
	$.fn.jwplayerControlbar.defaults = {
		fontsize: 10,
		fontcolor: '000000',
		position: $.fn.jwplayerControlbar.positions.BOTTOM,
		leftmargin: 0,
		rightmargin: 0,
		scrubber: 'none'
	};

	/** Draw the jwplayerControlbar elements. **/
	function buildElements(player, domelement) {
		// Draw the background.
		domelement.parents(":first").append('<div id="' + player.id + '_jwplayerControlbar"></div>');
		$("#" + player.id + '_jwplayerControlbar').css('position', 'absolute');
		$("#" + player.id + '_jwplayerControlbar').css('height', player.skin.controlbar.elements.background.height);
		switch (controlbars[player.id].position) {
			case $.fn.jwplayerControlbar.positions.TOP:
				$("#" + player.id + '_jwplayerControlbar').css('top', 0);
				break;
			default:
				$("#" + player.id + '_jwplayerControlbar').css('top', player.height());
				domelement.parents(":first").css('height', parseInt(domelement.parents(":first").css('height').replace('px', '')) + player.skin.controlbar.elements.background.height);
				break;
		}
		$("#" + player.id + '_jwplayerControlbar').css('background', 'url(' + player.skin.controlbar.elements.background.src + ') repeat-x center left');
		// Draw all elements on top of the bar.
		buildElement('capLeft', 'left', true, player);
		buildElement('playButton', 'left', false, player);
		buildElement('pauseButton', 'left', true, player);
		buildElement('divider1', 'left', true, player);
		buildElement('elapsedText', 'left', true, player);
		buildElement('timeSliderRail', 'left', false, player);
		buildElement('timeSliderBuffer', 'left', false, player);
		buildElement('timeSliderProgress', 'left', false, player);
		buildElement('timeSliderThumb', 'left', false, player);
		buildElement('capRight', 'right', true, player);
		// TODO
		if (false) {
			buildElement('fullscreenButton', 'right', false, player);
			buildElement('normalscreenButton', 'right', true, player);
			buildElement('divider2', 'right', true, player);
		}
		if (!$.fn.jwplayerUtils.isiPad()) {
			buildElement('volumeSliderRail', 'right', false, player);
			buildElement('volumeSliderProgress', 'right', true, player);
			buildElement('muteButton', 'right', false, player);
			buildElement('unmuteButton', 'right', true, player);
			buildElement('divider3', 'right', true, player);
		}
		buildElement('durationText', 'right', true, player);
	}


	/** Draw a single element into the jwplayerControlbar. **/
	function buildElement(element, align, offset, player) {
		var nam = player.id + '_' + element;
		$('#' + player.id + '_jwplayerControlbar').append('<div id="' + nam + '"></div>');
		$('#' + nam).css('position', 'absolute');
		$('#' + nam).css('top', '0px');
		if (element.indexOf('Text') > 0) {
			$('#' + nam).html('00:00');
			$('#' + nam).css('font', controlbars[player.id].fontsize + 'px/' + (player.skin.controlbar.elements.background.height + 1) + 'px Arial,sans-serif');
			$('#' + nam).css('text-align', 'center');
			$('#' + nam).css('font-weight', 'bold');
			$('#' + nam).css('cursor', 'default');
			var wid = 14 + 3 * controlbars[player.id].fontsize;
			$('#' + nam).css('color', '#' + controlbars[player.id].fontcolor.substr(-6));
		} else if (element.indexOf('divider') === 0) {
			$('#' + nam).css('background', 'url(' + player.skin.controlbar.elements.divider.src + ') repeat-x center left');
			var wid = player.skin.controlbar.elements.divider.width;
		} else {
			$('#' + nam).css('background', 'url(' + player.skin.controlbar.elements[element].src + ') repeat-x center left');
			var wid = player.skin.controlbar.elements[element].width;
		}
		if (align == 'left') {
			$('#' + nam).css(align, controlbars[player.id].leftmargin);
			if (offset) {
				controlbars[player.id].leftmargin += wid;
			}
		} else if (align == 'right') {
			$('#' + nam).css(align, controlbars[player.id].rightmargin);
			if (offset) {
				controlbars[player.id].rightmargin += wid;
			}
		}
		$('#' + nam).css('width', wid);
		$('#' + nam).css('height', player.skin.controlbar.elements.background.height);
	}


	/** Add interactivity to the jwplayerControlbar elements. **/
	function buildHandlers(player) {
		// Register events with the buttons.
		buildHandler('playButton', 'play', player);
		buildHandler('pauseButton', 'pause', player);
		buildHandler('muteButton', 'mute', player, true);
		buildHandler('unmuteButton', 'mute', player, false);
		buildHandler('fullscreenButton', 'fullscreen', player, true);
		buildHandler('normalscreenButton', 'fullscreen', player, false);

		addSliders(player);

		// Register events with the player.
		player.buffer(bufferHandler);
		player.state(stateHandler);
		player.time(timeHandler);
		player.mute(muteHandler);
		player.volume(volumeHandler);
		player.complete(completeHandler);

		// Trigger a few events so the bar looks good on startup.
		resizeHandler({
			id: player.id,
			fulscreen: player.fullscreen(),
			width: player.width(),
			height: player.height()
		});
		timeHandler({
			id: player.id,
			duration: player.duration(),
			position: 0
		});
		bufferHandler({
			id: player.id,
			bufferProgress: 0
		});
		muteHandler({
			id: player.id,
			mute: player.mute()
		});
		stateHandler({
			id: player.id,
			newstate: $.fn.jwplayer.states.IDLE
		});
		volumeHandler({
			id: player.id,
			volume: player.volume()
		});
	}


	/** Set a single button handler. **/
	function buildHandler(element, handler, player, args) {
		var nam = player.id + '_' + element;
		$('#' + nam).css('cursor', 'pointer');
		if (handler == 'fullscreen') {
			$('#' + nam).mouseup(function(evt) {
				evt.stopPropagation();
				player.fullscreen(!player.fullscreen());
				resizeHandler({
					id: player.id,
					fullscreen: player.fullscreen(),
					width: player.width(),
					height: player.height()
				});
			});
		} else {
			$('#' + nam).mouseup(function(evt) {
				evt.stopPropagation();
				if (!$.fn.jwplayerUtils.isNull(args)) {
					player[handler](args);
				} else {
					player[handler]();
				}

			});
		}
	}


	/** Set the volume drag handler. **/
	function addSliders(player) {
		var bar = '#' + player.id + '_jwplayerControlbar';
		var trl = '#' + player.id + '_timeSliderRail';
		var vrl = '#' + player.id + '_volumeSliderRail';
		$(bar).css('cursor', 'pointer');
		$(trl).css('cursor', 'pointer');
		$(vrl).css('cursor', 'pointer');
		$(bar).mousedown(function(evt) {
			if (evt.pageX >= $(trl).offset().left - window.pageXOffset && evt.pageX <= $(trl).offset().left - window.pageXOffset + $(trl).width()) {
				controlbars[player.id].scrubber = 'time';
			} else if (evt.pageX >= $(vrl).offset().left - window.pageXOffset && evt.pageX <= $(vrl).offset().left - window.pageXOffset + $(trl).width()) {
				controlbars[player.id].scrubber = 'volume';
			}
		});
		$(bar).mouseup(function(evt) {
			evt.stopPropagation();
			sliderUp(evt.pageX, player);
		});
		$(bar).mousemove(function(evt) {
			if (controlbars[player.id].scrubber == 'time') {
				controlbars[player.id].mousedown = true;
				var xps = evt.pageX - $(bar).offset().left - window.pageXOffset;
				$('#' + player.id + '_timeSliderThumb').css('left', xps);
			}
		});
	}


	/** The slider has been moved up. **/
	function sliderUp(msx, player) {
		controlbars[player.id].mousedown = false;
		if (controlbars[player.id].scrubber == 'time') {
			var xps = msx - $('#' + player.id + '_timeSliderRail').offset().left + window.pageXOffset;
			var wid = $('#' + player.id + '_timeSliderRail').width();
			var pos = xps / wid * controlbars[player.id].currentDuration;
			if (pos < 0) {
				pos = 0;
			} else if (pos > controlbars[player.id].currentDuration) {
				pos = controlbars[player.id].currentDuration - 3;
			}
			player.seek(pos);
			if (player.model.state != $.fn.jwplayer.states.PLAYING) {
				player.play();
			}
		} else if (controlbars[player.id].scrubber == 'volume') {
			var xps = msx - $('#' + player.id + '_volumeSliderRail').offset().left - window.pageXOffset;
			var wid = $('#' + player.id + '_volumeSliderRail').width();
			var pct = Math.round(xps / wid * 100);
			if (pct < 0) {
				pct = 0;
			} else if (pct > 100) {
				pct = 100;
			}
			if (player.model.mute) {
				player.mute(false);
			}
			player.volume(pct);
		}
		controlbars[player.id].scrubber = 'none';
	}


	/** Update the buffer percentage. **/
	function bufferHandler(event) {
		if (!$.fn.jwplayerUtils.isNull(event.bufferPercent)) {
			controlbars[event.id].currentBuffer = event.bufferPercent;
		}

		var wid = $('#' + event.id + '_timeSliderRail').width();
		var bufferWidth = isNaN(Math.round(wid * controlbars[event.id].currentBuffer / 100)) ? 0 : Math.round(wid * controlbars[event.id].currentBuffer / 100);
		$('#' + event.id + '_timeSliderBuffer').css('width', bufferWidth);
	}


	/** Update the mute state. **/
	function muteHandler(event) {
		if (event.mute) {
			$('#' + event.id + '_muteButton').css('display', 'none');
			$('#' + event.id + '_unmuteButton').css('display', 'block');
			$('#' + event.id + '_volumeSliderProgress').css('display', 'none');
		} else {
			$('#' + event.id + '_muteButton').css('display', 'block');
			$('#' + event.id + '_unmuteButton').css('display', 'none');
			$('#' + event.id + '_volumeSliderProgress').css('display', 'block');
		}
	}


	/** Update the playback state. **/
	function stateHandler(event) {
		// Handle the play / pause button
		if (event.newstate == $.fn.jwplayer.states.BUFFERING || event.newstate == $.fn.jwplayer.states.PLAYING) {
			$('#' + event.id + '_pauseButton').css('display', 'block');
			$('#' + event.id + '_playButton').css('display', 'none');
		} else {
			$('#' + event.id + '_pauseButton').css('display', 'none');
			$('#' + event.id + '_playButton').css('display', 'block');
		}

		// Show / hide progress bar
		if (event.newstate == $.fn.jwplayer.states.IDLE) {
			$('#' + event.id + '_timeSliderBuffer').css('display', 'none');
			$('#' + event.id + '_timeSliderProgress').css('display', 'none');
			$('#' + event.id + '_timeSliderThumb').css('display', 'none');
		} else {
			$('#' + event.id + '_timeSliderBuffer').css('display', 'block');
			if (event.newstate != $.fn.jwplayer.states.BUFFERING) {
				$('#' + event.id + '_timeSliderProgress').css('display', 'block');
				$('#' + event.id + '_timeSliderThumb').css('display', 'block');
			}
		}
	}

	/** Handles event completion **/
	function completeHandler(event) {
		timeHandler($.extend(event, {
			position: 0,
			duration: controlbars[event.id].currentDuration
		}));
	}


	/** Update the playback time. **/
	function timeHandler(event) {
		if (!$.fn.jwplayerUtils.isNull(event.position)) {
			controlbars[event.id].currentPosition = event.position;
		}
		if (!$.fn.jwplayerUtils.isNull(event.duration)) {
			controlbars[event.id].currentDuration = event.duration;
		}
		var progress = (controlbars[event.id].currentPosition === controlbars[event.id].currentDuration === 0) ? 0 : controlbars[event.id].currentPosition / controlbars[event.id].currentDuration;
		var railWidth = $('#' + event.id + '_timeSliderRail').width();
		var thumbWidth = $('#' + event.id + '_timeSliderThumb').width();
		var railLeft = $('#' + event.id + '_timeSliderRail').position().left;
		var progressWidth = isNaN(Math.round(railWidth * progress)) ? 0 : Math.round(railWidth * progress);
		var thumbPosition = railLeft + progressWidth;

		$('#' + event.id + '_timeSliderProgress').css('width', progressWidth);
		if (!controlbars[event.id].mousedown) {
			$('#' + event.id + '_timeSliderThumb').css('left', thumbPosition);
		}

		$('#' + event.id + '_durationText').html(timeFormat(controlbars[event.id].currentDuration));
		$('#' + event.id + '_elapsedText').html(timeFormat(controlbars[event.id].currentPosition));
	}


	/** Format the elapsed / remaining text. **/
	function timeFormat(sec) {
		str = '00:00';
		if (sec > 0) {
			str = Math.floor(sec / 60) < 10 ? '0' + Math.floor(sec / 60) + ':' : Math.floor(sec / 60) + ':';
			str += Math.floor(sec % 60) < 10 ? '0' + Math.floor(sec % 60) : Math.floor(sec % 60);
		}
		return str;
	}


	/** Flip the player size to/from full-browser-screen. **/
	function resizeHandler(event) {
		controlbars[event.id].width = event.width;
		controlbars[event.id].fullscreen = event.fullscreen;
		if (event.fullscreen) {
			$('#' + event.id + '_normalscreenButton').css('display', 'block');
			$('#' + event.id + '_fullscreenButton').css('display', 'none');
			// TODO
			if (false) {
				$(window).resize(function() {
					resizeBar(player);
				});
			}
		} else {
			$('#' + event.id + '_normalscreenButton').css('display', 'none');
			$('#' + event.id + '_fullscreenButton').css('display', 'block');
			// TODO
			if (false) {
				$(window).resize(null);
			}
		}
		resizeBar(event);
		timeHandler(event);
		bufferHandler(event);
	}


	/** Resize the jwplayerControlbar. **/
	function resizeBar(event) {
		var lft = controlbars[event.id].left;
		var top = controlbars[event.id].top;
		var wid = controlbars[event.id].width;
		var hei = $('#' + event.id + '_jwplayerControlbar').height();
		if (controlbars[event.id].position == 'over') {
			lft += 1 * controlbars[event.id].margin;
			top -= 1 * controlbars[event.id].margin + hei;
			wid -= 2 * controlbars[event.id].margin;
		}
		if (controlbars[event.id].fullscreen) {
			lft = controlbars[event.id].margin;
			top = $(window).height() - controlbars[event.id].margin - hei;
			wid = $(window).width() - 2 * controlbars[event.id].margin;
			$('#' + event.id + '_jwplayerControlbar').css('z-index', 99);
		} else {
			$('#' + event.id + '_jwplayerControlbar').css('z-index', 97);
		}
		$('#' + event.id + '_jwplayerControlbar').css('left', lft);
		$('#' + event.id + '_jwplayerControlbar').css('top', top);
		$('#' + event.id + '_jwplayerControlbar').css('width', wid);
		$('#' + event.id + '_timeSliderRail').css('width', (wid - controlbars[event.id].leftmargin - controlbars[event.id].rightmargin));
	}


	/** Update the volume level. **/
	function volumeHandler(event) {
		var progress = isNaN(event.volume / 100) ? 1 : event.volume / 100;
		var railWidth = $('#' + event.id + '_volumeSliderRail').width();
		var railRight = parseInt($('#' + event.id + '_volumeSliderRail').css('right').toString().replace('px', ''), 10);
		var progressWidth = isNaN(Math.round(railWidth * progress)) ? 0 : Math.round(railWidth * progress);

		$('#' + event.id + '_volumeSliderProgress').css('width', progressWidth);
		$('#' + event.id + '_volumeSliderProgress').css('right', (railWidth + railRight - progressWidth));
	}


})(jQuery);
/**
 * JW Player controller component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	var mediaParams = function() {
		return {
			volume: 100,
			fullscreen: false,
			mute: false,
			width: 480,
			height: 320,
			duration: 0,
			source: 0,
			sources: [],
			buffer: 0,
			position: 0,
			state: $.fn.jwplayer.states.IDLE
		};
	};

	$.fn.jwplayerController = function(player) {
		return {
			play: play(player),
			pause: pause(player),
			seek: seek(player),
			stop: stop(player),
			volume: volume(player),
			mute: mute(player),
			resize: resize(player),
			fullscreen: fullscreen(player),
			load: load(player),
			mediaInfo: mediaInfo(player),
			addEventListener: addEventListener(player),
			removeEventListener: removeEventListener(player),
			sendEvent: sendEvent(player)
		};
	};


	function play(player) {
		return function() {
			try {
				switch (player.model.state) {
					case $.fn.jwplayer.states.IDLE:
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER_FULL, player.media.play);
						player.media.load(player.model.sources[player.model.source].file);
						break;
					case $.fn.jwplayer.states.PAUSED:
						player.media.play();
						break;
				}

				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}

	/** Switch the pause state of the player. **/
	function pause(player) {
		return function() {
			try {
				switch (player.model.state) {
					case $.fn.jwplayer.states.PLAYING:
					case $.fn.jwplayer.states.BUFFERING:
						player.media.pause();
						break;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Seek to a position in the video. **/
	function seek(player) {
		return function(position) {
			try {
				switch (player.model.state) {
					case $.fn.jwplayer.states.PLAYING:
					case $.fn.jwplayer.states.PAUSED:
					case $.fn.jwplayer.states.BUFFERING:
						player.media.seek(position);
						break;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Stop playback and loading of the video. **/
	function stop(player) {
		return function() {
			try {
				player.media.stop();
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Get / set the video's volume level. **/
	function volume(player) {
		return function(arg) {
			try {
				switch ($.fn.jwplayerUtils.typeOf(arg)) {
					case "function":
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_MEDIA_VOLUME, arg);
						break;
					case "number":
						player.media.volume(arg);
						return true;
					case "string":
						player.media.volume(parseInt(arg, 10));
						return true;
					default:
						return player.model.volume;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}

	/** Get / set the mute state of the player. **/
	function mute(player) {
		return function(arg) {
			try {
				switch ($.fn.jwplayerUtils.typeOf(arg)) {
					case "function":
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_MEDIA_MUTE, arg);
						break;
					case "boolean":
						player.media.mute(arg);
						break;
					default:
						return player.model.mute;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Resizes the video **/
	function resize(player) {
		return function(arg1, arg2) {
			try {
				switch ($.fn.jwplayerUtils.typeOf(arg1)) {
					case "function":
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_RESIZE, arg1);
						break;
					case "number":
						player.media.resize(arg1, arg2);
						break;
					case "string":
						player.media.resize(arg1, arg2);
						break;
					default:
						break;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Jumping the player to/from fullscreen. **/
	function fullscreen(player) {
		return function(arg) {
			try {
				switch ($.fn.jwplayerUtils.typeOf(arg)) {
					case "function":
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_FULLSCREEN, arg);
						break;
					case "boolean":
						player.media.fullscreen(arg);
						break;
					default:
						return player.model.fullscreen;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}

	/** Loads a new video **/
	function load(player) {
		return function(arg) {
			try {
				switch ($.fn.jwplayerUtils.typeOf(arg)) {
					case "function":
						player.addEventListener($.fn.jwplayer.events.JWPLAYER_MEDIA_LOADED, arg);
						break;
					default:
						player.media.load(arg);
						break;
				}
				return $.jwplayer(player.id);
			} catch (err) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, err);
			}
			return false;
		};
	}


	/** Returns the meta **/
	function mediaInfo(player) {
		return function() {
			try {
				var result = {};
				for (var mediaParam in mediaParams()) {
					result[mediaParam] = player.model[mediaParam];
				}
				return result;
			} catch (err) {
				$.fn.jwplayerUtils.log("error", err);
			}
			return false;
		};
	}


	/** Add an event listener. **/
	function addEventListener(player) {
		return function(type, listener, count) {
			try {
				if (player.listeners[type] === undefined) {
					player.listeners[type] = [];
				}
				player.listeners[type].push({
					listener: listener,
					count: count
				});
			} catch (err) {
				$.fn.jwplayerUtils.log("error", err);
			}
			return false;
		};
	}


	/** Remove an event listener. **/
	function removeEventListener(player) {
		return function(type, listener) {
			try {
				for (var lisenterIndex in player.listeners[type]) {
					if (player.listeners[type][lisenterIndex] == listener) {
						player.listeners[type].slice(lisenterIndex, lisenterIndex + 1);
						break;
					}
				}
			} catch (err) {
				$.fn.jwplayerUtils.log("error", err);
			}
			return false;
		};
	}

	/** Send an event **/
	function sendEvent(player) {
		return function(type, data) {
			data = $.extend({
				id: player.id,
				version: player.version
			}, data);
			if ((player.config.debug !== undefined) && (player.config.debug.toString().toLowerCase() == 'console')) {
				$.fn.jwplayerUtils.log(type, data);
			}
			for (var listenerIndex in player.listeners[type]) {
				try {
					player.listeners[type][listenerIndex].listener(data);
				} catch (err) {
					$.fn.jwplayerUtils.log("There was an error while handling a listener", err);
				}
				if (player.listeners[type][listenerIndex].count === 1) {
					delete player.listeners[type][listenerIndex];
				} else if (player.listeners[type][listenerIndex].count > 0) {
					player.listeners[type][listenerIndex].count = player.listeners[type][listenerIndex].count - 1;
				}
			}
		};
	}

})(jQuery);
/**
 * Core component of the JW Player (initialization, API).
 *
 * @author jeroen
 * @version 1.0alpha
 * @lastmodifiedauthor zach
 * @lastmodifieddate 2010-04-11
 */
(function($) {
	/** Map with all players on the page. **/
	var players = {};

	/** Hooking the controlbar up to jQuery. **/
	$.fn.jwplayer = function(options) {
		return this.each(function() {
			$.fn.jwplayerUtils.log("Starting setup", this);
			return setupJWPlayer($(this), 0, options);
		});
	};

	function setupJWPlayer(player, step, options) {
		try {
			switch (step) {
				case 0:
					var model = $.fn.jwplayerModel(player, options);
					var jwplayer = {
						model: model,
						listeners: {}
					};
					return setupJWPlayer(jwplayer, step + 1);
				case 1:
					player.controller = $.fn.jwplayerController(player);
					players[player.model.config.id] = player;
					setupJWPlayer($.extend(player, api(player)), step + 1);
					return player;
				case 2:
					$.fn.jwplayerSkinner(player, function() {
						setupJWPlayer(player, step + 1);
					});
					break;
				case 3:
					$.fn.jwplayerView(player);
					setupJWPlayer(player, step + 1);
					break;
				case 4:
					$.fn.jwplayerModel.setActiveMediaProvider(player);
					if ((player.media === undefined) || !player.media.hasChrome) {
						setupJWPlayer(player, step + 1);
					}
					break;
				case 5:
					$.fn.jwplayerDisplay($.jwplayer(player.id), player.model.domelement);
					if (player.media === undefined) {
						player.sendEvent($.fn.jwplayer.events.JWPLAYER_READY);
					} else {
						setupJWPlayer(player, step + 1);
					}
					break;
				case 6:
					if (!$.fn.jwplayerUtils.isiPhone()) {
						$.fn.jwplayerControlbar($.jwplayer(player.id), player.model.domelement);
					}
					setupJWPlayer(player, step + 1);
					break;
				case 7:
					player.sendEvent($.fn.jwplayer.events.JWPLAYER_READY);
					setupJWPlayer(player, step + 1);
					break;
				default:
					if (player.config.autostart === true) {
						player.play();
					}
					break;
			}
		} catch (err) {
			$.fn.jwplayerUtils.log("Setup failed at step " + step, err);
		}
	}


	/** Map with config for the controlbar plugin. **/
	$.fn.jwplayer.defaults = {
		autostart: false,
		file: undefined,
		height: 295,
		image: undefined,
		skin: undefined,
		volume: 90,
		width: 480,
		mute: false,
		bufferlength: 5,
		start: 0,
		position: 0,
		debug: undefined,
		flashplayer: undefined,
		repeat: false
	};


	/** A factory for API calls that either set listeners or return data **/
	function dataListenerFactory(player, dataType, eventType) {
		return function(arg) {
			switch ($.fn.jwplayerUtils.typeOf(arg)) {
				case "function":
					if (!$.fn.jwplayerUtils.isNull(eventType)) {
						player.addEventListener(eventType, arg);
					}
					break;
				default:
					if (!$.fn.jwplayerUtils.isNull(dataType)) {
						return player.controller.mediaInfo()[dataType];
					}
					return player.controller.mediaInfo();
			}
			return $.jwplayer(player.id);
		};
	}


	function api(player) {
		if (!$.fn.jwplayerUtils.isNull(player.id)) {
			return player;
		}
		return {
			play: player.controller.play,
			pause: player.controller.pause,
			stop: player.controller.stop,
			seek: player.controller.seek,

			resize: player.controller.resize,
			fullscreen: player.controller.fullscreen,
			volume: player.controller.volume,
			mute: player.controller.mute,
			load: player.controller.load,

			addEventListener: player.controller.addEventListener,
			removeEventListener: player.controller.removeEventListener,
			sendEvent: player.controller.sendEvent,

			ready: dataListenerFactory(player, null, $.fn.jwplayer.events.JWPLAYER_READY),
			error: dataListenerFactory(player, null, $.fn.jwplayer.events.JWPLAYER_ERROR),
			complete: dataListenerFactory(player, null, $.fn.jwplayer.events.JWPLAYER_MEDIA_COMPLETE),
			state: dataListenerFactory(player, 'state', $.fn.jwplayer.events.JWPLAYER_PLAYER_STATE),
			buffer: dataListenerFactory(player, 'buffer', $.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER),
			time: dataListenerFactory(player, null, $.fn.jwplayer.events.JWPLAYER_MEDIA_TIME),
			position: dataListenerFactory(player, 'position'),
			duration: dataListenerFactory(player, 'duration'),
			width: dataListenerFactory(player, 'width'),
			height: dataListenerFactory(player, 'height'),
			meta: dataListenerFactory(player, null, $.fn.jwplayer.events.JWPLAYER_MEDIA_META),

			id: player.model.config.id,
			config: player.model.config,
			version: '0.1-alpha',
			skin: player.skin
		};
	}

	function jwplayer(selector) {
		if ($.fn.jwplayerUtils.isNull(selector)) {
			for (var player in players) {
				return api(players[player]);
			}
		} else {
			if (selector.indexOf('#') === 0) {
				selector = selector.substr(1, selector.length);
			}
			return api(players[selector]);
		}
		return null;
	}

	$.fn.jwplayer.states = {
		IDLE: 'IDLE',
		BUFFERING: 'BUFFERING',
		PLAYING: 'PLAYING',
		PAUSED: 'PAUSED'
	};

	$.fn.jwplayer.events = {
		JWPLAYER_READY: 'jwplayerReady',
		JWPLAYER_FULLSCREEN: 'jwplayerFullscreen',
		JWPLAYER_RESIZE: 'jwplayerResize',
		//JWPLAYER_LOCKED: 'jwplayerLocked',
		//JWPLAYER_UNLOCKED: 'jwplayerLocked',
		JWPLAYER_ERROR: 'jwplayerError',
		JWPLAYER_MEDIA_BUFFER: 'jwplayerMediaBuffer',
		JWPLAYER_MEDIA_BUFFER_FULL: 'jwplayerMediaBufferFull',
		JWPLAYER_MEDIA_ERROR: 'jwplayerMediaError',
		JWPLAYER_MEDIA_LOADED: 'jwplayerMediaLoaded',
		JWPLAYER_MEDIA_COMPLETE: 'jwplayerMediaComplete',
		JWPLAYER_MEDIA_TIME: 'jwplayerMediaTime',
		JWPLAYER_MEDIA_VOLUME: 'jwplayerMediaVolume',
		JWPLAYER_MEDIA_META: 'jwplayerMediaMeta',
		JWPLAYER_MEDIA_MUTE: 'jwplayerMediaMute',
		JWPLAYER_PLAYER_STATE: 'jwplayerPlayerState'
	};

	/** Extending jQuery **/
	$.extend({
		'jwplayer': jwplayer
	});

	/** Automatically initializes the player for all <video> tags with the JWPlayer class. **/
	$(document).ready(function() {
		$("video.jwplayer").jwplayer();
	});

})(jQuery);
/**
 * JW Player Defaul
 *
 * @author jeroen
 * @version 1.0alpha
 * @lastmodifiedauthor zach
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	/** Constructor **/
	$.fn.jwplayerDefaultSkin = '<?xml version="1.0" ?><skin author="LongTail Video" name="Five" version="1.0"><settings><setting name="backcolor" value="0xFFFFFF"/><setting name="frontcolor" value="0x000000"/><setting name="lightcolor" value="0x000000"/><setting name="screencolor" value="0x000000"/></settings><components><component name="controlbar"><settings><setting name="margin" value="20"/><setting name="fontsize" value="11"/></settings><elements><element name="background" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAIAAABvFaqvAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAFJJREFUeNrslLENwAAIwxLU/09j5AiOgD5hVQzNAVY8JK4qEfHMIKBnd2+BQlBINaiRtL/aV2rdzYBsM6CIONbI1NZENTr3RwdB2PlnJgJ6BRgA4hwu5Qg5iswAAAAASUVORK5CYII="/><element name="capLeft" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAYCAIAAAC0rgCNAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAD5JREFUeNosi8ENACAMAgnuv14H0Z8asI19XEjhOiKCMmibVgJTUt7V6fe9KXOtSQCfctJHu2q3/ot79hNgANc2OTz9uTCCAAAAAElFTkSuQmCC"/><element name="capRight" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAYCAIAAAC0rgCNAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAD5JREFUeNosi8ENACAMAgnuv14H0Z8asI19XEjhOiKCMmibVgJTUt7V6fe9KXOtSQCfctJHu2q3/ot79hNgANc2OTz9uTCCAAAAAElFTkSuQmCC"/><element name="divider" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAYCAIAAAC0rgCNAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAD5JREFUeNosi8ENACAMAgnuv14H0Z8asI19XEjhOiKCMmibVgJTUt7V6fe9KXOtSQCfctJHu2q3/ot79hNgANc2OTz9uTCCAAAAAElFTkSuQmCC"/><element name="playButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAEhJREFUeNpiYqABYBo1dNRQ+hr6H4jvA3E8NS39j4SpZvh/LJig4YxEGEqy3kET+w+AOGFQRhTJhrEQkGcczfujhg4CQwECDADpTRWU/B3wHQAAAABJRU5ErkJggg=="/><element name="pauseButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAChJREFUeNpiYBgFo2DwA0YC8v/R1P4nRu+ooaOGUtnQUTAKhgIACDAAFCwQCfAJ4gwAAAAASUVORK5CYII="/><element name="prevButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAEtJREFUeNpiYBgFo2Dog/9QDAPyQHweTYwiQ/2B+D0Wi8g2tB+JTdBQRiIMJVkvEy0iglhDF9Aq9uOpHVEwoE+NJDUKRsFgAAABBgDe2hqZcNNL0AAAAABJRU5ErkJggg=="/><element name="nextButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAElJREFUeNpiYBgFo2Dog/9AfB6I5dHE/lNqKAi/B2J/ahsKw/3EGMpIhKEk66WJoaR6fz61IyqemhEFSlL61ExSo2AUDAYAEGAAiG4hj+5t7M8AAAAASUVORK5CYII="/><element name="timeSliderRail" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAADxJREFUeNpiYBgFo2AU0Bwwzluw+D8tLWARFhKiqQ9YuLg4aWsBGxs7bS1gZ6e5BWyjSX0UjIKhDgACDABlYQOGh5pYywAAAABJRU5ErkJggg=="/><element name="timeSliderBuffer" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAD1JREFUeNpiYBgFo2AU0Bww1jc0/aelBSz8/Pw09QELOzs7bS1gY2OjrQWsrKy09gHraFIfBaNgqAOAAAMAvy0DChXHsZMAAAAASUVORK5CYII="/><element name="timeSliderProgress" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAClJREFUeNpiYBgFo2AU0BwwAvF/WlrARGsfjFow8BaMglEwCugAAAIMAOHfAQunR+XzAAAAAElFTkSuQmCC"/><element name="timeSliderThumb" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAAICAYAAAA870V8AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAABZJREFUeNpiZICA/yCCiQEJUJcDEGAAY0gBD1/m7Q0AAAAASUVORK5CYII="/><element name="muteButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAADFJREFUeNpiYBgFIw3MB+L/5Gj8j6yRiRTFyICJXHfTXyMLAXlGati4YDRFDj8AEGAABk8GSqqS4CoAAAAASUVORK5CYII="/><element name="unmuteButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAD1JREFUeNpiYBgFgxz8p7bm+cQa+h8LHy7GhEcjIz4bmAjYykiun/8j0fakGPIfTfPgiSr6aB4FVAcAAQYAWdwR1G1Wd2gAAAAASUVORK5CYII="/><element name="volumeSliderRail" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAYCAYAAADkgu3FAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAGpJREFUeNpi/P//PwM9ABMDncCoRYPfIqqDZcuW1UPp/6AUDcNM1DQYKtRAlaAj1mCSLSLXYIIWUctgDItoZfDA5aOoqKhGEANIM9LVR7SymGDQUctikuOIXkFNdhHEOFrDjlpEd4sAAgwAriRMub95fu8AAAAASUVORK5CYII="/><element name="volumeSliderProgress" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAYCAYAAADkgu3FAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAFtJREFUeNpi/P//PwM9ABMDncCoRYPfIlqAeij9H5SiYZiqBqPTlFqE02BKLSLaYFItIttgQhZRzWB8FjENiuRJ7aAbsMQwYMl7wDIsWUUQ42gNO2oR3S0CCDAAKhKq6MLLn8oAAAAASUVORK5CYII="/><element name="fullscreenButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAE5JREFUeNpiYBgFo2DQA0YC8v/xqP1PjDlMRDrEgUgxkgHIlfZoriVGjmzLsLFHAW2D6D8eA/9Tw7L/BAwgJE90PvhPpNgoGAVDEQAEGAAMdhTyXcPKcAAAAABJRU5ErkJggg=="/><element name="normalscreenButton" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAEZJREFUeNpiYBgFo2DIg/9UUkOUAf8JiFFsyX88fJyAkcQgYMQjNkzBoAgiezyRbE+tFGSPxQJ7auYBmma0UTAKBhgABBgAJAEY6zON61sAAAAASUVORK5CYII="/></elements></component><component name="display"><elements><element name="background" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAEpJREFUeNrszwENADAIA7DhX8ENoBMZ5KR10EryckCJiIiIiIiIiIiIiIiIiIiIiIh8GmkRERERERERERERERERERERERGRHSPAAPlXH1phYpYaAAAAAElFTkSuQmCC"/><element name="playIcon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAALdJREFUeNrs18ENgjAYhmFouDOCcQJGcARHgE10BDcgTOIosAGwQOuPwaQeuFRi2p/3Sb6EC5L3QCxZBgAAAOCorLW1zMn65TrlkH4NcV7QNcUQt7Gn7KIhxA+qNIR81spOGkL8oFJDyLJRdosqKDDkK+iX5+d7huzwM40xptMQMkjIOeRGo+VkEVvIPfTGIpKASfYIfT9iCHkHrBEzf4gcUQ56aEzuGK/mw0rHpy4AAACAf3kJMACBxjAQNRckhwAAAABJRU5ErkJggg=="/><element name="muteIcon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAHJJREFUeNrs1jEOgCAMBVAg7t5/8qaoIy4uoobyXsLCxA+0NCUAAADGUWvdQoQ41x4ixNBB2hBvBskdD3w5ZCkl3+33VqI0kjBBlh9rp+uTcyOP33TnolfsU85XX3yIRpQph8ZQY3wTZtU5AACASA4BBgDHoVuY1/fvOQAAAABJRU5ErkJggg=="/><element name="errorIcon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAWlJREFUeNrsl+1twjAQhsHq/7BBYQLYIBmBDcoGMAIjtBPQTcII2SDtBDBBwrU6pGsUO7YbO470PtKJkz9iH++d4ywWAAAAAABgljRNsyWr2bZzDuJG1rLdZhcMbTjrBCGDyUKsqQLFciJb9bSvuG/WagRVRUVUI6gqy5HVeKWfSgRyJruKIU//TrZTSn2nmlaXThrloi/v9F2STC1W4+Aw5cBzkquRc09bofFNc6YLxEON0VUZS5FPTftO49vMjRsIF3RhOGr7/D/pJw+FKU+q0vDyq8W42jCunDqI3LC5XxNj2wHLU1XjaRnb0Lhykhqhhd8MtSF5J9tbjCv4mXGvKJz/65FF/qJryyaaIvzP2QRxZTX2nTuXjvV/VPFSwyLnW7mpH99yTh1FEVro6JBSd40/pMrRdV8vPtcKl28T2pT8TnFZ4yNosct3Q0io6JfBiz1FlGdqVQH3VHnepAEAAAAAADDzEGAAcTwB10jWgxcAAAAASUVORK5CYII="/><element name="bufferIcon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAuhJREFUeNrsWr9rU1EUznuNGqvFQh1ULOhiBx0KDtIuioO4pJuik3FxFfUPaAV1FTdx0Q5d2g4FFxehTnEpZHFoBy20tCIWtGq0TZP4HfkeHB5N8m6Sl/sa74XDybvv3vvOd8/Pe4lXrVZT3dD8VJc0B8QBcUAcEAfESktHGeR5XtMfqFQq/f92zPe/NbtGlKTdCY30kuxrpMGO94BlQCXs+rbh3ONgA6BlzP1p20d80gEI5hmA2A92Qua1Q2PtAFISM+bvjMG8U+Q7oA3rQGASwrYCU6WpNdLGYbA+Pq5jjXIiwi8EEa2UDbQSaKOIuV+SlkcCrfjY8XTI9EpKGwP0C2kru2hLtHqa4zoXtZRWyvi4CLwv9Opr6Hkn6A9HKgEANsQ1iqC3Ub/vRUk2JgmRkatK36kVrnt0qObunwUdUUMXMWYpakJsO5Am8tAw2GBIgwWA+G2S2dMpiw0gDioQRQJoKhRb1QiDwlHZUABYbaXWsm5ae6loTE4ZDxN4CZar8foVzOJ2iyZ2kWF3t7YIevffaMT5yJ70kQb2fQ1sE5SHr2wazs2wgMxgbsEKEAgxAvZUJbQLBGTSBMgNrncJbA6AljtS/eKDJ0Ez+DmrQEzXS2h1Ck25kAg0IZcUOaydCy4sYnN2fOA+2AP16gNoHALlQ+fwH7XO4CxLenUpgj4xr6ugY2roPMbMx+Xs18m/E8CVEIhxsNeg83XWOAN6grG3lGbk8uE5fr4B/WH3cJw+co/l9nTYsSGYCJ/lY5/qv0thn6nrIWmjeJcPSnWOeY++AkF8tpJHIMAUs/MaBBpj3znZfQo5psY+ZrG4gv5HickjEOymKjEeRpgyST6IuZcTcWbnjcgdPi5ghxciRKsl1lDSsgwA1i8fssonJgzmTSqfGUkCENndNdAL7PS6QQ7ZYISTo+1qq0LEWjTWcvY4isa4z+yfQB+7ooyHVg5RI7/i1Ijn/vnggDggDogD4oC00P4KMACd/juEHOrS4AAAAABJRU5ErkJggg=="/></elements></component><component name="dock"><elements><element name="button" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAFBJREFUeNrs0cEJACAQA8Eofu0fu/W6EM5ZSAFDRpKTBs00CQQEBAQEBAQEBAQEBAQEBATkK8iqbY+AgICAgICAgICAgICAgICAgIC86QowAG5PAQzEJ0lKAAAAAElFTkSuQmCC"/></elements></component><component name="playlist"><elements><element name="item" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAIAAAC1nk4lAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAHhJREFUeNrs2NEJwCAMBcBYuv/CFuIE9VN47WWCR7iocXR3pdWdGPqqwIoMjYfQeAiNh9B4JHc6MHQVHnjggQceeOCBBx77TifyeOY0iHi8DqIdEY8dD5cL094eePzINB5CO/LwcOTptNB4CP25L4TIbZzpU7UEGAA5wz1uF5rF9AAAAABJRU5ErkJggg=="/><element name="sliderRail" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAA8CAIAAADpFA0BAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAADhJREFUeNrsy6ENACAMAMHClp2wYxZLAg5Fcu9e3OjuOKqqfTMzbs14CIZhGIZhGIZhGP4VLwEGAK/BBnVFpB0oAAAAAElFTkSuQmCC"/><element name="sliderThumb" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAA8CAIAAADpFA0BAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAADRJREFUeNrsy7ENACAMBLE8++8caFFKKiRffU53112SGs3ttOohGIZhGIZhGIZh+Fe8BRgAiaUGde6NOSEAAAAASUVORK5CYII="/></elements></component></components></skin>';

})(jQuery);
/**
 * JW Player view component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-11
 */
(function($) {
	var logoDefaults = {
		prefix: "http://l.longtailvideo.com/html5/0/",
		file: "logo.png",
		link: "http://www.longtailvideo.com/players/jw-flv-player/",
		margin: 8,
		out: 0.5,
		over: 1,
		timeout: 3,
		hide: "true",
		position: "bottom-left",
		width: 93,
		height: 30
	};

	var displays = {};

	$.fn.jwplayerDisplay = function(player, domelement) {
		if (displays[player.id] === undefined) {
			displays[player.id] = {};
			displays[player.id].domelement = domelement;
			displays[player.id].elements = initializeDisplayElements(player);
			if ($.fn.jwplayerUtils.isiPhone()) {
				domelement.attr('poster', $.fn.jwplayerUtils.getAbsolutePath(player.config.image));
			} else {
				setupDisplay(player);
				player.state(stateHandler);
				player.mute(stateHandler);
				player.error(function(obj) {

				});
			}
		}
	};

	function setupDisplay(player) {
		var meta = player.meta();
		var html = [];
		html.push("<div id='" + player.id + "_display'" + getStyle(player, 'display') + ">");
		html.push("<div id='" + player.id + "_displayImage'" + getStyle(player, 'displayImage') + ">&nbsp;</div>");
		html.push("<div id='" + player.id + "_displayIconBackground'" + getStyle(player, 'displayIconBackground') + ">");
		html.push("<img id='" + player.id + "_displayIcon' src='" + player.skin.display.elements.playIcon.src + "' alt='Click to play video'" + getStyle(player, 'displayIcon') + "/>");
		html.push('</div>');
		html.push('<div id="' + player.id + '_logo" target="_blank"' + getStyle(player, 'logo') + '>&nbsp;</div>');
		html.push('</div>');
		displays[player.id].domelement.before(html.join(''));
		setupDisplayElements(player);
	}

	function getStyle(player, element) {
		var result = '';
		for (var style in displays[player.id].elements[element].style) {
			result += style + ":" + displays[player.id].elements[element].style[style] + ";";
		}
		if (result === '') {
			return ' ';
		}
		return ' style="' + result + '" ';
	}

	function setupDisplayElements(player) {
		var displayElements = initializeDisplayElements(player);
		for (var element in displayElements) {
			var elementId = ['#', player.id, '_', element];
			displays[player.id][element] = $(elementId.join(''));
			if (displayElements[element].click !== undefined) {
				displays[player.id][element].click(displayElements[element].click);
			}
		}
	}

	function initializeDisplayElements(player) {
		var meta = player.meta();
		var elements = {
			display: {
				style: {
					cursor: 'pointer',
					width: meta.width + "px",
					height: meta.height + "px",
					position: 'relative',
					'z-index': 50,
					margin: 0,
					padding: 0
				},
				click: displayClickHandler(player)
			},
			displayIcon: {
				style: {
					cursor: 'pointer',
					position: 'absolute',
					top: ((player.skin.display.elements.background.height - player.skin.display.elements.playIcon.height) / 2) + "px",
					left: ((player.skin.display.elements.background.width - player.skin.display.elements.playIcon.width) / 2) + "px",
					border: 0,
					margin: 0,
					padding: 0
				}
			},
			displayIconBackground: {
				style: {
					cursor: 'pointer',
					position: 'absolute',
					top: ((meta.height - player.skin.display.elements.background.height) / 2) + "px",
					left: ((meta.width - player.skin.display.elements.background.width) / 2) + "px",
					border: 0,
					'background-image': (['url(', player.skin.display.elements.background.src, ')']).join(''),
					width: player.skin.display.elements.background.width + "px",
					height: player.skin.display.elements.background.height + "px",
					margin: 0,
					padding: 0
				}
			},
			displayImage: {
				style: {
					display: 'block',
					background: ([player.config.screencolor, ' url(', $.fn.jwplayerUtils.getAbsolutePath(player.config.image), ') no-repeat center center']).join(''),
					width: meta.width + "px",
					height: meta.height + "px",
					position: 'absolute',
					cursor: 'pointer',
					left: 0,
					top: 0,
					margin: 0,
					padding: 0,
					'text-decoration': 'none'
				}
			},
			logo: {
				style: {
					position: 'absolute',
					width: logoDefaults.width + "px",
					height: logoDefaults.height + "px",
					'background-image': (['url(', logoDefaults.prefix, logoDefaults.file, ')']).join(''),
					margin: 0,
					padding: 0,
					display: 'none',
					'text-decoration': 'none'
				},
				click: logoClickHandler()
			}
		};
		var positions = logoDefaults.position.split("-");
		for (var position in positions) {
			elements.logo.style[positions[position]] = logoDefaults.margin + "px";
		}
		return elements;
	}

	function displayClickHandler(player) {
		return function(evt) {
			if (player.media === undefined) {
				document.location.href = $.fn.jwplayerUtils.getAbsolutePath(player.meta().sources[player.meta().source].file);
				return;
			}
			if (typeof evt.preventDefault != 'undefined') {
				evt.preventDefault(); // W3C
			} else {
				evt.returnValue = false; // IE
			}
			if (player.model.state != $.fn.jwplayer.states.PLAYING) {
				player.play();
			} else {
				player.pause();
			}
		};
	}

	function logoClickHandler() {
		return function(evt) {
			evt.stopPropagation();
			return;
		};
	}

	function setIcon(player, path) {
		$("#" + player.id + "_displayIcon")[0].src = path;
	}

	function animate(element, state) {
		var speed = 'slow';
		if (!displays[player.id].animate) {
			return;
		}
		if (state) {
			element.slideDown(speed, function() {
				animate(element);
			});
		} else {
			element.slideUp(speed, function() {
				animate(element, true);
			});
		}
	}


	function stateHandler(obj) {
		player = $.jwplayer(obj.id);
		displays[player.id].animate = false;
		switch (player.model.state) {
			case $.fn.jwplayer.states.BUFFERING:
				displays[obj.id].logo.fadeIn(0, function() {
					setTimeout(function() {
						displays[obj.id].logo.fadeOut(logoDefaults.out * 1000);
					}, logoDefaults.timeout * 1000);
				});
				displays[obj.id].displayIcon[0].src = player.skin.display.elements.bufferIcon.src;
				displays[obj.id].displayIcon.css({
					"display": "block",
					top: (player.skin.display.elements.background.height - player.skin.display.elements.bufferIcon.height) / 2 + "px",
					left: (player.skin.display.elements.background.width - player.skin.display.elements.bufferIcon.width) / 2 + "px"
				});
				displays[player.id].animate = true;
				// TODO: Buffer Icon rotation
				if (false) {
					animate(displays[obj.id].displayIconBackground);
				}
				displays[obj.id].displayIconBackground.css('display', 'none');
				break;
			case $.fn.jwplayer.states.PAUSED:
				displays[obj.id].logo.fadeIn(0);
				displays[obj.id].displayImage.css("background", "transparent no-repeat center center");
				displays[obj.id].displayIconBackground.css("display", "block");
				displays[obj.id].displayIcon[0].src = player.skin.display.elements.playIcon.src;
				displays[obj.id].displayIcon.css({
					"display": "block",
					top: (player.skin.display.elements.background.height - player.skin.display.elements.playIcon.height) / 2 + "px",
					left: (player.skin.display.elements.background.width - player.skin.display.elements.playIcon.width) / 2 + "px"
				});
				break;
			case $.fn.jwplayer.states.IDLE:
				displays[obj.id].logo.fadeOut(0);
				displays[obj.id].displayImage.css("background", "#ffffff url('" + $.fn.jwplayerUtils.getAbsolutePath(player.config.image) + "') no-repeat center center");
				displays[obj.id].displayIconBackground.css("display", "block");
				displays[obj.id].displayIcon[0].src = player.skin.display.elements.playIcon.src;
				displays[obj.id].displayIcon.css({
					"display": "block",
					top: (player.skin.display.elements.background.height - player.skin.display.elements.playIcon.height) / 2 + "px",
					left: (player.skin.display.elements.background.width - player.skin.display.elements.playIcon.width) / 2 + "px"
				});
				break;
			default:
				if (player.mute()) {
					displays[obj.id].displayImage.css("background", "transparent no-repeat center center");
					displays[obj.id].displayIconBackground.css("display", "block");
					displays[obj.id].displayIcon[0].src = player.skin.display.elements.muteIcon.src;
					displays[obj.id].displayIcon.css({
						"display": "block",
						top: (player.skin.display.elements.muteIcon.height - player.skin.display.elements.muteIcon.height) / 2 + "px",
						left: (player.skin.display.elements.background.width - player.skin.display.elements.muteIcon.width) / 2 + "px"
					});
				} else {
					try {
						displays[obj.id].logo.clearQueue();
					} catch (err) {

					}
					displays[obj.id].logo.fadeIn(0, function() {
						setTimeout(function() {
							displays[obj.id].logo.fadeOut(logoDefaults.out * 1000);
						}, logoDefaults.timeout * 1000);
					});
					displays[obj.id].displayImage.css("background", "transparent no-repeat center center");
					displays[obj.id].displayIconBackground.css("display", "none");
					displays[obj.id].displayIcon.css("display", "none");
				}
				break;
		}
	}

})(jQuery);
/**
 * JW Player Flash Media component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-12
 */
(function($) {

	var controllerEvents = {
		ERROR: $.fn.jwplayer.events.JWPLAYER_ERROR,
		ITEM: "ITEM",
		MUTE: $.fn.jwplayer.events.JWPLAYER_MEDIA_MUTE,
		PLAY: "PLAY",
		PLAYLIST: "PLAYLIST",
		RESIZE: $.fn.jwplayer.events.JWPLAYER_RESIZE,
		SEEK: "SEEK",
		STOP: "STOP",
		VOLUME: $.fn.jwplayer.events.JWPLAYER_MEDIA_VOLUME
	};

	var modelEvents = {
		BUFFER: $.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER,
		ERROR: $.fn.jwplayer.events.JWPLAYER_MEDIA_ERROR,
		LOADED: $.fn.jwplayer.events.JWPLAYER_MEDIA_LOADED,
		META: $.fn.jwplayer.events.JWPLAYER_MEDIA_META,
		STATE: $.fn.jwplayer.events.JWPLAYER_PLAYER_STATE,
		TIME: $.fn.jwplayer.events.JWPLAYER_MEDIA_TIME
	};

	var viewEvents = {
		FULLSCREEN: "FULLSCREEN",
		ITEM: "ITEM",
		LINK: "LINK",
		LOAD: "LOAD",
		MUTE: "MUTE",
		NEXT: "NEXT",
		PLAY: "PLAY",
		PREV: "PREV",
		REDRAW: "REDRAW",
		SEEK: "SEEK",
		STOP: "STOP",
		TRACE: "TRACE",
		VOLUME: "VOLUME"
	};


	$.fn.jwplayerMediaFlash = function(player) {
		var options = {};
		var media = {
			play: play(player),
			pause: pause(player),
			seek: seek(player),
			volume: volume(player),
			mute: mute(player),
			fullscreen: fullscreen(player),
			load: load(player),
			resize: resize(player),
			state: $.fn.jwplayer.states.IDLE,
			hasChrome: true

		};
		player.media = media;
		$.fn.jwplayerView.embedFlash(player, options);
	};

	function stateHandler(event, player) {
		player.model.state = event.newstate;
		player.sendEvent($.fn.jwplayer.events.JWPLAYER_PLAYER_STATE, {
			oldstate: event.oldstate,
			newstate: event.newstate
		});
	}


	function addEventListeners(player) {
		if (player.model.domelement[0].addControllerListener === undefined) {
			setTimeout(function() {
				addEventListeners(player);
			}, 100);
			return;
		}
		$.fn.jwplayerMediaFlash.forwarders[player.id] = {};
		var video = $("#" + player.id);
		for (var controllerEvent in controllerEvents) {
			$.fn.jwplayerMediaFlash.forwarders[player.id][controllerEvents[controllerEvent]] = forwardFactory(controllerEvents[controllerEvent], player);
			video[0].addControllerListener(controllerEvent, "$.fn.jwplayerMediaFlash.forwarders." + player.id + "." + controllerEvents[controllerEvent]);
		}
		for (var modelEvent in modelEvents) {
			$.fn.jwplayerMediaFlash.forwarders[player.id][modelEvents[modelEvent]] = forwardFactory(modelEvents[modelEvent], player);
			video[0].addModelListener(modelEvent, "$.fn.jwplayerMediaFlash.forwarders." + player.id + "." + modelEvents[modelEvent]);
		}
		$.fn.jwplayerMediaFlash.forwarders[player.id][viewEvents.MUTE] = forwardFactory(viewEvents.MUTE, player);
		video[0].addViewListener(viewEvents.MUTE, "$.fn.jwplayerMediaFlash.forwarders." + player.id + "." + viewEvents.MUTE);

	}

	function forwardFactory(type, player) {
		return function(event) {
			forward(event, type, player);
		};
	}

	$.fn.jwplayerMediaFlash.playerReady = function(evt) {
		addEventListeners($.jwplayer(evt.id));
	};

	$.fn.jwplayerMediaFlash.forwarders = {};

	function forward(event, type, player) {
		switch (type) {
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_META:
				player.sendEvent(type, event);
				break;
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_MUTE:
				player.model.mute = event.state;
				event.mute = event.state;
				player.sendEvent(type, event);
				break;
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_VOLUME:
				player.model.volume = event.percentage;
				event.volume = event.percentage;
				player.sendEvent(type, event);
				break;
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_RESIZE:
				player.model.fullscreen = event.fullscreen;
				player.model.height = event.height;
				player.model.width = event.width;
				player.sendEvent(type, event);
				break;
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_TIME:
				if (player.model.duration === 0) {
					player.model.duration = event.duration;
				}
				player.model.position = event.position;
				player.sendEvent(type, event);
				break;
			case $.fn.jwplayer.events.JWPLAYER_PLAYER_STATE:
				if (event.newstate == "COMPLETED") {
					player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_COMPLETE, event);
				} else {
					stateHandler(event, player);
				}
				break;
			case $.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER:
				event.bufferPercent = event.percentage;
				player.model.buffer = event.percentage;
				player.sendEvent(type, event);
				break;
			default:
				player.sendEvent(type, event);
				break;
		}
	}

	function play(player) {
		return function() {
			player.model.domelement[0].sendEvent("PLAY", true);
		};
	}

	/** Switch the pause state of the player. **/
	function pause(player) {
		return function() {
			player.model.domelement[0].sendEvent("PLAY", false);
		};
	}


	/** Seek to a position in the video. **/
	function seek(player) {
		return function(position) {
			player.model.domelement[0].sendEvent("SEEK", position);
		};
	}


	/** Stop playback and loading of the video. **/
	function stop(player) {
		return function() {
			player.model.domelement[0].sendEvent("STOP");
		};
	}


	/** Change the video's volume level. **/
	function volume(player) {
		return function(position) {
			player.model.domelement[0].sendEvent("VOLUME", position);
		};
	}

	/** Switch the mute state of the player. **/
	function mute(player) {
		return function(state) {
			if (((player.model.domelement[0].getConfig().mute === true) && (state === false)) || state) {
				player.model.domelement[0].sendEvent("MUTE", state);
			}
		};
	}

	/** Switch the fullscreen state of the player. **/
	function fullscreen(player) {
		return function(state) {
			player.model.fullscreen = state;
			$.fn.jwplayerUtils.log("Fullscreen does not work for Flash media.");
		};
	}

	/** Load a new video into the player. **/
	function load(player) {
		return function(path) {
			path = $.fn.jwplayerUtils.getAbsolutePath(path);
			player.model.domelement[0].sendEvent("LOAD", path);
			player.model.domelement[0].sendEvent("PLAY");
		};
	}

	/** Resizes the video **/
	function resize(player) {
		return function(width, height) {
			player.model.width = width;
			player.model.height = height;
			player.css("width", width);
			player.css("height", height);
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_RESIZE, {
				width: width,
				hieght: height
			});
		};
	}

})(jQuery);
/**
 * JW Player Video Media component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-12
 */
(function($) {
	var states = {
		"ended": $.fn.jwplayer.states.IDLE,
		"playing": $.fn.jwplayer.states.PLAYING,
		"pause": $.fn.jwplayer.states.PAUSED,
		"buffering": $.fn.jwplayer.states.BUFFERING
	};

	var events = {
		'abort': generalHandler,
		'canplay': stateHandler,
		'canplaythrough': stateHandler,
		'durationchange': metaHandler,
		'emptied': generalHandler,
		'ended': stateHandler,
		'error': errorHandler,
		'loadeddata': metaHandler,
		'loadedmetadata': metaHandler,
		'loadstart': stateHandler,
		'pause': stateHandler,
		'play': positionHandler,
		'playing': stateHandler,
		'progress': progressHandler,
		'ratechange': generalHandler,
		'seeked': stateHandler,
		'seeking': stateHandler,
		'stalled': stateHandler,
		'suspend': stateHandler,
		'timeupdate': positionHandler,
		'volumechange': generalHandler,
		'waiting': stateHandler,
		'canshowcurrentframe': generalHandler,
		'dataunavailable': generalHandler,
		'empty': generalHandler,
		'load': generalHandler,
		'loadedfirstframe': generalHandler
	};


	$.fn.jwplayerMediaVideo = function(player) {
		player.model.domelement.attr('loop', player.config.repeat);
		var media = {
			play: play(player),
			pause: pause(player),
			seek: seek(player),
			stop: stop(player),
			volume: volume(player),
			mute: mute(player),
			fullscreen: fullscreen(player),
			load: load(player),
			resize: resize(player),
			state: $.fn.jwplayer.states.IDLE,
			interval: null,
			loadcount: 0,
			hasChrome: false
		};
		player.media = media;
		media.mute(player.mute());
		media.volume(player.volume());
		$.each(events, function(event, handler) {
			player.model.domelement[0].addEventListener(event, function(event) {
				handler(event, player);
			}, true);
		});
	};

	function generalHandler(event, player) {
	}

	function stateHandler(event, player) {
		if (states[event.type]) {
			setState(player, states[event.type]);
		}
	}

	function setState(player, newstate) {
		if (player.media.stopped) {
			newstate = $.fn.jwplayer.states.IDLE;
		}
		if (player.model.state != newstate) {
			var oldstate = player.model.state;
			player.media.state = newstate;
			player.model.state = newstate;
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_PLAYER_STATE, {
				oldstate: oldstate,
				newstate: newstate
			});
		}
		if (newstate == $.fn.jwplayer.states.IDLE) {
			clearInterval(player.media.interval);
			player.media.interval = null;
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_COMPLETE);
			if (player.config.repeat && !player.media.stopped) {
				player.play();
			}
			if (player.model.domelement.css('display') != 'none') {
				player.model.domelement.css('display', 'none');
			}
		}
		player.media.stopped = false;
	}

	function metaHandler(event, player) {
		var meta = {
			height: event.target.videoHeight,
			width: event.target.videoWidth,
			duration: event.target.duration
		};
		if (player.model.duration === 0) {
			player.model.duration = event.target.duration;
		}
		player.model.sources[player.model.source] = $.extend(player.model.sources[player.model.source], meta);
		player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_META, meta);
	}

	function positionHandler(event, player) {
		if (player.media.stopped) {
			return;
		}
		if (!$.fn.jwplayerUtils.isNull(event.target)) {
			if (player.model.duration === 0) {
				player.model.duration = event.target.duration;
			}

			if (player.media.state == $.fn.jwplayer.states.PLAYING) {
				player.model.position = Math.round(event.target.currentTime * 10) / 10;
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_TIME, {
					position: Math.round(event.target.currentTime * 10) / 10,
					duration: Math.round(event.target.duration * 10) / 10
				});
			}
		}
		progressHandler({}, player);
	}

	function progressHandler(event, player) {
		var bufferPercent, bufferTime, bufferFill;
		if (!isNaN(event.loaded / event.total)) {
			bufferPercent = event.loaded / event.total * 100;
			bufferTime = bufferPercent / 100 * (player.model.duration - player.model.domelement[0].currentTime);
		} else if ((player.model.domelement[0].buffered !== undefined) && (player.model.domelement[0].buffered.length > 0)) {
			maxBufferIndex = 0;
			if (maxBufferIndex >= 0) {
				bufferPercent = player.model.domelement[0].buffered.end(maxBufferIndex) / player.model.domelement[0].duration * 100;
				bufferTime = player.model.domelement[0].buffered.end(maxBufferIndex) - player.model.domelement[0].currentTime;
			}
		}

		bufferFill = bufferTime / player.model.config.bufferlength * 100;

		// TODO: Buffer underrun
		if (false) {
			if (bufferFill < 25 && player.media.state == $.fn.jwplayer.states.PLAYING) {
				setState($.fn.jwplayer.states.BUFFERING);
				player.media.bufferFull = false;
				if (!player.model.domelement[0].seeking) {
					player.model.domelement[0].pause();
				}
			} else if (bufferFill > 95 && player.media.state == $.fn.jwplayer.states.BUFFERING && player.media.bufferFull === false && bufferTime > 0) {
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER_FULL, {});
			}
		}

		if (player.media.bufferFull === false) {
			player.media.bufferFull = true;
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER_FULL, {});
		}

		if (!player.media.bufferingComplete) {
			if (bufferPercent == 100 && player.media.bufferingComplete === false) {
				player.media.bufferingComplete = true;
			}

			if (!$.fn.jwplayerUtils.isNull(bufferPercent)) {
				player.model.buffer = Math.round(bufferPercent);
				player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_BUFFER, {
					bufferPercent: Math.round(bufferPercent)
					//bufferingComplete: player.media.bufferingComplete,
					//bufferFull: player.media.bufferFull,
					//bufferFill: bufferFill,
					//bufferTime: bufferTime
				});
			}

		}
	}

	function startInterval(player) {
		if (player.media.interval === null) {
			player.media.interval = window.setInterval(function() {
				positionHandler({}, player);
			}, 100);
		}
	}


	function errorHandler(event, player) {
		player.sendEvent($.fn.jwplayer.events.JWPLAYER_ERROR, {});
	}

	function play(player) {
		return function() {
			if (player.media.state != $.fn.jwplayer.states.PLAYING) {
				setState(player, $.fn.jwplayer.states.PLAYING);
				player.model.domelement[0].play();
			}
		};
	}

	/** Switch the pause state of the player. **/
	function pause(player) {
		return function() {
			player.model.domelement[0].pause();
		};
	}


	/** Seek to a position in the video. **/
	function seek(player) {
		return function(position) {
			player.model.domelement[0].currentTime = position;
			player.model.domelement[0].play();
		};
	}


	/** Stop playback and loading of the video. **/
	function stop(player) {
		return function() {
			player.media.stopped = true;
			player.model.domelement[0].pause();
			clearInterval(player.media.interval);
			player.media.interval = undefined;
			player.model.position = 0;
		};
	}


	/** Change the video's volume level. **/
	function volume(player) {
		return function(position) {
			player.model.volume = position;
			player.model.domelement[0].volume = position / 100;
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_VOLUME, {
				volume: Math.round(player.model.domelement[0].volume * 100)
			});
		};
	}

	/** Switch the mute state of the player. **/
	function mute(player) {
		return function(state) {
			player.model.mute = state;
			player.model.domelement[0].muted = state;
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_MUTE, {
				mute: player.model.domelement[0].muted
			});
		};
	}

	/** Resize the player. **/
	function resize(player) {
		return function(width, height) {
			// TODO: Fullscreen
			if (false) {
				$("#" + player.id + "_jwplayer").css("position", 'fixed');
				$("#" + player.id + "_jwplayer").css("top", '0');
				$("#" + player.id + "_jwplayer").css("left", '0');
				$("#" + player.id + "_jwplayer").css("width", width);
				$("#" + player.id + "_jwplayer").css("height", height);
				player.model.width = $("#" + player.id + "_jwplayer").width;
				player.model.height = $("#" + player.id + "_jwplayer").height;
			}
			player.sendEvent($.fn.jwplayer.events.JWPLAYER_MEDIA_RESIZE, {
				fullscreen: player.model.fullscreen,
				width: width,
				hieght: height
			});
		};
	}

	/** Switch the fullscreen state of the player. **/
	function fullscreen(player) {
		return function(state) {
			player.model.fullscreen = state;
			if (state === true) {
				player.resize("100%", "100%");
			} else {
				player.resize(player.model.config.width, player.model.config.height);
			}
		};
	}

	/** Load a new video into the player. **/
	function load(player) {
		return function(path) {
			if (player.model.domelement.css('display') == 'none') {
				player.model.domelement.css('display', 'block');
			}

			setTimeout(function() {
				path = $.fn.jwplayerUtils.getAbsolutePath(path);
				if (path == player.model.domelement[0].src && player.media.loadcount > 0) {
					player.model.position = 0;
					player.model.domelement[0].currentTime = 0;
					setState(player, $.fn.jwplayer.states.BUFFERING);
					setState(player, $.fn.jwplayer.states.PLAYING);
					if (player.model.domelement[0].paused) {
						player.model.domelement[0].play();
					}
					return;
				} else if (path != player.model.domelement[0].src) {
					player.media.loadcount = 0;
				}
				player.media.loadcount++;
				player.media.bufferFull = false;
				player.media.bufferingComplete = false;
				setState(player, $.fn.jwplayer.states.BUFFERING);
				player.model.domelement[0].src = path;
				player.model.domelement[0].load();
				startInterval(player);
				try {
					player.model.domelement[0].currentTime = 0;
				} catch (err){

				}
			}, 25);
		};
	}

})(jQuery);
/**
 * JW Player model component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-11
 */
(function($) {
	var jwplayerid = 1;

	var modelParams = {
		volume: 100,
		fullscreen: false,
		mute: false,
		start: 0,
		width: 480,
		height: 320,
		duration: 0
	};

	function createModel() {
		return {
			sources: {},
			state: $.fn.jwplayer.states.IDLE,
			source: 0,
			buffer: 0
		};
	}


	$.fn.jwplayerModel = function(domElement, options) {
		var model = createModel();
		model.config = $.extend(true, {}, $.fn.jwplayer.defaults, $.fn.jwplayerParse(domElement[0]), options);
		if ($.fn.jwplayerUtils.isNull(model.config.id)) {
			model.config.id = "jwplayer_" + jwplayerid++;
		}
		model.sources = model.config.sources;
		delete model.config.sources;
		model.domelement = domElement;
		for (var modelParam in modelParams) {
			if (!$.fn.jwplayerUtils.isNull(model.config[modelParam])) {
				model[modelParam] = model.config[modelParam];
			} else {
				model[modelParam] = modelParams[modelParam];
			}
		}
		//model = $.extend(true, {}, , model);
		return model;
	};

	$.fn.jwplayerModel.setActiveMediaProvider = function(player) {
		var source, sourceIndex;
		for (sourceIndex in player.model.sources) {
			source = player.model.sources[sourceIndex];
			if (source.type === undefined) {
				var extension = $.fn.jwplayerUtils.extension(source.file);
				if (extension == "ogv") {
					extension = "ogg";
				}
				source.type = 'video/' + extension + ';';
			}
			if ($.fn.jwplayerUtils.supportsType(source.type)) {
				player.model.source = sourceIndex;
				$.fn.jwplayerMediaVideo(player);
				return true;
			}
		}
		if ($.fn.jwplayerUtils.supportsFlash && player.state != $.fn.jwplayer.states.PLAYING) {
			for (sourceIndex in player.model.sources) {
				source = player.model.sources[sourceIndex];
				if ($.fn.jwplayerUtils.flashCanPlay(source.file)) {
					player.model.source = sourceIndex;
					$.fn.jwplayerMediaFlash(player);
					return true;
				}
			}
		}
		return false;
	};

})(jQuery);
/**
 * Parser for the JW Player.
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	var elementAttributes = {
		element: {
			width: 'width',
			height: 'height',
			id: 'id',
			'class': 'className',
			name: 'name'
		},
		media: {
			src: 'file',
			preload: 'preload',
			autoplay: 'autostart',
			loop: 'repeat',
			controls: 'controls'
		},
		source: {
			src: 'file',
			type: 'type',
			media: 'media'
		},
		video: {
			poster: 'image'
		}
	};

	var parsers = {};

	$.fn.jwplayerParse = function(player) {
		return parseElement(player);
	};

	function getAttributeList(elementType, attributes) {
		if (attributes === undefined) {
			attributes = elementAttributes[elementType];
		} else {
			$.extend(attributes, elementAttributes[elementType]);
		}
		return attributes;
	}

	function parseElement(domElement, attributes) {
		if (parsers[domElement.tagName.toLowerCase()] && (attributes === undefined)) {
			return parsers[domElement.tagName.toLowerCase()](domElement);
		} else {
			attributes = getAttributeList('element', attributes);
			var configuration = {};
			for (var attribute in attributes) {
				if (attribute != "length") {
					var value = $(domElement).attr(attribute);
					if (!(value === "" || value === undefined)) {
						configuration[attributes[attribute]] = $(domElement).attr(attribute);
					}
				}
			}
			configuration.screencolor = (($(domElement).css("background-color") == "transparent") || ($(domElement).css("background-color") == "rgba(0, 0, 0, 0)")) ? "black" : $(domElement).css("background-color");
			configuration.plugins = {};
			return configuration;
		}
	}

	function parseMediaElement(domElement, attributes) {
		attributes = getAttributeList('media', attributes);
		var sources = [];
		if (!(navigator.plugins && navigator.mimeTypes && navigator.mimeTypes.length)){
			var currentElement = $(domElement).next();
			if (currentElement[0] !== undefined){
				while(currentElement[0].tagName.toLowerCase() == "source") {
					sources[sources.length] = parseSourceElement(currentElement[0]);
					currentElement = currentElement.next();
				}
			}
		} else {
			$("source", domElement).each(function() {
				sources[sources.length] = parseSourceElement(this);
			});
		}
		var configuration = parseElement(domElement, attributes);
		if (configuration.file !== undefined) {
			sources[0] = {
				'file': configuration.file
			};
		}
		if (!$.fn.jwplayerUtils.isiPhone()) {
			domElement.removeAttribute('src');
		}
		configuration.sources = sources;
		return configuration;
	}

	function parseSourceElement(domElement, attributes) {
		attributes = getAttributeList('source', attributes);
		return parseElement(domElement, attributes);
	}

	function parseVideoElement(domElement, attributes) {
		attributes = getAttributeList('video', attributes);
		var result = parseMediaElement(domElement, attributes);
		if (!$.fn.jwplayerUtils.isiPhone() && !$.fn.jwplayerUtils.isiPad()) {
			try {
				$(domElement)[0].removeAttribute('poster');
			} catch (err) {

			}
		}
		return result;
	}

	parsers.media = parseMediaElement;
	parsers.audio = parseMediaElement;
	parsers.source = parseSourceElement;
	parsers.video = parseVideoElement;


})(jQuery);
/**
 * JW Player component that loads / interfaces PNG skinning.
 *
 * @author jeroen
 * @version 1.0alpha
 * @lastmodifiedauthor zach
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	var players = {};

	/** Constructor **/
	$.fn.jwplayerSkinner = function(player, completeHandler) {
		players[player.id] = {
			completeHandler: completeHandler
		};
		load(player);
	};

	/** Load the skin **/
	function load(player) {
		$.ajax({
			url: $.fn.jwplayerUtils.getAbsolutePath(player.model.config.skin),
			complete: function(xmlrequest, textStatus) {
				if (textStatus == "success") {
					loadSkin(player, xmlrequest.responseXML);
				} else {
					loadSkin(player, $.fn.jwplayerDefaultSkin);
				}
			}

		});
	}

	function loadSkin(player, xml) {
		var skin = {
			properties: {}
		};
		player.skin = skin;
		var components = $('component', xml);
		if (components.length === 0) {
			return;
		}
		for (var componentIndex = 0; componentIndex < components.length; componentIndex++) {
			players[player.id].loading = true;

			var componentName = $(components[componentIndex]).attr('name');
			var component = {
				settings: {},
				elements: {}
			};
			player.skin[componentName] = component;
			var elements = $(components[componentIndex]).find('element');
			for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {
				loadImage(elements[elementIndex], componentName, player);
			}
			var settings = $(components[componentIndex]).find('setting');
			for (var settingIndex = 0; settingIndex < settings.length; settingIndex++) {
				player.skin[componentName].settings[$(settings[settingIndex]).attr("name")] = $(settings[settingIndex]).attr("value");
			}

			players[player.id].loading = false;

			resetCompleteIntervalTest(player);
		}
	}

	function resetCompleteIntervalTest(player) {
		clearInterval(players[player.id].completeInterval);
		players[player.id].completeInterval = setInterval(function() {
			checkComplete(player);
		}, 100);
	}

	/** Load the data for a single element. **/
	function loadImage(element, component, player) {
		var img = new Image();
		var elementName = $(element).attr('name');
		var elementSource = $(element).attr('src');
		var skinUrl = $.fn.jwplayerUtils.getAbsolutePath(player.model.config.skin);
		var skinRoot = skinUrl.substr(0, skinUrl.lastIndexOf('/'));
		var imgUrl = (elementSource.indexOf('data:image/png;base64,') === 0) ? elementSource : [skinRoot, component, elementSource].join('/');

		player.skin[component].elements[elementName] = {
			height: 0,
			width: 0,
			src: '',
			ready: false
		};

		$(img).load(completeImageLoad(img, elementName, component, player));
		$(img).error(function() {
			player.skin[component].elements[elementName].ready = true;
			resetCompleteIntervalTest(player);
		});

		img.src = imgUrl;
	}

	function checkComplete(player) {
		for (var component in player.skin) {
			if (component != 'properties') {
				for (var element in player.skin[component].elements) {
					if (!player.skin[component].elements[element].ready) {
						return;
					}
				}
			}
		}
		if (players[player.id].loading === false) {
			clearInterval(players[player.id].completeInterval);
			players[player.id].completeHandler();
		}
	}

	function completeImageLoad(img, element, component, player) {
		return function() {
			player.skin[component].elements[element].height = img.height;
			player.skin[component].elements[element].width = img.width;
			player.skin[component].elements[element].src = img.src;
			player.skin[component].elements[element].ready = true;
			resetCompleteIntervalTest(player);
		};
	}

	$.fn.jwplayerSkinner.hasComponent = function(player, component) {
		return (player.skin[component] !== null);
	};


	$.fn.jwplayerSkinner.getSkinElement = function(player, component, element) {
		try {
			return player.skin[component].elements[element];
		} catch (err) {
			$.fn.jwplayerUtils.log("No such skin component / element: ", [player, component, element]);
		}
		return null;
	};


	$.fn.jwplayerSkinner.addSkinElement = function(player, component, name, element) {
		try {
			player.skin[component][name] = element;
		} catch (err) {
			$.fn.jwplayerUtils.log("No such skin component ", [player, component]);
		}
	};

	$.fn.jwplayerSkinner.getSkinProperties = function(player) {
		return player.skin.properties;
	};

})(jQuery);
/**
 * Utility methods for the JW Player.
 *
 * @author jeroen
 * @version 1.0alpha
 * @lastmodifiedauthor zach
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	/** Constructor **/
	$.fn.jwplayerUtils = function() {
		return this.each(function() {
		});
	};

	//http://old.nabble.com/jQuery-may-add-$.browser.isiPhone-td11163329s27240.html
	$.fn.jwplayerUtils.isiPhone = function() {
		var agent = navigator.userAgent.toLowerCase();
		return agent.match(/iPhone/i);
	};

	$.fn.jwplayerUtils.isiPad = function() {
		var agent = navigator.userAgent.toLowerCase();
		return agent.match(/iPad/i);
	};

	/** Check if this client supports Flash player 9.0.115+ (FLV/H264). **/
	$.fn.jwplayerUtils.supportsFlash = function() {
		var version = '0,0,0,0';
		try {
			try {
				var axo = new ActiveXObject('ShockwaveFlash.ShockwaveFlash.6');
				try {
					axo.AllowScriptAccess = 'always';
				} catch (e) {
					version = '6,0,0';
				}
			} catch (e) {
			}
			version = new ActiveXObject('ShockwaveFlash.ShockwaveFlash').GetVariable('$version').replace(/\D+/g, ',').match(/^,?(.+),?$/)[1];
		} catch (e) {
			try {
				if (navigator.mimeTypes['application/x-shockwave-flash'].enabledPlugin) {
					version = (navigator.plugins['Shockwave Flash 2.0'] ||
					navigator.plugins['Shockwave Flash']).description.replace(/\D+/g, ",").match(/^,?(.+),?$/)[1];
				}
			} catch (e) {
			}
		}
		var major = parseInt(version.split(',')[0], 10);
		var minor = parseInt(version.split(',')[2], 10);
		if (major > 9 || (major == 9 && minor > 97)) {
			return true;
		} else {
			return false;
		}
	};

	/** Filetypes supported by Flash **/
	var flashFileTypes = {
		'aac': true,
		'f4v': true,
		'flv': true,
		'm4a': true,
		'm4v': true,
		'mov': true,
		'mp3': true,
		'mp4': true
	};


	/** Check if this client supports Flash player 9.0.115+ (FLV/H264). **/
	$.fn.jwplayerUtils.flashCanPlay = function(fileName) {
		if (flashFileTypes[$.fn.jwplayerUtils.extension(fileName)]) {
			return true;
		}
		return false;
	};

	/** Check if this client supports playback for the specified type. **/
	$.fn.jwplayerUtils.supportsType = function(type) {
		try {
			return !!document.createElement('video').canPlayType(type);
		} catch (e) {
			return false;
		}
	};

	/** Check if this client supports HTML5 H.264 playback. **/
	$.fn.jwplayerUtils.supportsH264 = function() {
		return $.fn.jwplayerUtils.supportsType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
	};


	/** Check if this client supports HTML5 OGG playback. **/
	$.fn.jwplayerUtils.supportsOgg = function() {
		return $.fn.jwplayerUtils.supportsType('video/ogg; codecs="theora, vorbis"');
	};

	/** Returns the extension of a file name **/
	$.fn.jwplayerUtils.extension = function(path) {
		return path.substr(path.lastIndexOf('.') + 1, path.length);
	};

	/** Resets an element's CSS **/
	/*$.fn.jwplayerCSS = function(options) {
		return this.each(function() {
			var defaults = {
				'margin': 0,
				'padding': 0,
				'background': 'none',
				'border': 'none',
				'bottom': 'auto',
				'clear': 'none',
				'float': 'none',
				'font-family': '"Arial", "Helvetica", sans-serif',
				'font-size': 'medium',
				'font-style': 'normal',
				'font-weight': 'normal',
				'height': 'auto',
				'left': 'auto',
				'letter-spacing': 'normal',
				'line-height': 'normal',
				'max-height': 'none',
				'max-width': 'none',
				'min-height': 0,
				'min-width': 0,
				'overflow': 'visible',
				'position': 'static',
				'right': 'auto',
				'text-align': 'left',
				'text-decoration': 'none',
				'text-indent': 0,
				'text-transform': 'none',
				'top': 'auto',
				'visibility': 'visible',
				'white-space': 'normal',
				'width': 'auto',
				'z-index': 'auto'
			};
			try {
				$(this).css($.extend(defaults, options));
			} catch (err) {
				//alert($.fn.jwplayerUtils.dump(err));
			}
		});
	};*/

	$.fn.jwplayerUtils.isNull = function(obj) {
		return ((obj === null) || (obj === undefined) || (obj === ""));
	};

	/** Gets an absolute file path based on a relative filepath **/
	$.fn.jwplayerUtils.getAbsolutePath = function(path) {
		if ($.fn.jwplayerUtils.isNull(path)){
			return path;
		}
		if (isAbsolutePath(path)) {
			return path;
		}
		var protocol = document.location.href.substr(0, document.location.href.indexOf("://") + 3);
		var basepath = document.location.href.substring(protocol.length, (path.indexOf("/") === 0) ? document.location.href.indexOf('/', protocol.length) : document.location.href.lastIndexOf('/'));
		var patharray = (basepath + "/" + path).split("/");
		var result = [];
		for (var i = 0; i < patharray.length; i++) {
			if ($.fn.jwplayerUtils.isNull(patharray[i]) || patharray[i] == ".") {
				continue;
			} else if (patharray[i] == "..") {
				result.pop();
			} else {
				result.push(patharray[i]);
			}
		}
		return protocol + result.join("/");
	};

	function isAbsolutePath(path) {
		if($.fn.jwplayerUtils.isNull(path)){
			return;
		}
		var protocol = path.indexOf("://");
		var queryparams = path.indexOf("?");
		return (protocol > 0 && (queryparams < 0 || (queryparams > protocol)));
	}

	$.fn.jwplayerUtils.mapEmpty = function (map){
		for (var val in map){
			return false;
		}
		return true;
	};

	$.fn.jwplayerUtils.mapLength = function (map){
		var result = 0;
		for (var val in map){
			result++;
		}
		return result;
	};


	/** Dumps the content of an object to a string **/
	$.fn.jwplayerUtils.dump = function(object, depth) {
		if (object === null) {
			return 'null';
		} else if ($.fn.jwplayerUtils.typeOf(object) != 'object') {
			if ($.fn.jwplayerUtils.typeOf(object) == 'string') {
				return "\"" + object + "\"";
			}
			return object;
		}

		var type = $.fn.jwplayerUtils.typeOf(object);

		depth = (depth === undefined) ? 1 : depth + 1;
		var indent = "";
		for (var i = 0; i < depth; i++) {
			indent += "\t";
		}

		var result = (type == "array") ? "[" : "{";
		result += "\n" + indent;

		for (var i in object) {
			if (type == "object") {
				result += "\"" + i + "\": ";
			}
			result += $.fn.jwplayerUtils.dump(object[i], depth) + ",\n" + indent;
		}

		result = result.substring(0, result.length - 2 - depth) + "\n";

		result += indent.substring(0, indent.length - 1);
		result += (type == "array") ? "]" : "}";

		return result;
	};

	/** Returns the true type of an object **/
	$.fn.jwplayerUtils.typeOf = function(value) {
		var s = typeof value;
		if (s === 'object') {
			if (value) {
				if (value instanceof Array) {
					s = 'array';
				}
			} else {
				s = 'null';
			}
		}
		return s;
	};


	/** Logger **/
	$.fn.jwplayerUtils.log = function(msg, obj) {
		try {
			if (obj) {
				console.log("%s: %o", msg, obj);
			} else {
				console.log($.fn.jwplayerUtils.dump(msg));
			}
		} catch (err) {
		}
		return this;
	};


})(jQuery);
/**
 * JW Player view component
 *
 * @author zach
 * @version 1.0alpha
 * @lastmodifieddate 2010-04-11
 */
(function($) {

	var styleString = "left:0px;top:0px;position:absolute;z-index:0;";
	var embedString = "<embed %elementvars% src='%flashplayer%' allowfullscreen='true' allowscriptaccess='always' flashvars='%flashvars%' %style% />";
	var objectString = "<object classid='clsid:D27CDB6E-AE6D-11cf-96B8-444553540000' %elementvars% %style% > <param name='movie' value='%flashplayer%'> <param name='allowfullscreen' value='true'> <param name='allowscriptaccess' value='always'> <param name='wmode' value='transparent'> <param name='flashvars' value='%flashvars%'> </object>";
	var elementvars = {
		id: true,
		name: true,
		className: true
	};

	$.fn.jwplayerView = function(player) {
		player.model.domelement.wrap("<div id='" + player.model.config.id + "_jwplayer' />");
		player.model.domelement.parent().css({
			position: 'relative',
			height: player.config.height+'px',
			width: player.config.width+'px',
			margin: 'auto',
			padding: 0,
			'background-color': player.config.screencolor
		});
		var display = ($.fn.jwplayerUtils.isiPhone() || !(navigator.plugins && navigator.mimeTypes && navigator.mimeTypes.length)) ? 'block' : 'none' ;
		player.model.domelement.css({
			position: 'absolute',
			width: player.model.config.width+'px',
			height: player.model.config.height+'px',
			top: 0,
			left: 0,
			'z-index': 0,
			margin: 'auto',
			display: display
		});
	};

	$.fn.jwplayerView.switchMediaProvider = function() {

	};

	/** Embeds a Flash Player at the specified location in the DOM. **/
	$.fn.jwplayerView.embedFlash = function(player, options) {
		if (player.model.config.flashplayer) {
			var htmlString, elementvarString = "", flashvarString = "";
			if (navigator.plugins && navigator.mimeTypes && navigator.mimeTypes.length) {
				htmlString = embedString;
			} else {
				htmlString = objectString;
			}
			for (var elementvar in elementvars) {
				if (!$.fn.jwplayerUtils.isNull(player.model.config[elementvar])) {
					elementvarString += elementvar + "='" + player.model.config[elementvar] + "' ";
				}
			}
			if (elementvarString.indexOf("name=") < 0) {
				elementvarString += "name='" + player.id + "' ";
			}
			var config = $.extend(true, {}, player.model.config, options);
			if (!$.fn.jwplayerUtils.isNull(player.model.sources[player.model.source])){
				flashvarString += 'file=' + $.fn.jwplayerUtils.getAbsolutePath(player.model.sources[player.model.source].file) + '&';
			}
			if (!$.fn.jwplayerUtils.isNull(config.image)){
				flashvarString += 'image=' + $.fn.jwplayerUtils.getAbsolutePath(config.image) + '&';
			}
			for (var flashvar in config) {
				if ((flashvar == 'file') || (flashvar == 'image') || (flashvar == 'plugins')) {
					continue;
				}
				if (!$.fn.jwplayerUtils.isNull(config[flashvar])) {
					flashvarString += flashvar + '=' + config[flashvar] + '&';
				}
			}

			flashvarString += 'playerready=$.fn.jwplayerMediaFlash.playerReady';

			htmlString = htmlString.replace("%elementvars%", elementvarString);
			htmlString = htmlString.replace("%flashvars%", flashvarString);
			htmlString = htmlString.replace("%flashplayer%", $.fn.jwplayerUtils.getAbsolutePath(player.model.config.flashplayer));
			htmlString = htmlString.replace("%style%", "style='" + styleString + "width:" + player.model.config.width + "px;height:" + player.model.config.height + "px;'");
			if (navigator.plugins && navigator.mimeTypes && navigator.mimeTypes.length) {
				htmlString = htmlString.replace("%style%", "style='" + styleString + "width:" + player.model.config.width + "px;height:" + player.model.config.height + "px;'");
				player.model.domelement.before(htmlString);
			} else {
				htmlString = htmlString.replace("%style%", "style='" + styleString + "width:" + player.model.config.width + "px;height:" + (player.model.config.height + player.skin.controlbar.elements.background.height) + "px;'");
				player.model.domelement.before("<div />");
				player.model.domelement.prev().html(htmlString);

			}
			var oldDOMElement = player.model.domelement;
			player.model.domelement = player.model.domelement.prev();
			oldDOMElement.remove();
		}
	};
})(jQuery);

/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.players.Html5Player');

goog.require('goog.array');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.Component');
goog.require('goog.userAgent.product');
goog.require('mcore.players');



/**
 * HTML5 Player.
 *
 * Capable of rendering itself or decorating an existing HTMLMediaElement.
 *
 * Provides a single NO_SUPPORTED_SRC event when all sources fail to play.
 *
 * Provides a simple CAN_PLAY event, which fires once when we find a playable
 * source and enough of it is downloaded to begin playing.
 *
 * Attempts to workaround the shortcomings of <video> tag support on Android,
 * but this is currently untested.
 *
 * @param {mcore.players.MediaType=} opt_mediaType Audio or video. Necessary
 *     only for rendering.
 * @param {Object|Array.<string>|string=} opt_mediaAttrs If object, then a map
 *     of name-value pairs for attributes. If a string, then this is the
 *     className of the new element. If an array, the elements will be joined
 *     together as the className of the new element. Used only for rendering
 *     the HTMLMediaElement.
 * @param {Array.<mcore.players.Html5Player.Source>=} opt_sources Media sources
 *     to try playing, if there are multiple. Used for rendering.
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.Html5Player = function(opt_mediaType, opt_mediaAttrs,
    opt_sources, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * Audio or Video. Necessary only when rendering.
   * @type {mcore.players.MediaType|undefined}
   * @private
   */
  this.mediaType_ = opt_mediaType;

  /**
   * Attributes to render the HTMLMediaElement with.
   * @see goog.dom.createDom
   * @type {Object|Array.<string>|string|undefined}
   * @private
   */
  this.mediaAttrs_ = opt_mediaAttrs;

  /**
   * Media Sources. Can be undefined if decorating instead of rendering,
   * or if the only source is defined in this.mediaAttrs.
   * @type {Array.<mcore.players.Html5Player.Source>|undefined}
   * @private
   */
  this.sources_ = opt_sources;
};
goog.inherits(mcore.players.Html5Player, goog.ui.Component);


/**
 * Multiple media sources are specified as objects with these keys.
 * Only a 'src' is required.
 * @typedef {{src: string, type, media}}
 * */
mcore.players.Html5Player.Source;


/**
 * Feature test the browser to see if HTML5 audio or video is supported.
 * Note that some devices (Android, for one) support video but not audio,
 * so be mindful of which medium you're testing.
 * @param {string=} opt_mediaType 'audio' or 'video'. Defaults to video.
 * @return {boolean} True if the device supports the given media element.
 */
mcore.players.Html5Player.isSupported = function(opt_mediaType) {
  var mediaType = opt_mediaType || mcore.players.MediaType.VIDEO;
  var media = goog.dom.createElement(mediaType);
  return goog.isDef(media.canPlayType);
};


/**
 * The last resort playback source URI.
 * @type {string|undefined}
 * @private
 */
mcore.players.Html5Player.prototype.lastSrc_;


/**
 * Create a HTMLMediaElement, or rather a <video> or <audio> tag.
 * Called by {@link render()}.
 * @protected
 */
mcore.players.Html5Player.prototype.createDom = function() {
  goog.asserts.assertString(this.mediaType_);

  var element = this.dom_.createDom(this.mediaType_, this.mediaAttrs_);
  if (this.sources_) {
    for (var source, i = 0; source = this.sources_[i]; i++) {
      if (goog.userAgent.product.ANDROID) {
        delete source['type'];
      }
      this.dom_.append(element, this.dom_.createDom('source', source));
    }
  }

  this.setElementInternal(element);
  this.testSupport();
};


/**
 * Decorate an Html5 Audio or Video element and filter out unplayable sources.
 * @param {Element} element Element to decorate.
 * @protected
 */
mcore.players.Html5Player.prototype.decorateInternal = function(element) {
  // Drill down until an <audio> or <video> tag is found
  while (element &&
         element.tagName.toLowerCase() != mcore.players.MediaType.VIDEO &&
         element.tagName.toLowerCase() != mcore.players.MediaType.AUDIO) {
    element = this.dom_.getFirstElementChild(element);
  }
  if (!element) {
    throw Error(goog.ui.Component.Error.DECORATE_INVALID);
  }

  this.mediaType_ = /** @type {mcore.players.MediaType} */
      (element.tagName.toLowerCase());

  // Workaround a broken HTMLMediaElement.canPlayType on Android devices,
  // which always returns an empty string regardless of whether the type
  // is supported.
  if (goog.userAgent.product.ANDROID && !element.src) {
    var sources = this.dom_.getElementsByTagNameAndClass('source',
        undefined, element);
    for (var source, i = 0; source = sources[i]; ++i) {
      source.removeAttribute('type');
    }
  }

  this.setElementInternal(element);
  this.testSupport();
};


/**
 * Dispatch events immediately if we know we don't support Html5 or any
 * of the given sources, otherwise attach events and wait for success/failure.
 */
mcore.players.Html5Player.prototype.testSupport = function() {
  if (mcore.players.Html5Player.isSupported(this.mediaType_)) {
    if (this.testSources()) {
      this.attachEvents();
    } else {
      this.dispatchEvent(mcore.players.EventType.NO_SUPPORTED_SRC);
    }
  } else {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
  }
};


/**
 * Inspect the media tag and find our last resort for playable sources.
 * When errors occur, we'll know playback has failed completely when it
 * fails on the last source returned here.
 *
 * During this process any sources whose mimetype the browser can't play
 * are removed from the DOM. Hopefully this will prevent iPads from
 * failing to try anything but the first source listed, but I don't have
 * one to test with at the time of writing.
 *
 * @return {boolean} True if any of the sources are worth trying.
 * @protected
 */
mcore.players.Html5Player.prototype.testSources = function() {
  var media = /** @type {HTMLMediaElement} */ (this.getElement());
  // Check for a src attribute on the <video> tag
  if (media.src) {
    this.lastSrc_ = media.src;
  } else {
    // Check all the child source tags of <video>
    var sources = this.dom_.getElementsByTagNameAndClass('source',
        undefined, media);
    var source, maybePlayable;
    for (var i = 0; source = sources[i]; i++) {
      maybePlayable = !source.type || media.canPlayType(source.type);
      if (maybePlayable && maybePlayable != 'no') {
        this.lastSrc_ = source.src;
      } else {
        this.dom_.removeNode(source);
      }
    }
  }
  return !!this.lastSrc_;
};


/**
 * Attach event listeners.
 * To avoid a potential race condition by inserting the HTMLMediaElement into
 * the DOM prior to the error handler being in place, we are intentionally not
 * using {@link enterDocument} to attach these listeners.
 * @protected
 */
mcore.players.Html5Player.prototype.attachEvents = function() {
  var element = this.getElement();
  var handler = this.getHandler();
  handler.listen(element,
                 goog.events.EventType.ERROR,
                 this.handleError,
                 true /* fire in the capture phase (required) */);
  handler.listenOnce(element,
                     mcore.players.EventType.CAN_PLAY,
                     this.handleCanPlay);

  // On Android an extra event is needed to trigger playback
  if (goog.userAgent.product.ANDROID) {
    handler.listen(element,
                   goog.events.EventType.CLICK,
                   this.handleAndroidClick);
  }
};


/**
 * Handle an error event on the HTMLMediaElement or any of its child sources.
 *
 * At one point the HTML5 spec stated that each <source> should raise an
 * error when it cannot play, while now browsers are supposed to only throw
 * one error when all sources fail to play. WebKit does the former while
 * Firefox does the latter. For our purposes we only care when all sources
 * have failed.
 *
 * @param {goog.events.Event} e The error event.
 * @protected
 */
mcore.players.Html5Player.prototype.handleError = function(e) {
  e.stopPropagation();
  // TODO: Explicitly check the error code and handle:
  //        element.error.code == MEDIA_SRC_NOT_SUPPORTED,
  //                              MEDIA_ERR_NETWORK,
  //                              MEDIA_ERR_DECODE,
  //                              MEDIA_ERR_ABORT
  //        element.networkState == NETWORK_NO_SOURCE
  if (// On Firefox this implies all sources have failed.
      !this.getElement().currentSrc ||
      // On WebKit with multiple <source> tags, this means they all failed.
      this.getElement().currentSrc.match(this.lastSrc_)
  ) {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORTED_SRC);
  }
};


/**
 * Fire a play event when the player successfully starts to play.
 * @param {goog.events.Event} e The canplay event.
 * @protected
 */
mcore.players.Html5Player.prototype.handleCanPlay = function(e) {
  this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
};


/**
 * Begin playing the video when clicked to overcome Android shortcomings.
 * @param {!goog.events.BrowserEvent} e Click event.
 * @protected
 */
mcore.players.Html5Player.prototype.handleAndroidClick = function(e) {
  this.getElement().play();
};


/**
 * Return the player element itself.
 * @return {HTMLAudioElement|HTMLVideoElement} The HTML5 element.
 */
mcore.players.Html5Player.prototype.getContentElement =
    goog.ui.Component.prototype.getElement;


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {mcore.players.Html5Player} The player instance for chaining.
 */
mcore.players.Html5Player.prototype.setSize = mcore.players.setSize;


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {mcore.players.Html5Player}
 */
mcore.players.Html5Player.prototype.getSize = mcore.players.getSize;


/** @inheritDoc */
mcore.players.Html5Player.prototype.disposeInternal = function() {
  this.lastSrc_ = undefined;
  this.mediaType_ = undefined;
  this.mediaAttrs_ = undefined;
  this.sources_ = undefined;
  goog.base(this, 'disposeInternal');
};


goog.exportSymbol('mcore.Html5Player', mcore.players.Html5Player);
goog.exportSymbol('mcore.Html5Player.isSupported',
    mcore.players.Html5Player.isSupported);

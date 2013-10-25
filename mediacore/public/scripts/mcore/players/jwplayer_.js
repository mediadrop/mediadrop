/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * BARE MINIMUM PLAYER METHODS (called from our code):
 *
 * decorate
 * setSize
 * getSize
 * getContentElement
 * getDomHelper
 */

goog.provide('mcore.players.JWPlayer');

goog.require('goog.dom');
goog.require('goog.math');
goog.require('goog.object');
goog.require('goog.style');
goog.require('goog.ui.Component');
goog.require('goog.userAgent.product');
goog.require('mcore.players');

/**
 * JW Player.
 *
 * @param {Object.<string, *>} jwplayerOpts An options object of the format
 *     expected by the jwplayer library. See:
 *     http://www.longtailvideo.com/support/jw-player/jw-player-for-flash-v5/12538/supported-player-embed-methods
 *     http://www.longtailvideo.com/support/jw-player/jw-player-for-flash-v5/12540/javascript-api-reference
 * @param {Object=} opt_flashPlaylist Optional playlist override for when
 *     the flash-based JWPlayer is available. Useful for providing RTMP
 *     URLs to Flash and HTTP URLs for HTML5.
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.JWPlayer = function(jwplayerOpts, opt_flashPlaylist, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * The instantiation options for our jwplayer object.
   * @type {Object.<string, *>}
   * @private
   */
  this.jwplayerOpts_ = jwplayerOpts;

  /**
   * An optional playlist data structure for when the flash-based JWPlayer is
   * available. Useful for providing RTMP URLs to Flash and HTTP URLs for
   * devices that only support HTML5.
   * @type {Object|undefined}
   * @private
   */
  this.flashPlaylist_ = opt_flashPlaylist;

  // We will add our onReady and onError events to the player options
  var events = jwplayerOpts['events'] = jwplayerOpts['events'] || {};
  var newEvents = {
    'onReady': goog.bind(this.handlePlayerReady, this),
    'onError': goog.bind(this.handlePlayerError, this)
  };
  goog.object.forEach(newEvents, function(listener, type) {
    if (events[type]) {
      var origListener = events[type];
      events[type] = function() {
        listener();
        origListener();
      };
    } else {
      events[type] = listener;
    }
  });
};
goog.inherits(mcore.players.JWPlayer, goog.ui.Component);


/**
 * JW Embedder Instance.
 * @type {jwplayer.api.PlayerAPI|undefined}
 * @private
 */
mcore.players.JWPlayer.prototype.jwplayer_;


/**
 * A width and height to resize the player to once it's loaded.
 * @type {Array.<number>|undefined}
 * @private
 */
mcore.players.JWPlayer.prototype.pendingResize_;



/**
 * Create a div element and decorate it with a jwplayer() instance.
 * Called by {@link render()}.
 * @protected
 */
mcore.players.JWPlayer.prototype.createDom = function() {
  var outer = this.dom_.createDom('div');
  var body = this.dom_.getDocument().body;
  goog.style.showElement(outer, false);
  body.appendChild(outer);
  this.decorateInternal(outer);
  body.removeChild(outer);
  goog.style.showElement(outer, true);
};


/**
 * Determines if a given element can be decorated by this type of component.
 * @param {Element} element Element to decorate.
 * @return {boolean} True if the element can be decorated, false otherwise.
 */
mcore.players.JWPlayer.prototype.canDecorate = function(element) {
  if (!element) { return false; }

  // JWPlayer is stupid and can only work with elements that are available via
  // the window.document.getElement() method. This leads to the constraint that
  // candidates for decoration must be descendants of window.document.body
  var body = this.dom_.getDocument().body;
  var ancestralBody = goog.dom.getAncestor(element,
      function(ancestor) { return ancestor == body; }
  );
  if (ancestralBody == null) { return false; }

  return true;
};


/**
 * Decorate a <div> element by inserting a child element and delegating control
 * of that child element to the external jwplayer library.
 * @param {Element} element Element to decorate.
 * @protected
 */
mcore.players.JWPlayer.prototype.decorateInternal = function(element) {
  // JWPlayer 5.4 on iPhone produces this error in an infinite loop:
  // TypeError: Result of expression 'v.getBoundingClientRect' [undefined] is not a function.
  // Abort and hope that we were decorating an HTML5 element which will
  // play properly on this device.
  if (goog.userAgent.product.IPHONE || goog.userAgent.product.IPAD) {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
    return;
  }

  var contentElement = this.dom_.getFirstElementChild(element);

  // Create a div for the player to be injected into if there's no html5 tag
  // to decorate.
  if (contentElement.tagName != 'AUDIO' && contentElement.tagName != 'VIDEO') {
    contentElement = this.dom_.createElement('div');
    element.appendChild(contentElement);
  }

  // A unique ID is required by the JW embedder js.
  if (contentElement.id) {
    this.setId(contentElement.id);
  } else {
    contentElement.id = this.getId();
  }

  // Define the size of the player-box div so that it won't collapse while
  // JWPlayer loads the flash player. This is important even when HTML5 is
  // being decorated.
  goog.style.setSize(element,
      this.jwplayerOpts_.width, this.jwplayerOpts_.height);

  this.jwplayer_ = jwplayer(contentElement).setup(this.jwplayerOpts_);

  this.setElementInternal(element);
};


/**
 * Callback event for the JWPlayer library.
 *
 * Executed when the player is initialized. Does not necessarily mean that the
 * player is able to play any of the available media files. Only means that the
 * player has been rendered and can be interacted with.
 */
mcore.players.JWPlayer.prototype.handlePlayerReady = function() {
  if (this.pendingResize_) {
    this.jwplayer_.resize(this.pendingResize_[0], this.pendingResize_[1]);
    delete this.pendingResize_;
  }

  // If a flash-specific playlist was provided, switch to that if JWPlayer
  // loaded the flash player instead of the HTML5 player.
  if (this.flashPlaylist_ &&
      this.getContentElement().tagName == goog.dom.TagName.OBJECT) {
    this.jwplayer_.load(this.flashPlaylist_);
  }
};


/**
 * Callback event for the JWPlayer library.
 *
 * Executed when the initialized player is unable to play any of the available
 * media files, or has otherwise encountered a playback error.
 */
mcore.players.JWPlayer.prototype.handlePlayerError = function() {
  // FIXME: This event naming doesn't fit. We need to rethink all player
  //        event names now that we've implemented a few different players.
  this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
};


/**
 * Returns the DOM element into which child components are to be rendered,
 * or null if the component itself hasn't been rendered yet.
 * @return {Element} Element to contain child elements (null if none).
 */
mcore.players.JWPlayer.prototype.getContentElement = function() {
  return this.dom_.getElement(this.getId());
};


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {mcore.players.JWPlayer} The player instance for chaining.
 */
mcore.players.JWPlayer.prototype.setSize = function(w, opt_h) {
  var h;
  if (w instanceof goog.math.Size) {
    h = w.height;
    w = w.width;
  } else {
    if (opt_h == undefined) {
      throw Error('missing height argument');
    }
    h = opt_h;
  }

  if (!goog.isNumber(w) || !goog.isNumber(h)) {
    throw Error('Provided width and height must be integers.');
  }

  // ensure the containing element is immediately resized. this is always
  // necessary because we set a fixed size when constructing this component
  goog.style.setSize(this.getElement(), w, h);

  if (goog.isDef(this.jwplayer_.getWidth())) {
    this.jwplayer_.resize(w, h);
  } else {
    // XXX: If the result of getWidth() is undefined, we assume the player is
    //      in the middle of initializing. If this is the case, an immediate
    //      call to resize() will be ignored. So we delay until onReady, but
    //      we can improve the situation by resizing the <object> immediately.
    this.pendingResize_ = [w, h];
    var videoOrObjectTag = this.getContentElement();
    videoOrObjectTag.width = w;
    videoOrObjectTag.height = h;
  }
  return this;
};


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {mcore.players.JWPlayer}
 */
mcore.players.JWPlayer.prototype.getSize = function() {
  return goog.style.getSize(this.getElement());
};


/** @inheritDoc */
mcore.players.JWPlayer.prototype.disposeInternal = function() {
  // TODO: Is this nulling really necessary?
  this.jwplayerOpts_ = null;
  this.jwplayer_ = null;
  goog.base(this, 'disposeInternal');
};


goog.exportSymbol('mcore.JWPlayer', mcore.players.JWPlayer);

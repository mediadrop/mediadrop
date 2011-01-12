/**
 * This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
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
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.JWPlayer = function(jwplayerOpts, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * The instantiation options for our jwplayer object.
   * @type {Object.<string, *>}
   * @private
   */
  this.jwplayerOpts_ = jwplayerOpts;

  /**
   * The DOM component into which child components are to be rendered
   * XXX: This element is initially created in decorateInternal(), but will be
   *      further 'decorated' by the third-party jwplayer() initialiation.
   *      The third-party code sometimes removes this element and replaces it
   *      with a new element, copying over the original 'id' attribute. Because
   *      the third-party code references this element only by its 'id'
   *      attribute, it is important that this element has an 'id' attribute
   *      and is a descendant of the main <body> element.
   * XXX: When the third-party jwplayer code replaces this element, it does not
   *      insert the new element in place, but appends it as the last child of
   *      the original element's parent node.
   * @type {Element}
   * @private
   */
  this.contentElement_ = null;

  /**
   * The ID string of the content element (see JWPlayer.contentElement_)
   * @type {string|null}
   * @private
   */
  this.contentElementId_ = null;

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
  var contentElement = this.dom_.getFirstElementChild(element);

  // Create a div for the player to be injected into if there's no html5 tag
  // to decorate.
  if (contentElement.tagName != 'AUDIO' && contentElement.tagName != 'VIDEO') {
    contentElement = this.dom_.createElement('div');
    element.appendChild(contentElement);
  }

  // A unique ID is required by the JW embedder js.
  if (!contentElement.id) {
    contentElement.id = this.getId();
  }

  // Define the size of the player-box div so that it won't collapse while
  // JWPlayer loads the flash player. This is important even when HTML5 is
  // being decorated.
  goog.style.setSize(element,
      this.jwplayerOpts_.width, this.jwplayerOpts_.height);

  this.jwplayer_ = jwplayer(contentElement);
  this.jwplayer_.setup(this.jwplayerOpts_);

  this.contentElement_ = contentElement;
  this.contentElementId_ = contentElement.id;
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
  // The jwplayer() instance may replace the contentElement that we pointed it
  // to with another element having the same ID
  this.contentElement_ = this.dom_.getElement(this.contentElementId_);
  // TODO: Make use of this hook.
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
  return this.contentElement_;
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

  // ensure the containing element is immediately resized
  goog.style.setSize(this.getElement(), w, h);

  if (goog.isDef(this.jwplayer_.getWidth())) {
    this.jwplayer_.resize(w, h);
  } else {
    // XXX: If the result of getWidth() is undefined, we assume the player is
    //      in the middle of initializing. If this is the case, an immediate
    //      call to resize() will be ignored. So we set a delayed retry.
    goog.Timer.callOnce(function() {
      this.setSize(w, h);
    }, 100, this);
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
  this.contentElement_ = null;
  this.jwplayerOpts_ = null;
  this.jwplayer_ = null;
  goog.base(this, 'disposeInternal');
};


goog.exportSymbol('mcore.JWPlayer', mcore.players.JWPlayer);

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

goog.require('goog.array');
goog.require('goog.asserts');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.math');
goog.require('goog.ui.Component');
goog.require('goog.userAgent.product');
goog.require('mcore.players');

/**
 * JW Player.
 *
 * XXX: Capable only of decorating an existing <div> element when the the
 *      selected <div> element has, among its children, a single <div> tag with
 *      a non-empty 'id' attribute.
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
   * @type {Element}
   * @private
   */
  this.contentElement_ = null;
};
goog.inherits(mcore.players.JWPlayer, goog.ui.Component);


/**
 * Multiple media sources are specified as objects with these keys.
 * Only a 'src' is required.
 * @typedef {{src: string, type, media}}
 * */
mcore.players.JWPlayer.Source;

/**
 * Create a div element and decorate it with a jwplayer() instance.
 * Called by {@link render()}.
 * @protected
 */
mcore.players.JWPlayer.prototype.createDom = function() {
  /** XXX: Not implemented! */
  throw Error(goog.ui.Component.Error.NOT_SUPPORTED);
};


/**
 * Determines if a given element can be decorated by this type of component.
 * @param {Element} element Element to decorate.
 * @return {boolean} True if the element can be decorated, false otherwise.
 */
mcore.players.JWPlayer.prototype.canDecorate = function(element) {
  if (!element) { return false; }

  // The provided element must contain one <div>
  var divs = element.getElementsByTagName('div');
  if (divs.length != 1) { return false; }

  // This element must have an 'id' attribute, or JWPlayer will break.
  var contentElement = divs[0];
  if (contentElement.id == '') { return false; }

  return true;
};


/**
 * Decorate an Html5 Audio or Video element and filter out unplayable sources.
 * @param {Element} element Element to decorate.
 * @protected
 */
mcore.players.JWPlayer.prototype.decorateInternal = function(element) {
  if (!this.canDecorate(element)) {
    throw Error(goog.ui.Component.Error.DECORATE_INVALID);
  }
  var contentElement = element.getElementsByTagName('div')[0];

  // ensure the containing element is immediately resized
  goog.style.setSize(element,
      this.jwplayerOpts_.width, this.jwplayerOpts_.height);

  this.jwplayer_ = jwplayer(contentElement);
  this.jwplayer_.setup(this.jwplayerOpts_)
  this.contentElement_ = contentElement;
  this.setElementInternal(element);
};


/**
 * Attach event listeners.
 * To avoid a potential race condition by inserting the HTMLMediaElement into
 * the DOM prior to the error handler being in place, we are intentionally not
 * using {@link enterDocument} to attach these listeners.
 * @protected
 */
mcore.players.JWPlayer.prototype.attachEvents = function() {
  var element = this.getElement();
  var handler = this.getHandler();
  handler.listenOnce(element,
                     mcore.players.EventType.CAN_PLAY,
                     this.handleCanPlay);
};

/**
 * Fire a play event when the player successfully starts to play.
 * @param {goog.events.Event} e The canplay event.
 * @protected
 */
mcore.players.JWPlayer.prototype.handleCanPlay = function(e) {
  this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
};


/**
 * Returns the DOM element into which child components are to be rendered,
 * or null if the component itself hasn't been rendered yet.
 * @return {Element} Element to contain child elements (null if none).
 */
mcore.players.JWPlayer.prototype.getContentElement = function() {
  return this.contentElement_;
}

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
    var this_ = this;
    setTimeout(function() {
      this_.setSize(w, h);
    }, 100);
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

/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

/**
 * @fileoverview Provides a similar interface for rendering Flash
 * players as for rendering Html5 players.
 */

goog.provide('mcore.players.FlashPlayer');

goog.require('goog.ui.media.FlashObject');
goog.require('goog.userAgent.flash');
goog.require('goog.userAgent.product');
goog.require('mcore.players');



/**
 * Flash Player.
 *
 * Renders a flash object in a cross-browser way.
 *
 * @param {string} flashUrl The flash SWF URL.
 * @param {number|string|goog.math.Size=} opt_width The width or Size object
 *     of the movie.
 * @param {number|string=} opt_height The height of the movie.
 * @param {Object=} opt_flashVars Flash vars to add.
 * @param {goog.dom.DomHelper=} opt_domHelper An optional DomHelper.
 * @constructor
 * @extends {goog.ui.media.FlashObject}
 */
mcore.players.FlashPlayer = function(flashUrl, opt_width, opt_height,
    opt_flashVars, opt_domHelper) {
  goog.base(this, flashUrl, opt_domHelper);

  /**
   * The Flash SWF URL. Stored here because there is no public accesor
   * for this in goog.ui.media.FlashObject.
   * @type {string}
   * @protected
   */
  this.flashUrl = flashUrl;

  this.setRequiredVersion(mcore.players.FlashPlayer.REQUIRED_VERSION);

  if (opt_width && opt_height) {
    this.setSize(opt_width, opt_height);
  }
  if (opt_flashVars) {
    this.addFlashVars(opt_flashVars);
  }
};
goog.inherits(mcore.players.FlashPlayer, goog.ui.media.FlashObject);


/**
 * The version of Flash that is required for playback of most video.
 * @type {string}
 */
mcore.players.FlashPlayer.REQUIRED_VERSION = '9.0.115.0';


/**
 * @return {boolean} True if the device supports Flash and the H264 codec.
 */
mcore.players.FlashPlayer.isSupported = function() {
  return goog.userAgent.flash.isVersion(
      mcore.players.FlashPlayer.REQUIRED_VERSION);
};


/**
 * Dispatch an event indicating flash is supported or it isn't.
 * @return {boolean} Success.
 */
mcore.players.FlashPlayer.prototype.testSupport = function() {
  var isSupported = mcore.players.FlashPlayer.isSupported();
  if (!isSupported && this.isYoutubeOnIPhone()) {
    isSupported = true;
    // Disable the flash version checking so that rendering will continue
    this.setRequiredVersion(null);
  }
  if (isSupported) {
    this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
    return true;
  }
  this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
  return false;
};


/**
 * iPhones and iPads support YouTube videos when embedded with an <embed> tag.
 * @return {boolean} True if the browser is an iDevice and the flash URL
 *     is a YouTube Video.
 */
mcore.players.FlashPlayer.prototype.isYoutubeOnIPhone = function() {
  return (goog.userAgent.product.IPHONE || goog.userAgent.product.IPAD) &&
      /^https?:\/\/(\w+\.)?youtube\.com/.test(this.flashUrl);
};


/**
 * Renders the flash object or dispatches a not-supported event.
 * @inheritDoc
 */
mcore.players.FlashPlayer.prototype.render = function(opt_parentElement) {
  if (this.testSupport()) {
    goog.base(this, 'render', opt_parentElement);
  }
};


/**
 * Renders the flash object or dispatches a not-supported event.
 * @inheritDoc
 */
mcore.players.FlashPlayer.prototype.renderBefore = function(siblingElement) {
  if (this.testSupport()) {
    goog.base(this, 'renderBefore', siblingElement);
  }
};


/**
 * Decorate or dispatch a player not supported event.
 * @inheritDoc
 */
mcore.players.FlashPlayer.prototype.decorate = function(element) {
  if (this.testSupport()) {
    goog.base(this, 'decorate', element);
  }
};


/**
 * Return the player element itself.
 * @return {Element} The flash embed or object element.
 */
mcore.players.FlashPlayer.prototype.getContentElement =
    goog.ui.media.FlashObject.prototype.getFlashElement;


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {goog.ui.media.FlashObject} This player instance for chaining.
 */
mcore.players.FlashPlayer.prototype.setSize = function(w, opt_h) {
  var h;
  // Read Size objects to provide an interface consistent with other players.
  if (w instanceof goog.math.Size) {
    h = w.height;
    w = w.width;
  } else {
    if (!goog.isDef(opt_h) || goog.isNull(w)) {
      throw Error('missing width or height argument');
    }
    h = opt_h;
  }
  return goog.base(this, 'setSize', w, h);
};


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {mcore.players.FlashPlayer}
 */
mcore.players.FlashPlayer.prototype.getSize = mcore.players.getSize;


goog.exportSymbol('mcore.FlashPlayer', mcore.players.FlashPlayer);
goog.exportSymbol('mcore.FlashPlayer.isSupported',
    mcore.players.FlashPlayer.isSupported);
goog.exportSymbol('mcore.FlashPlayer.prototype.decorate',
    mcore.players.FlashPlayer.prototype.decorate);
goog.exportSymbol('mcore.FlashPlayer.prototype.render',
    mcore.players.FlashPlayer.prototype.render);

/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.players.Rater');

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.net.XhrIo');
goog.require('goog.string');
goog.require('goog.ui.Component');



/**
 *
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.events.EventTarget}
 */
mcore.players.Rater = function(opt_domHelper) {
  goog.base(this);

  /**
   * DOM Helper.
   * @type {goog.dom.DomHelper}
   * @protected
   * @suppress {underscore}
   */
  this.dom_ = opt_domHelper || goog.dom.getDomHelper();
};
goog.inherits(mcore.players.Rater, goog.events.EventTarget);


/**
 * XHR for logging the rating.
 * @type {goog.net.XhrIo}
 * @private
 */
mcore.players.Rater.prototype.xhr_;


/**
 * Handle the user clicking the like-this button.
 * @param {string} url Submit URL for logging the rating.
 */
mcore.players.Rater.prototype.like = function(url, parameters) {
  this.submitRating(url, parameters);
  this.incrementDisplayCounter('mcore-likes-counter');
};


/**
 * Handle the user clicking the dislike-this button.
 * @param {string} url Submit URL for logging the rating.
 */
mcore.players.Rater.prototype.dislike = function(url, parameters) {
  this.submitRating(url, parameters);
  this.incrementDisplayCounter('mcore-dislikes-counter');
};


/**
 * Submit a request that increments the likes or dislikes.
 * @param {string} url Submit URL.
 * @protected
 */
mcore.players.Rater.prototype.submitRating = function(url, parameters) {
  this.xhr_ = new goog.net.XhrIo();
  goog.events.listenOnce(this.xhr_,
      goog.net.EventType.COMPLETE,
      this.handleRatingComplete, false, this);
  var data = goog.Uri.QueryData.createFromMap(new goog.structs.Map(parameters));
  this.xhr_.send(url, 'POST', data.toString(), {'X-Requested-With': 'XMLHttpRequest'});
};


/**
 * Cleanup the XHR on any result. We silently ignore the result because
 * a missed like is not a major cause for concern.
 * @param {!goog.events.Event} e XHR Event.
 * @protected
 */
mcore.players.Rater.prototype.handleRatingComplete = function(e) {
  goog.dispose(this.xhr_);
};


/**
 * Increment the number inside the given element.
 * NOTE: i18n: This may result in incorrect pluralization such as "1 likes".
 * @param {Element|string} element A DOM element or string ID.
 * @return {number|undefined} The new count or undefined if a non-existant
 *     element ID was provided.
 */
mcore.players.Rater.prototype.incrementDisplayCounter = function(element) {
  element = this.dom_.getElement(element);
  if (element) {
    var count = Number(this.dom_.getTextContent(element)) + 1;
    this.dom_.setTextContent(element, String(count));
    return count;
  }
};


/** @inheritDoc */
mcore.players.Rater.prototype.disposeInternal = function() {
  goog.base(this, 'disposeInternal');
  goog.dispose(this.xhr_);
  delete this.xhr_;
};

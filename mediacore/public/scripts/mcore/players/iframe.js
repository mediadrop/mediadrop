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

goog.provide('mcore.players.IframePlayer');

goog.require('goog.dom.TagName');
goog.require('goog.ui.Component');
goog.require('mcore.players');



/**
 * Dummy iframe wrapper that provides the bare minimum of methods for a player.
 * @param {goog.dom.DomHelper=} opt_domHelper An optional DomHelper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.IframePlayer = function(opt_domHelper) {
  goog.base(this, opt_domHelper);
};
goog.inherits(mcore.players.IframePlayer, goog.ui.Component);


/**
 * Return the player element itself.
 * @return {Element} The iframe element.
 */
mcore.players.IframePlayer.prototype.getContentElement = function() {
  var iframe = this.dom_.getElementsByTagNameAndClass(goog.dom.TagName.IFRAME,
      undefined, this.getElement())[0];
  return iframe;
};


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {mcore.players.IframePlayer} This player instance for chaining.
 */
mcore.players.IframePlayer.prototype.setSize = mcore.players.setSize;


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {mcore.players.IframePlayer}
 */
mcore.players.IframePlayer.prototype.getSize = mcore.players.getSize;


goog.exportSymbol('mcore.IframePlayer', mcore.players.IframePlayer);

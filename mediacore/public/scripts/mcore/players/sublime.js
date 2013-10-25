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

goog.provide('mcore.players.SublimePlayer');

goog.require('goog.dom.TagName');
goog.require('goog.ui.Component');
goog.require('mcore.players');



/**
 * Dummy wrapper for Sublime. Currently sublime doesn't offer an API for
 * resizing the HTML5 player, so there's not much we can do here yet.
 * @param {goog.dom.DomHelper=} opt_domHelper An optional DomHelper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.SublimePlayer = function(opt_domHelper) {
  goog.base(this, opt_domHelper);
};
goog.inherits(mcore.players.SublimePlayer, goog.ui.Component);


/**
 * Return the player element itself.
 * @return {Element} The iframe element.
 */
mcore.players.SublimePlayer.prototype.getContentElement = function() {
  return this.dom_.getFirstElementChild(this.getElement());
};


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {mcore.players.SublimePlayer} This player instance for chaining.
 */
mcore.players.SublimePlayer.prototype.setSize = goog.nullFunction;


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {mcore.players.SublimePlayer}
 */
mcore.players.SublimePlayer.prototype.getSize = mcore.players.getSize;


goog.exportSymbol('mcore.SublimePlayer', mcore.players.SublimePlayer);

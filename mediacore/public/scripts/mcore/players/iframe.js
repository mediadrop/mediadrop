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

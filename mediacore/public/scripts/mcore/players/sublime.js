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

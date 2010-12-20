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

goog.provide('mcore.players');
goog.provide('mcore.players.EventType');
goog.provide('mcore.players.MediaType');

goog.require('goog.dom');
goog.require('goog.math.Size');
goog.require('goog.style');


/**
 * Media Types
 * @enum {string}
 */
mcore.players.MediaType = {
  AUDIO: 'audio',
  VIDEO: 'video'
};


/**
 * Error Codes
 * @enum {string}
 */
mcore.players.EventType = {
  CAN_PLAY: 'canplay',
  NO_SUPPORT: 'nosupport',
  NO_SUPPORTED_SRC: 'nosupportedsrc'
};


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {goog.ui.Component} The player instance for chaining.
 * @this {goog.ui.Component}
 */
mcore.players.setSize = function(w, opt_h) {
  goog.style.setSize(this.getContentElement(), w, opt_h);
  return this;
};


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size} The player instance for chaining.
 * @this {goog.ui.Component}
 */
mcore.players.getSize = function() {
  return goog.style.getSize(this.getContentElement());
};

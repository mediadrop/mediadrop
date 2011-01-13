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
 * @fileoverview This file defines the signatures of functions and prototypes
 * that are provided by third party libraries, but used in code that will be
 * compiled with the closure compiler.
 *
 * Defining variables here will prevent them being renamed in the compiled
 * code.
 *
 * See: http://code.google.com/closure/compiler/docs/api-tutorial3.html#externs
 */


/**
 * The main jwplayer library access point.
 * From scripts/third-party/jw_player/jwplayer.js
 * @param {Element|string|number=} opt_playerElement The DOM element, ID,
 *     or player index to construct or retrieve the player API for.
 * @return {jwplayer.api.PlayerAPI}
 */
function jwplayer(opt_playerElement) {};

jwplayer.api = {};

/**
 * JW Embedder type.
 * This type is never constructed directly -- {@see jwplayer()}.
 * @constructor
 */
jwplayer.api.PlayerAPI = function() {};

/**
 * @return {number} The current player height.
 */
jwplayer.api.PlayerAPI.prototype.getHeight = function() {};

/**
 * @return {number} The current player width.
 */
jwplayer.api.PlayerAPI.prototype.getWidth = function() {};

/**
 * @param {number} width New width.
 * @param {number} height New Height.
 * @return {jwplayer.api.PlayerAPI} A fluent interface for chaining.
 */
jwplayer.api.PlayerAPI.prototype.resize = function(width, height) {};

/**
 * Configure the JW Embedder with the given options.
 * This can be called multiple times if necessary.
 * @param {Object.<string, *>} options JW Embedder options.
 * @return {jwplayer.api.PlayerAPI} A fluent interface for chaining.
 */
jwplayer.api.PlayerAPI.prototype.setup = function(options) {};

/**
 * Load the given playlist.
 * To be called after {@see setup()}.
 * @param {Array|Object|string} playlist A playlist data structure.
 * @return {jwplayer.api.PlayerAPI} A fluent interface for chaining.
 */
jwplayer.api.PlayerAPI.prototype.load = function(playlist) {};

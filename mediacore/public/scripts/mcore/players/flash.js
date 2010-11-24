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
 *
 * XXX: This is currently not in use by MediaCore, but may be some
 *      time in the future.
 */

goog.provide('mcore.players.FlashPlayer');

goog.require('mcore.players');
goog.require('goog.ui.media.FlashObject');
goog.require('goog.userAgent.flash');



/**
 * Flash Player
 * @param {string} flashUrl The flash SWF URL.
 * @param {number|string=} width The width of the movie.
 * @param {number|string=} height The height of the movie.
 * @param {Object=} opt_flashVars Flash vars to add.
 * @param {goog.dom.DomHelper=} opt_domHelper An optional DomHelper.
 * @constructor
 * @extends {goog.ui.media.FlashObject}
 */
mcore.players.FlashPlayer = function(flashUrl, opt_width, opt_height, opt_flashVars, opt_domHelper) {
  goog.base(this, flashUrl, opt_domHelper);
  if (goog.isDef(opt_width) && goog.isDef(opt_height)) {
    this.setSize(opt_width, opt_height);
  }
  if (goog.isDef(opt_flashVars)) {
    this.addFlashVars(opt_flashVars);
  }
};
goog.inherits(mcore.players.FlashPlayer, goog.ui.media.FlashObject);


/**
 * @return {boolean} True if the device supports Flash and the H264 codec.
 */
mcore.players.FlashPlayer.isSupported = function() {
  return goog.userAgent.flash.isVersion('9.0.115.0');
};


/**
 * Renders the component.  If a parent element is supplied, the component's
 * element will be appended to it.  If there is no optional parent element and
 * the element doesn't have a parentNode then it will be appended to the
 * document body.
 *
 * If this component has a parent component, and the parent component is
 * not in the document already, then this will not call {@code enterDocument}
 * on this component.
 *
 * Throws an Error if the component is already rendered.
 *
 * @param {Element|string=} opt_parentElement Optional parent element to render
 *    the component into.
 * @return {mcore.players.FlashPlayer} This player
 */
mcore.players.FlashPlayer.prototype.render = function(element) {
  element = this.dom_.getElement(element);
  goog.base(this, 'render', element);
}

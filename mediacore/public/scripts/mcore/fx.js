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

goog.provide('mcore.fx');
goog.provide('mcore.fx.SlideIntoView');

goog.require('goog.fx.dom.ResizeHeight');
goog.require('goog.style');



/**
 * Height Resize Animation for sliding an element from 0 to its full height.
 * @param {!Element} element A DOM element.
 * @param {number} duration Length of animation in milliseconds.
 * @param {Function=} opt_acc Acceleration function, returns 0-1 for inputs 0-1.
 * @constructor
 * @extends {goog.fx.dom.ResizeHeight}
 */
mcore.fx.SlideIntoView = function(element, duration, opt_acc) {
  var height = goog.style.getSize(element).height;
  goog.base(this, element, 0, height, duration, opt_acc);
};
goog.inherits(mcore.fx.SlideIntoView, goog.fx.dom.ResizeHeight);


/** @inheritDoc */
mcore.fx.SlideIntoView.prototype.onBegin = function() {
  goog.base(this, 'onBegin');
  this.element.style.display = 'block';
  this.element.style.overflow = 'hidden';
};


/** @inheritDoc */
mcore.fx.SlideIntoView.prototype.onEnd = function() {
  goog.base(this, 'onEnd');
  this.element.style.overflow = '';
};

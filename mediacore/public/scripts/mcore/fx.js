/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

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

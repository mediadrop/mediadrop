/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

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

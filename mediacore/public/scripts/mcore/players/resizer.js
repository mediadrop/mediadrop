/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.players.ColumnViewResizer');
goog.provide('mcore.players.ResizerBase');
goog.provide('mcore.players.WideViewResizer');

goog.require('goog.dom.classes');
goog.require('goog.events.EventTarget');
goog.require('goog.style');



/**
 * Resize Handler for transitioning the player
 * @param {goog.ui.Component} player The player instance to resize.
 * @constructor
 * @extends {goog.events.EventTarget}
 */
mcore.players.ResizerBase = function(player) {
  goog.base(this);

  /**
   * Player instance to resize.
   * @type {goog.ui.Component}
   * @protected
   */
  this.player = player;

  /**
   * DOM Helper
   * @type {!goog.dom.DomHelper}
   * @protected
   * @suppress {underscore}
   */
  this.dom_ = player.getDomHelper();
};
goog.inherits(mcore.players.ResizerBase, goog.events.EventTarget);


/**
 * Expand or reduce the player size depending on its current state.
 */
mcore.players.ResizerBase.prototype.toggleExpanded = function() {
  this.setExpanded(!this.isExpanded());
};


/**
 * Internal flag that indicates if the size is expanded currently.
 * @type {boolean}
 * @protected
 */
mcore.players.ResizerBase.prototype.expanded;


/**
 * @return {boolean} True if the player is not in its smaller state.
 */
mcore.players.ResizerBase.prototype.isExpanded = function() {
  return this.expanded;
};


/**
 * Simple implementation example for resizing the player.
 * This method can be overridden to handle resizing other elements
 * on the page as needed.
 * @param {boolean|number|string} expanded Flag.
 */
mcore.players.ResizerBase.prototype.setExpanded = function(expanded) {
  this.expanded = !!expanded;
  this.resizePlayer(this.expanded);
};


/**
 * Helper that simply expands and contracts the player.
 * @param {boolean} expand True for expand, False for normal size.
 * @return {goog.math.Size} The new player size.
 * @protected
 */
mcore.players.ResizerBase.prototype.resizePlayer = function(expand) {
  var newSize;
  var currSize = this.player.getSize();
  // Our player is expected to be 890x500 (expand) or 560x315 (normal).
  // Sometimes players are rendered with additional height for the controls
  // to maintain a 16:9 aspect ratio, so the height must be adjusted in
  // relative terms only.
  if (expand && currSize.width == 560) {
    newSize = new goog.math.Size(890, currSize.height + (500 - 315));
  } else if (!expand && currSize.width == 890) {
    newSize = new goog.math.Size(560, currSize.height - (500 - 315));
  } else {
    newSize = currSize;
  }
  this.player.setSize(newSize);
  return newSize;
};


/** @inheritDoc */
mcore.players.ResizerBase.prototype.disposeInternal = function() {
  goog.base(this, 'disposeInternal');
  this.player = null;
  delete this.dom_;
};



/**
 * Resize Handler for transitioning the player
 * @param {goog.ui.Component} player The player instance to resize.
 * @constructor
 * @extends {mcore.players.ResizerBase}
 */
mcore.players.ColumnViewResizer = function(player) {
  goog.base(this, player);
  this.expanded = false;
};
goog.inherits(mcore.players.ColumnViewResizer, mcore.players.ResizerBase);


/**
 * Expand or contract the player.
 * @param {boolean|number|string} expanded Flag.
 * @override
 */
mcore.players.ColumnViewResizer.prototype.setExpanded = function(expanded) {
  this.expanded = !!expanded;
  var newSize = this.resizePlayer(this.expanded);

  var container = this.dom_.getElement('media-box');
  var sidebar = this.dom_.getElement('media-sidebar');
  var margin = this.expanded ? goog.style.getSize(container).height + 15 : 0;

  sidebar.style.marginTop = margin + 'px';
  goog.dom.classes.enable(container, 'media-norm', !this.expanded);
  goog.dom.classes.enable(container, 'media-wide', this.expanded);
};



/**
 * Resize Handler for transitioning the player
 * @param {goog.ui.Component} player The player instance to resize.
 * @constructor
 * @extends {mcore.players.ResizerBase}
 */
mcore.players.WideViewResizer = function(player) {
  goog.base(this, player);
  this.expanded = true;
};
goog.inherits(mcore.players.WideViewResizer, mcore.players.ResizerBase);


/**
 * Expand or contract the player.
 * @param {boolean|number|string} expanded Flag.
 * @override
 */
mcore.players.WideViewResizer.prototype.setExpanded = function(expanded) {
  this.expanded = !!expanded;
  var newSize = this.resizePlayer(this.expanded);

  var container = this.dom_.getElement('media-box');
  var info = this.dom_.getElement('media-info');
  var sidebar = this.dom_.getElement('media-sidebar');
  var position, padding;

  if (newSize.width == 560) {
    position = 'absolute';
    padding = goog.style.getSize(container).height + 15 + 'px';
    goog.style.setPosition(container, 0, 0);
  } else {
    position = 'static';
    padding = 0;
  }

  container.style.position = position;
  info.style.paddingTop = padding;
  goog.dom.classes.enable(container, 'media-norm', !this.expanded);
  goog.dom.classes.enable(container, 'media-wide', this.expanded);
};

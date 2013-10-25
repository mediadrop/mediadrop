/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.players.MultiPlayer');

goog.require('goog.array');
goog.require('goog.math.Size');
goog.require('goog.ui.Component');
goog.require('mcore.players.EventType');



/**
 * A component for rendering each of the given players until one works.
 *
 * @param {Array.<goog.ui.Component>} players Player component instances.
 * @param {goog.dom.DomHelper=} opt_domHelper An optional DomHelper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.MultiPlayer = function(players, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * Player UI Components.
   * @type {Array.<goog.ui.Component>}
   * @protected
   */
  this.players = players;
  for (var i=0; i<this.players.length; i++) {
    mcore.players.Controller.mapCompiledMethodNamesToUncompiled(this.players[i]);
  }
};
goog.inherits(mcore.players.MultiPlayer, goog.ui.Component);


/**
 * Index of the currently rendered/decorated sub-player.
 * Corresponds to {@code this.players} and is potentially out of bounds.
 * @type {number}
 * @protected
 */
mcore.players.MultiPlayer.prototype.currentPlayer = -1;


/**
 * Begin working through the available players.
 * @inheritDoc
 */
mcore.players.MultiPlayer.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  this.rotatePlayer();
};


/**
 * Swallow the event and rotate the player when an error event is thrown.
 * @param {goog.events.Event} e Error event.
 * @protected
 */
mcore.players.MultiPlayer.prototype.handleErrorEvent = function(e) {
  e.stopPropagation();
  this.rotatePlayer();
};


/**
 * Try the next available player after disposing of the last one.
 */
mcore.players.MultiPlayer.prototype.rotatePlayer = function() {
  if (this.players[this.currentPlayer]) {
    this.players[this.currentPlayer].dispose();
    delete this.players[this.currentPlayer];
  }

  var player = this.players[++this.currentPlayer];

  if (player) {
    player.setParentEventTarget(this);

    this.getHandler().listen(
        player,
        [mcore.players.EventType.NO_SUPPORT,
         mcore.players.EventType.NO_SUPPORTED_SRC],
        this.handleErrorEvent);

    if (this.wasDecorated()) {
      player.decorate(this.getElement());
    } else {
      player.render(this.getElement());
    }
  } else {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
  }
};


/**
 * Return the player instance that is currently in the document.
 * @return {goog.ui.Component|undefined} A Component subclass.
 */
mcore.players.MultiPlayer.prototype.getCurrentPlayer = function() {
  return this.players[this.currentPlayer];
};


/**
 * Expose a copy of the players to preserve the preferred order.
 * @return {Array.<goog.ui.Component>} Player components.
 */
mcore.players.MultiPlayer.prototype.getPlayers = function() {
  return goog.array.clone(this.players);
};


/** @inheritDoc */
mcore.players.MultiPlayer.prototype.disposeInternal = function() {
  goog.base(this, 'disposeInternal');
  for (var i = 0; i < this.players.length; i++) {
    // The players array may now be sparse so we must check for defined values
    if (this.players[i]) {
      this.players[i].dispose();
    }
  }
  delete this.players;
};


/** @inheritDoc */
mcore.players.MultiPlayer.prototype.getContentElement = function() {
  return this.getCurrentPlayer() ?
      this.getCurrentPlayer().getContentElement() : null;
};


/**
 * Resize the player element to the given dimensions.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 * @return {mcore.players.MultiPlayer} The player instance for chaining.
 */
mcore.players.MultiPlayer.prototype.setSize = function(w, opt_h) {
  if (this.getCurrentPlayer()) {
    this.getCurrentPlayer().setSize(w, opt_h);
  }
  return this;
};


/**
 * Get the current player element dimensions.
 * @return {!goog.math.Size|undefined} The player instance for chaining.
 * @this {mcore.players.MultiPlayer}
 */
mcore.players.MultiPlayer.prototype.getSize = function() {
  if (this.getCurrentPlayer()) {
    return this.getCurrentPlayer().getSize();
  }
  return new goog.math.Size(0, 0);
};


goog.exportSymbol('mcore.MultiPlayer', mcore.players.MultiPlayer);

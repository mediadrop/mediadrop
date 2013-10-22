/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.require('goog.dom');
goog.require('goog.json');

goog.require('goog.testing.ContinuationTestCase');
goog.require('goog.testing.jsunit');
goog.require('goog.userAgent.flash');

goog.require('mcore.players');
goog.require('mcore.players.Html5Player');

var dom = goog.dom;
var $ = dom.getElement;

// restore the flash version for every test
var origHasFlash, origFlashVersion;
var setUpPage = function() {
  origHasFlash = goog.userAgent.flash.HAS_FLASH;
  origFlashVersion = goog.userAgent.flash.VERSION;
};
var tearDown = function() {
  goog.userAgent.flash.HAS_FLASH = origHasFlash;
  goog.userAgent.flash.VERSION = origFlashVersion;
};

// create a mock player component this is always supported.
var MockSupportedPlayer = function() {
  goog.base(this);
};
goog.inherits(MockSupportedPlayer, goog.ui.Component);

MockSupportedPlayer.prototype.isSupported = function() {
  return true;
};
MockSupportedPlayer.prototype.decorate = function() {
  this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
};
MockSupportedPlayer.prototype.render = function() {
  this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
};

// create a mock player component that is never supported.
var MockUnsupportedPlayer = function() {
  goog.base(this);
};
goog.inherits(MockUnsupportedPlayer, goog.ui.Component);

MockUnsupportedPlayer.prototype.isSupported = function() {
  return false;
};
MockUnsupportedPlayer.prototype.decorate = function() {
  this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
};
MockUnsupportedPlayer.prototype.render = function() {
  this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
};



var testNoPlayers = function() {
  var player = new mcore.players.MultiPlayer([]);
  waitForEvent(player, mcore.players.EventType.NO_SUPPORT, function() {
    player.dispose();
  });
  player.render();
};


var testUnsupportedPlayer = function() {
  var player = new mcore.players.MultiPlayer([
    new MockUnsupportedPlayer()
  ]);
  waitForEvent(player, mcore.players.EventType.NO_SUPPORT, function() {
    player.dispose();
  });
  player.render();
};


var testMultipleUnsupportedPlayers = function() {
  var player = new mcore.players.MultiPlayer([
    new MockUnsupportedPlayer(),
    new MockUnsupportedPlayer(),
    new MockUnsupportedPlayer()
  ]);
  waitForEvent(player, mcore.players.EventType.NO_SUPPORT, function() {
    player.dispose();
  });
  player.render();
};


var testSupportedPlayer = function() {
  var player = new mcore.players.MultiPlayer([
    new MockSupportedPlayer()
  ]);
  waitForEvent(player, mcore.players.EventType.CAN_PLAY, function() {
    player.dispose();
  });
  player.render();
};


var testSupportedAndUnsupportedPlayers = function() {
  var player = new mcore.players.MultiPlayer([
    new MockUnsupportedPlayer(),
    new MockSupportedPlayer()
  ]);
  waitForEvent(player, mcore.players.EventType.CAN_PLAY, function() {
    player.dispose();
  });
  player.render();
};


var testCase = new goog.testing.ContinuationTestCase();
testCase.autoDiscoverTests();
G_testRunner.initialize(testCase);

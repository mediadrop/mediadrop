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

goog.require('mcore.players');
goog.require('mcore.players.Html5Player');

goog.require('goog.testing.ContinuationTestCase');
goog.require('goog.testing.jsunit');
goog.require('goog.userAgent.flash');

goog.require('goog.dom');
goog.require('goog.json');

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

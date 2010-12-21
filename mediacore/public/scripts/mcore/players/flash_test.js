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

goog.require('goog.dom');
goog.require('goog.json');
goog.require('goog.testing.ContinuationTestCase');
goog.require('goog.testing.PropertyReplacer');
goog.require('goog.testing.jsunit');
goog.require('goog.userAgent.flash');
goog.require('goog.userAgent.product');

goog.require('mcore.players');
goog.require('mcore.players.FlashPlayer');

var dom = goog.dom;
var $ = dom.getElement;
var stubs;
var FLOWPLAYER_URL = '../../third-party/flowplayer-3.2.3.swf';
var YOUTUBE_URL = 'http://youtube.com/v/iDe4v318f64';

var setUp = function() {
  stubs = new goog.testing.PropertyReplacer();
};
var tearDown = function() {
  stubs.reset();
};

var testRender = function() {
  stubs.replace(goog.userAgent.flash, 'HAS_FLASH', true);
  stubs.replace(goog.userAgent.flash, 'VERSION', '10.0');

  var element = $('player-render-container');
  var player = new mcore.players.FlashPlayer(FLOWPLAYER_URL, 560, 315, {
    'config': goog.json.serialize({
      'playlist': [
        {'url': './media/mediacore-ipod.mp4'}
      ]
    })
  });

  var canPlay = false;
  goog.events.listenOnce(player, mcore.players.EventType.CAN_PLAY, function() {
    canPlay = true;
  });

  waitForEvent(player, mcore.players.EventType.CAN_PLAY, function() {});
  waitForCondition(
    function() { return player.isLoaded(); },
    function() {
      assert('The CAN_PLAY event should fire.', canPlay);
      player.dispose();
    },
    100,
    1500);

  player.render(element);
};


var testDecorate = function() {
  stubs.replace(goog.userAgent.flash, 'HAS_FLASH', true);
  stubs.replace(goog.userAgent.flash, 'VERSION', '10.0');

  var element = $('player-decorate-container');
  var player = new mcore.players.FlashPlayer(FLOWPLAYER_URL, 560, 315, {
    'config': goog.json.serialize({
      'playlist': [
        {'url': './media/mediacore-ipod.mp4'}
      ]
    })
  });

  var canPlay = false;
  goog.events.listenOnce(player, mcore.players.EventType.CAN_PLAY, function() {
    canPlay = true;
  });

  waitForEvent(player, mcore.players.EventType.CAN_PLAY, function() {});
  waitForCondition(
    function() { return player.isLoaded(); },
    function() {
      assert('The CAN_PLAY event should fire.', canPlay);
      player.dispose();
    },
    100,
    1500);

  player.decorate(element);
};


var testNoFlashSupport = function() {
  stubs.replace(goog.userAgent.flash, 'HAS_FLASH', false);
  stubs.replace(goog.userAgent.flash, 'VERSION', '');

  var player = new mcore.players.FlashPlayer(FLOWPLAYER_URL, 560, 315, {
    'config': goog.json.serialize({
      'playlist': [
        {'url': './media/mediacore-ipod.mp4'}
      ]
    })
  });

  waitForEvent(player, mcore.players.EventType.NO_SUPPORT, function() {
    player.dispose();
  });

  player.render();
};


var testOldFlashVersion = function() {
  stubs.replace(goog.userAgent.flash, 'HAS_FLASH', true);
  stubs.replace(goog.userAgent.flash, 'VERSION', '7.0');

  var player = new mcore.players.FlashPlayer(FLOWPLAYER_URL, 560, 315, {
    'config': goog.json.serialize({
      'playlist': [
        {'url': './media/mediacore-ipod.mp4'}
      ]
    })
  });

  waitForEvent(player, mcore.players.EventType.NO_SUPPORT, function() {
    player.dispose();
  });

  player.render();
};


var testCanPlayYoutubeVideosOnIPhone = function() {
  stubs.replace(goog.userAgent.flash, 'HAS_FLASH', false);
  stubs.replace(goog.userAgent.flash, 'VERSION', '');
  stubs.replace(goog.userAgent.product, 'IPHONE', true);

  var player = new mcore.players.FlashPlayer(YOUTUBE_URL, 560, 315);

  var canPlay = false;
  goog.events.listenOnce(player, mcore.players.EventType.CAN_PLAY, function() {
    canPlay = true;
  });

  waitForEvent(player, mcore.players.EventType.CAN_PLAY, function() {});
  waitForCondition(
    function() { return player.isLoaded(); },
    function() {
      assert('The CAN_PLAY event should fire.', canPlay);
      assert('Tag must be <embed> for YouTube to work on iPhones.',
             player.getContentElement().tagName == 'EMBED');
      player.dispose();
    },
    100,
    1500);

  player.render();
};


var testCase = new goog.testing.ContinuationTestCase();
testCase.autoDiscoverTests();
G_testRunner.initialize(testCase);

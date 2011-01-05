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
goog.require('mcore.players.JWPlayer');

var dom = goog.dom;
var $ = dom.getElement;
var stubs;

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

  var opts = {
    'file': './media/mediacore-ipod.mp4',
    'height': 315,
    'width': 560,
    'image': '/images/media/newl.jpg',
    'players': [
      {'type': 'html5'},
      {'type': 'flash', 'src': '/scripts/third-party/jw_player/player.swf'},
      {'type': 'download'}
    ],
    'autostart': false,
    'provider': 'video'
  };

  var player = new mcore.players.JWPlayer(opts);
  player.render(element);
};


var testCase = new goog.testing.ContinuationTestCase();
testCase.autoDiscoverTests();
G_testRunner.initialize(testCase);


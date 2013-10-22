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


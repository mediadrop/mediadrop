/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.require('goog.dom');
goog.require('goog.testing.ContinuationTestCase');

goog.require('goog.testing.jsunit');
goog.require('mcore.players');

goog.require('mcore.players.Html5Player');

var dom = goog.dom;

/**
 * Assert the given HTML contains all the same tags and attributes,
 * regardless of what order the attributes appear in.
 */
var assertHtmlEquivalent = function(expectedElement, observedElement) {
  var getElementPartsList = function(element) {
    var html = dom.getOuterHtml(expectedElement).replace(/>\s+</g, '><');
    var tags = html.split(/><\/?/g);
    var parts = [];
    for (var i = 0; i < tags.length; i++) {
      parts.push(tags[i].replace(/[><]/, '').split(' '));
    }
    return parts;
  };
  var expectedHtmlParts = getElementPartsList(expectedElement);
  var observedHtmlParts = getElementPartsList(observedElement);
  assertEquals(expectedHtmlParts.length, observedHtmlParts.length);
  for (var i = 0; i < expectedHtmlParts.length; i++) {
    var expectedTagParts = expectedHtmlParts[i];
    var observedTagParts = observedHtmlParts[i];
    assertSameElements(expectedTagParts, observedTagParts);
  }
};


var testCreateVideoDomWithSingleSrcAttribute = function() {
  var comparisonClassName = 'mp4-src';
  var comparisonEl = dom.getElementsByClass(comparisonClassName)[0];
  assertNotUndefined('Missing a video.' + comparisonClassName + ' DOM element ' +
                     'to check our rendered result against.',
                     comparisonEl);

  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {
    'class': comparisonClassName,
    'src': './media/mediacore-ipod.mp4',
    'controls': true,
    'width': 320,
    'height': 180
  });
  player.render(document.body);

  assertHtmlEquivalent(comparisonEl, player.getElement());
  dom.removeNode(comparisonEl);
  dom.removeNode(player.getElement());
};


var testCreateVideoDomWithMultipleSources = function() {
  var comparisonClassName = 'many-sources';
  var comparisonEl = dom.getElementsByClass(comparisonClassName)[0];
  assertNotUndefined('Missing a video.' + comparisonClassName + ' DOM element ' +
                     'to check our rendered result against.',
                     comparisonEl);

  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {
    'class': comparisonClassName,
    'controls': true,
    'width': 320,
    'height': 180
  }, [
    {'src': './media/mediacore-ipod.mp4', 'type': 'video/mp4'},
    {'src': './media/mediacore-theora.ogg', 'type': 'video/ogg'},
    {'src': './media/mediacore-vp8.webm', 'type': 'video/webm'}
  ]);
  player.render(document.body);

  assertHtmlEquivalent(comparisonEl, player.getElement());
  dom.removeNode(comparisonEl);
  dom.removeNode(player.getElement());
};


var testNoSupportSrcEventWithInvalidSrcAttr = function() {
  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO,
      {'src': './media/doesnotexist.xyz'});
  waitForEvent(player, mcore.players.EventType.NO_SUPPORTED_SRC, function() {
    dom.removeNode(player.getElement());
  });
  player.render(document.body);
};


var testNoSupportSrcEventWithInvalidSrcTag = function() {
  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {}, [
    {'src': './media/doesnotexist.xyz'}
  ]);
  waitForEvent(player, mcore.players.EventType.NO_SUPPORTED_SRC, function() {
    dom.removeNode(player.getElement());
  });
  player.render(document.body);
};


var testNoSupportSrcEventWithInvalidTypeAttr = function() {
  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {}, [
    {'src': './media/doesnotexist.xyz', 'type': 'video/nonexistent'}
  ]);
  waitForEvent(player, mcore.players.EventType.NO_SUPPORTED_SRC, function() {
    dom.removeNode(player.getElement());
  });
  player.render(document.body);
};


var testNoSupportSrcEventWithMultipleVariedSources = function() {
  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {
    'id': 'testNoSupportSrcEventWithMultipleVariedSources',
    'controls': true,
    'width': 320,
    'height': 180
  }, [
    {'src': './media/doesnotexist.ogv', 'type': 'video/ogg'},
    {'src': './media/doesnotexist.xyz', 'type': 'video/mp4'},
    {'src': './media/doesnotexist2.xyz'}
  ]);
  var eventFired = false;
  goog.events.listen(player, mcore.players.EventType.NO_SUPPORTED_SRC, function(e) {
    eventFired = true;
  });
  waitForCondition(
      function() { return eventFired; },
      function() {
        assert('Fired!', eventFired);
        dom.removeNode(player.getElement());
      },
      100,
      2000);
  player.render(document.body);
};

var testCanPlayEventWithMultipleSources = function() {
  var player = new mcore.players.Html5Player(mcore.players.MediaType.VIDEO, {
    'id': 'testPlayEventWithMultipleSources',
    'controls': true,
    'width': 320,
    'height': 180
  }, [
    {'src': './media/mediacore-ipod.mp4', 'type': 'video/mp4'},
    {'src': './media/mediacore-theora.ogg', 'type': 'video/ogg'},
    {'src': './media/mediacore-vp8.webm', 'type': 'video/webm'}
  ]);
  var eventFired = false;
  goog.events.listen(player, mcore.players.EventType.CAN_PLAY, function(e) {
    eventFired = true;
  });
  waitForCondition(
      function() { return eventFired; },
      function() {
        assert('Fired!', eventFired);
      },
      100,
      2000);
  player.render(document.body);
};


var testCase = new goog.testing.ContinuationTestCase();
testCase.autoDiscoverTests();
G_testRunner.initialize(testCase);

/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.likes');
goog.provide('mcore.likes.LikeThis');

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.net.XhrIo');
goog.require('goog.string');
goog.require('goog.ui.Component');



/**
 * A simple UI widget for rating up a Media item.
 *
 * This Component provides no render() method. Instead, it decorates
 * an anchor tag from the document, and uses the anchor's href as the
 * POST URL to log the rating.
 *
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.likes.LikeThis = function(opt_domHelper) {
  goog.base(this, opt_domHelper);
};
goog.inherits(mcore.likes.LikeThis, goog.ui.Component);


/**
 * Attach an onClick event to the element when it's decorated.
 *
 * This method is called internally when you call:
 *     var component = LikeThis();
 *     component.decorate(element);
 */
mcore.likes.LikeThis.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  this.getHandler().listenOnce(this.getElement(),
      goog.events.EventType.CLICK,
      this.onClick);
};


/**
 * Handle the user clicking the like-this button.
 * @param {!goog.events.Event} e The click event.
 * @protected
 */
mcore.likes.LikeThis.prototype.onClick = function(e) {
  e.preventDefault();

  // Assume the likes will be incremented successfully, replace the button now.
  var element = this.getElement();
  var dom = this.dom_;
  var likes = Number(dom.getTextContent(element.firstChild)) + 1;
  var labelTag = dom.getFirstElementChild(element);
  var newElement = dom.createDom('span', element.className,
      likes + ' ', labelTag);
  dom.replaceNode(newElement, element);

  // Dispatch the request to the server in the background
  var xhr = new goog.net.XhrIo();
  this.getHandler().listen(xhr,
      goog.net.EventType.COMPLETE,
      this.onSaveComplete);
  xhr.send(element.href, undefined, undefined,
      {'X-Requested-With': 'XMLHttpRequest'});
};


/**
 * Update the DOM to reflect the new number of likes.
 * @param {!goog.events.Event} e The XhrIo Event.
 * @protected
 */
mcore.likes.LikeThis.prototype.onSaveComplete = function(e) {
  var xhr = /** @type {goog.net.XhrIo} */ (e.target);
  var likes = xhr.getResponseText() + ' ';
  this.dispose();
};

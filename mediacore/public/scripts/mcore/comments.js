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

goog.provide('mcore.comments');
goog.provide('mcore.comments.CommentForm');

goog.require('goog.dom');
goog.require('goog.dom.classes');
goog.require('goog.dom.forms');
goog.require('goog.fx.dom.Fade');
goog.require('goog.style');
goog.require('goog.ui.Component');
goog.require('goog.ui.LabelInput');
goog.require('mcore.fx.SlideIntoView');
goog.require('mcore.net.FormXhrIo');



/**
 * Post Comment Form Component
 *
 * This component is very simple in that it simply creates a child
 * goog.ui.LabelInput for each label/field combination when decorate()
 * is called.
 *
 * This is defines as a component, and not a simple function, so that
 * it may be expanded to allow Ajax posting.
 *
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.comments.CommentForm = function(opt_domHelper) {
  goog.base(this, opt_domHelper);
  this.fade_ = null;
};
goog.inherits(mcore.comments.CommentForm, goog.ui.Component);


/**
 * Replace <label> inputs with goog.ui.LabelInput.
 * @param {Element} element The form element to decorate.
 */
mcore.comments.CommentForm.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
  var labels = this.dom_.getElementsByTagNameAndClass('label', undefined,
      element);
  goog.array.forEach(labels, function(label) {
    var labelText = this.dom_.getTextContent(label);
    var labelDiv = label.parentNode;
    var fieldDiv = this.dom_.getNextElementSibling(labelDiv);
    var field = this.dom_.getFirstElementChild(fieldDiv);
    var newLabel = new goog.ui.LabelInput(labelText);
    this.addChild(newLabel);
    newLabel.decorate(field);
    this.dom_.removeNode(labelDiv);
  }, this);
};


/**
 * Setup the form submit event when the form is decorated.
 */
mcore.comments.CommentForm.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  this.getHandler().listen(this.getElement(),
      goog.events.EventType.SUBMIT,
      this.handleSubmit);
};


/**
 * Submit the form with XHR.
 * @param {!goog.events.Event} e Form submit event.
 */
mcore.comments.CommentForm.prototype.handleSubmit = function(e) {
  e.preventDefault();
  var form = /** @type {HTMLFormElement} */ (this.getElement());
  var xhr = new mcore.net.FormXhrIo(form);
  this.getHandler().listenOnce(xhr, goog.net.EventType.COMPLETE,
      this.handleSubmitComplete);
  xhr.send();
  this.setFormEnabled(false);
};


/**
 * Handle the XHR response.
 * @param {!goog.events.Event} e Form submit event.
 */
mcore.comments.CommentForm.prototype.handleSubmitComplete = function(e) {
  var xhr = e.target;
  if (xhr.isSuccess()) {
    var commentHtml = xhr.getResponseJson()['comment'];
    if (commentHtml) {
      var fragment = this.dom_.htmlToDocumentFragment(commentHtml);
      var liElement = this.dom_.getFirstElementChild(fragment);
      this.injectComment(liElement);
    } else {
      this.injectMessage(xhr.getResponseJson()['message']);
    }
    this.setFormValues({});
  } else if (xhr.isUserError()) {
    this.displayUserErrors(xhr.getUserErrors());
  }
  this.setFormEnabled(true);
};


/**
 * Change the child LabelInput's to use the values from the given object.
 * @param {Object=} values A mapping of field names to values or null.
 */
mcore.comments.CommentForm.prototype.setFormValues = function(values) {
  // XXX: This depends on the fact that we registered goog.ui.LabelInput's
  //      in enterDocument.
  this.forEachChild(function(child) {
    var name = child.getElement().name;
    var value = values && name in values ? values[name] : '';
    if (child.getValue() != value) {
      child.setValue(value);
    }
  });
};


/**
 * Enable or disable the form with an opacity fade animation.
 * @param {!boolean} enable To go on or off.
 */
mcore.comments.CommentForm.prototype.setFormEnabled = function(enable) {
  goog.dom.forms.setDisabled(this.getElement(), !enable);
  if (this.fade_) {
    this.fade_.dispose();
  }
  var opacityAfter = enable ? 1 : 0.5;
  var opacityNow = goog.style.getOpacity(this.getElement());
  if (goog.isString(opacityNow)) {
    opacityNow = 1;
  }
  this.fade_ = new goog.fx.dom.Fade(this.getElement(), opacityNow,
      opacityAfter, 100);
  this.fade_.play();
};


/**
 * Take the element and inject it into the first .comment-list on the page.
 * @param {Element} element An element to append.
 */
mcore.comments.CommentForm.prototype.injectComment = function(element) {
  element.style.display = 'none';
  var noComments = this.dom_.getElement('no-comments');
  if (noComments) {
    this.dom_.removeNode(noComments);
  }
  var list = this.dom_.getElement('comments-list');
  this.dom_.appendChild(list, element);
  var slide = new mcore.fx.SlideIntoView(element, 250);
  slide.play();
};


/**
 * Display an error message next to the associated field.
 * @param {Object} errors Field names and their error message.
 */
mcore.comments.CommentForm.prototype.displayUserErrors = function(errors) {
  var form = this.getElement();
  for (var name in errors) {
    var field = form.elements[name];
    var errorDiv = this.dom_.getPreviousElementSibling(field);
    if (!errorDiv || !goog.dom.classes.has(errorDiv, 'field-error')) {
      errorDiv = this.dom_.createDom('div', 'field-error');
      this.dom_.insertSiblingBefore(errorDiv, field);
    }
    this.dom_.setTextContent(errorDiv, errors[name]);
  }
};


/**
 * Notify the user that their comment is awaiting moderation, etc.
 * @param {string} message A user-friendly message.
 */
mcore.comments.CommentForm.prototype.injectMessage = function(message) {
  // FIXME: Display a message in the DOM, not an alert.
  alert(message);
};

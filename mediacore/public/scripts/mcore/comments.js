/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.comments');
goog.provide('mcore.comments.CommentForm');

goog.require('goog.dom');
goog.require('goog.dom.classes');
goog.require('goog.dom.forms');
goog.require('goog.dom.TagName');
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
};
goog.inherits(mcore.comments.CommentForm, goog.ui.Component);


/**
 * Fade effect used when the form is disabled while being submitted.
 * @type {goog.fx.Animation}
 */
mcore.comments.CommentForm.prototype.fade_ = null;


/**
 * Replace <label> inputs with goog.ui.LabelInput.
 * @param {Element} formElement The form element to decorate.
 */
mcore.comments.CommentForm.prototype.decorateInternal = function(formElement) {
  goog.base(this, 'decorateInternal', formElement);
  var labels = this.dom_.getElementsByTagNameAndClass('label', undefined,
      formElement);
  goog.array.forEach(formElement.elements, function(field) {
    if (field.tagName == goog.dom.TagName.INPUT || field.tagName == goog.dom.TagName.TEXTAREA) {
      var fieldDiv = field.parentNode;
      var labelDiv = this.dom_.getPreviousElementSibling(fieldDiv);
      var label = this.dom_.getFirstElementChild(labelDiv);
      var labelText = this.dom_.getTextContent(label);
      var newLabel = new goog.ui.LabelInput(labelText);
      this.addChild(newLabel, false);
      newLabel.decorate(field);
      this.dom_.removeNode(labelDiv);
    }
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
  // In most browsers the label is stripped out by a form on submit event,
  // but for some reason that isn't working in IE7. We manually build the
  // POST content using the goog.ui.LabelInput API to workaround this issue.
  var dataSb = [];
  this.forEachChild(function(labelInput) {
    var key = labelInput.getElement().name;
    var value = labelInput.getValue();
    dataSb.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
  });
  var data = dataSb.join('&');
  xhr.send(data);
  this.removeUserErrors();
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
  goog.dispose(this.fade_);
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
  var counter = this.dom_.getElement('mcore-comments-counter');
  if (counter) {
    var count = Number(this.dom_.getTextContent(counter)) + 1;
    this.dom_.setTextContent(counter, String(count));
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
    var errorDiv = this.dom_.createDom('div', 'field-error', errors[name]);
    this.dom_.insertSiblingBefore(errorDiv, field);
  }
};


/**
 * Dispose of all user error messages.
 */
mcore.comments.CommentForm.prototype.removeUserErrors = function() {
  var form = this.getElement();
  var errorDivs = this.dom_.getElementsByClass('field-error', form);
  goog.array.forEach(errorDivs, function(elem) {
    this.dom_.removeNode(elem);
  }, this);
};


/**
 * Notify the user that their comment is awaiting moderation, etc.
 * @param {string} message A user-friendly message.
 */
mcore.comments.CommentForm.prototype.injectMessage = function(message) {
  // FIXME: Display a message in the DOM, not an alert.
  alert(message);
};

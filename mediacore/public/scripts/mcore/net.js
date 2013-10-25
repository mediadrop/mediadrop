/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.net');
goog.provide('mcore.net.FormXhrIo');

goog.require('goog.dom.forms');
goog.require('goog.events.Event');
goog.require('goog.events.EventTarget');
goog.require('goog.net.XhrIo');



/**
 * Specialized class for submitting forms via XMLHttpRequests.
 *
 * @param {HTMLFormElement} element The DOM form element.
 * @param {goog.net.XmlHttpFactory=} opt_xmlHttpFactory Factory to use when
 *     creating XMLHttpRequest objects.
 * @constructor
 * @extends {goog.net.XhrIo}
 */
mcore.net.FormXhrIo = function(element, opt_xmlHttpFactory) {
  goog.base(this, opt_xmlHttpFactory);

  /**
   * The form element to handle
   * @type {HTMLFormElement}
   * @private
   */
  this.element_ = element;

  /**
   * Memoized response JSON.
   * @type {Object|undefined|null}
   * @private
   */
  this.responseJson_ = undefined;
};
goog.inherits(mcore.net.FormXhrIo, goog.net.XhrIo);


/**
 * Send the Xhr using the form action and method.
 *
 * Our server depends on an 'X-Requested-With: XMLHttpRequest' header,
 * so we add it automatically here.
 *
 * @param {string=} opt_data Post data.
 * @param {Object=} opt_headers Extra headers.
 */
mcore.net.FormXhrIo.prototype.send = function(opt_data, opt_headers) {
  var url = this.getElement().action;
  var method = (this.getElement().method || 'GET').toUpperCase();
  var content = goog.isDef(opt_data) ? opt_data :
      goog.dom.forms.getFormDataString(this.getElement());
  var headers = opt_headers || {};
  headers['X-Requested-With'] = 'XMLHttpRequest';
  goog.base(this, 'send', url, method, content, headers);
};


/**
 * @override
 * @return {boolean} True if the request and form validation succeeded.
 */
mcore.net.FormXhrIo.prototype.isSuccess = function() {
  var success = goog.base(this, 'isSuccess');
  return success ? this.getResponseJson()['success'] : false;
};


/**
 * @return {boolean} True if the request succeeded but the form had errors.
 */
mcore.net.FormXhrIo.prototype.isUserError = function() {
  return mcore.net.FormXhrIo.superClass_.isSuccess.call(this) &&
      !this.getResponseJson()['success'];
};


/**
 * Return the error messages from the failed form validation.
 * @return {Object|undefined} Fields and their associated errors.
 */
mcore.net.FormXhrIo.prototype.getUserErrors = function() {
  return this.getResponseJson()['errors'];
};


/**
 * Return filtered values from the form validation, if any.
 * @return {Object|undefined} Fields and their new values.
 */
mcore.net.FormXhrIo.prototype.getValues = function() {
  return this.getResponseJson()['values'];
};


/**
 * Return the form element that is tied to this XhrIo.
 * @return {HTMLFormElement} The DOM form element.
 */
mcore.net.FormXhrIo.prototype.getElement = function() {
  return this.element_;
};


/**
 * Get the response and evaluate it as JSON from the Xhr object, and cache it.
 * Will only return correct result when called from the context of a callback.
 *
 * @param {string=} opt_xssiPrefix Optional XSSI prefix string to use for
 *     stripping of the response before parsing. This needs to be set only if
 *     your backend server prepends the same prefix string to the JSON response.
 * @return {Object|undefined} JavaScript object.
 */
mcore.net.FormXhrIo.prototype.getResponseJson = function(opt_xssiPrefix) {
  if (goog.isDef(this.responseJson_)) {
    return this.responseJson_;
  }
  return this.responseJson_ = goog.base(this, 'getResponseJson',
      opt_xssiPrefix);
};


/** @inheritDoc */
mcore.net.FormXhrIo.prototype.disposeInternal = function() {
  goog.base(this, 'disposeInternal');
  this.responseJson_ = null;
};

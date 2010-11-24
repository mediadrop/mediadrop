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

goog.provide('mcore.net');
goog.provide('mcore.net.FormXhrIo');

goog.require('goog.debug.Logger');
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
 * A reference to the XhrIo logger
 * @type {goog.debug.Logger}
 * @private
 */
mcore.net.FormXhrIo.prototype.logger_ =
    goog.debug.Logger.getLogger('mcore.net.FormXhrIo');


/**
 * Send the Xhr using the form action and method.
 *
 * Our server depends on an 'X-Requested-With: XMLHttpRequest' header,
 * so we add it automatically here.
 *
 * @param {Object=} opt_headers Extra headers.
 */
mcore.net.FormXhrIo.prototype.send = function(opt_headers) {
  var url = this.getElement().action;
  var method = (this.getElement().method || 'GET').toUpperCase();
  var content = goog.dom.forms.getFormDataString(this.getElement());
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

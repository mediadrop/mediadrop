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

goog.provide('mcore.players.Html5Player');

goog.require('goog.array');
goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.ui.Component');
goog.require('mcore.players');



/**
 * HTML5 Player.
 * Capable of rendering itself or decorating an existing HTMLMediaElement.
 * Provides a single NO_SUPPORTED_SRC event when all sources fail to play.
 * Provides a simple CAN_PLAY event, which fires once when we find a playable
 * source and enough of it is downloaded to begin playing.
 *
 * @param {mcore.players.MediaType=} opt_mediaType Audio or video. Necessary
 *     only for rendering.
 * @param {Object|Array.<string>|string=} opt_mediaAttrs If object, then a map
 *     of name-value pairs for attributes. If a string, then this is the
 *     className of the new element. If an array, the elements will be joined
 *     together as the className of the new element. Used only for rendering
 *     the HTMLMediaElement.
 * @param {Array.<mcore.players.Html5Player.Source>=} opt_sources Media sources
 *     to try playing, if there are multiple. Used for rendering.
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.players.Html5Player = function(opt_mediaType, opt_mediaAttrs,
    opt_sources, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * Audio or Video. Necessary only when rendering.
   * @type {mcore.players.MediaType|undefined}
   * @private
   */
  this.mediaType_ = opt_mediaType;

  /**
   * Attributes to render the HTMLMediaElement with.
   * @see goog.dom.createDom
   * @type {Object|Array.<string>|string|undefined}
   * @private
   */
  this.mediaAttrs_ = opt_mediaAttrs;

  /**
   * Media Sources. Can be undefined if decorating instead of rendering,
   * or if the only source is defined in this.mediaAttrs.
   * @type {Array.<mcore.players.Html5Player.Source>|undefined}
   * @private
   */
  this.sources_ = opt_sources;
};
goog.inherits(mcore.players.Html5Player, goog.ui.Component);


/**
 * Multiple media sources are specified as objects with these keys.
 * Only a 'src' is required.
 * @typedef {{src: string, type, media}}
 * */
mcore.players.Html5Player.Source;


/**
 * @return {boolean} True if the device supports HTML5 media elements.
 */
mcore.players.Html5Player.isSupported = function() {
  return goog.isDef(
      goog.dom.createDom(mcore.players.MediaType.VIDEO).canPlayType);
};


/**
 * The last resort playback source URI.
 * @type {string|undefined}
 * @private
 */
mcore.players.Html5Player.prototype.lastSrc_;


/**
 * Create a HTMLMediaElement, or rather a <video> or <audio> tag.
 * Called by {@link render()}.
 * @protected
 */
mcore.players.Html5Player.prototype.createDom = function() {
  goog.asserts.assertString(this.mediaType_);
  var element = this.dom_.createDom(this.mediaType_, this.mediaAttrs_);
  if (this.sources_) {
    var source;
    for (var i = 0; source = this.sources_[i]; i++) {
      this.dom_.append(element, this.dom_.createDom('source', source));
    }
  }
  this.decorateInternal(element);
};


/**
 * Decorate an Html5 Audio or Video element and filter out unplayable sources.
 * Called by {@link decorate()} and also {@link render()}.
 * @param {Element|string} element Element or ID to decorate.
 * @protected
 */
mcore.players.Html5Player.prototype.decorateInternal = function(element) {
  // Allow decoration by ID string
  element = this.dom_.getElement(element);
  if (element.tagName.toLowerCase() != mcore.players.MediaType.VIDEO &&
      element.tagName.toLowerCase() != mcore.players.MediaType.AUDIO) {
    element = this.dom_.getFirstElementChild(element);
  }
  goog.base(this, 'decorateInternal', element);
  this.testSupport();
};


/**
 * Dispatch events immediately if we know we don't support Html5 or any
 * of the given sources, otherwise attach events and wait for success/failure.
 */
mcore.players.Html5Player.prototype.testSupport = function() {
  if (mcore.players.Html5Player.isSupported()) {
    if (this.testSources()) {
      this.attachEvents();
    } else {
      this.dispatchEvent(mcore.players.EventType.NO_SUPPORTED_SRC);
    }
  } else {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORT);
  }
};


/**
 * Inspect the media tag and find our last resort for playable sources.
 * When errors occur, we'll know playback has failed completely when it
 * fails on the last source returned here.
 *
 * During this process any sources whose mimetype the browser can't play
 * are removed from the DOM. Hopefully this will prevent iPads from
 * failing to try anything but the first source listed, but I don't have
 * one to test with at the time of writing.
 *
 * @return {boolean} True if any of the sources are worth trying.
 * @protected
 */
mcore.players.Html5Player.prototype.testSources = function() {
  var media = /** @type {HTMLMediaElement} */ (this.getElement());
  // Check for a src attribute on the <video> tag
  if (media.src) {
    this.lastSrc_ = media.src;
  } else {
    // Check all the child source tags of <video>
    var sources = this.dom_.getElementsByTagNameAndClass('source',
        undefined, media);
    var source, maybePlayable;
    for (var i = 0; source = sources[i]; i++) {
      maybePlayable = !source.type || media.canPlayType(source.type);
      if (maybePlayable && maybePlayable != 'no') {
        this.lastSrc_ = source.src;
      } else {
        this.dom_.removeNode(source);
      }
    }
  }
  return !!this.lastSrc_;
};


/**
 * Attach event listeners.
 * To avoid a potential race condition by inserting the HTMLMediaElement into
 * the DOM prior to the error handler being in place, we are intentionally not
 * using {@link enterDocument} to attach these listeners.
 * @protected
 */
mcore.players.Html5Player.prototype.attachEvents = function() {
  this.getHandler().listen(this.getElement(),
                           goog.events.EventType.ERROR,
                           this.onError,
                           true /* fire in the capture phase (required) */);
  this.getHandler().listenOnce(this.getElement(),
                               mcore.players.EventType.CAN_PLAY,
                               this.onCanPlay);
};


/**
 * Handle an error event on the HTMLMediaElement or any of its child sources.
 *
 * At one point the HTML5 spec stated that each <source> should raise an
 * error when it cannot play, while now browsers are supposed to only throw
 * one error when all sources fail to play. WebKit does the former while
 * Firefox does the latter. For our purposes we only care when all sources
 * have failed.
 *
 * @param {goog.events.Event} e The error event.
 * @protected
 */
mcore.players.Html5Player.prototype.onError = function(e) {
  e.stopPropagation();
  // TODO: Explicitly check the error code and handle:
  //        element.error.code == MEDIA_SRC_NOT_SUPPORTED,
  //                              MEDIA_ERR_NETWORK,
  //                              MEDIA_ERR_DECODE,
  //                              MEDIA_ERR_ABORT
  //        element.networkState == NETWORK_NO_SOURCE
  if (// On Firefox this implies all sources have failed.
      !this.getElement().currentSrc ||
      // On WebKit with multiple <source> tags, this means they all failed.
      this.getElement().currentSrc.match(this.lastSrc_)
  ) {
    this.dispatchEvent(mcore.players.EventType.NO_SUPPORTED_SRC);
  }
};


/**
 * Fire a play event when the player successfully starts to play.
 * @param {goog.events.Event} e The canplay event.
 * @protected
 */
mcore.players.Html5Player.prototype.onCanPlay = function(e) {
  this.dispatchEvent(mcore.players.EventType.CAN_PLAY);
};


/** @inheritDoc */
mcore.players.Html5Player.prototype.disposeInternal = function() {
  this.lastSrc_ = undefined;
  this.mediaType_ = undefined;
  this.mediaAttrs_ = undefined;
  this.sources_ = undefined;
  goog.base(this, 'disposeInternal');
};


goog.exportSymbol('mcore.Html5Player', mcore.players.Html5Player);
goog.exportSymbol('mcore.Html5Player.isSupported',
    mcore.players.Html5Player.isSupported);
goog.exportSymbol('mcore.Html5Player.prototype.decorate',
    mcore.players.Html5Player.prototype.decorate);
goog.exportSymbol('mcore.Html5Player.prototype.render',
    mcore.players.Html5Player.prototype.render);

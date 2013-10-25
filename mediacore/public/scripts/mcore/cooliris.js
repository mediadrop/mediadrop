/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.Cooliris');

goog.require('goog.dom.classes');
goog.require('goog.events');
goog.require('goog.style');
goog.require('goog.ui.Component');
goog.require('goog.ui.media.FlashObject');
goog.require('goog.userAgent.flash');
goog.require('mcore.fx.SlideIntoView');



/**
 * Cooliris Widget.
 * @param {number} width Flash object width.
 * @param {number} height Flash object height.
 * @param {Object} flashVars Cooliris config vars.
 * @param {Element|string} opt_activeFeedButton Feed button to highlight
 *     initially, if any.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.Cooliris = function(width, height, flashVars, opt_activeFeedButton) {
  goog.base(this);

  /**
   * Cooliris Dimensions.
   * @type {Array.<number>}
   * @private
   */
  this.size_ = [width, height];

  /**
   * Cooliris Config.
   * @type {Object}
   * @private
   */
  this.flashVars_ = flashVars;

  /**
   * The currently displayed feed URL.
   * @type {string|null}
   * @private
   */
  this.feedUrl_ = flashVars['feed'];

  if (opt_activeFeedButton) {
    this.setActiveFeed(opt_activeFeedButton);
  }
};
goog.inherits(mcore.Cooliris, goog.ui.Component);


/**
 * The remotely-hosted SWF file to embed.
 * @type {string}
 */
mcore.Cooliris.FLASH_URL = 'http://apps.cooliris.com/embed/cooliris.swf';


/**
 * The current selected feed element
 * @type {Element}
 * @private
 */
mcore.Cooliris.prototype.activeFeedButton_ = null;


/**
 * Hilight the currently selected CoolIris feed
 * @param {string|Element} activeFeedID ID of feed to hilight.
 * @protected
 */
mcore.Cooliris.prototype.setActiveFeed = function(activeFeedID) {
  if (this.activeFeedButton_) {
    goog.dom.classes.remove(this.activeFeedButton_, 'cooliris-feed-active');
  }
  var active = this.dom_.getElement(activeFeedID);
  if (active) {
    goog.dom.classes.add(active, 'cooliris-feed-active');
  }
  this.activeFeedButton_ = active;
};


/**
 * Check that flash is installed before decorating and hide the element if not.
 * @inheritDoc
 * */
mcore.Cooliris.prototype.decorate = function(element) {
  if (goog.userAgent.flash.HAS_FLASH) {
    goog.base(this, 'decorate', element);
  } else {
    element.style.display = 'none';
  }
};


/**
 * Store references to all DOM elements we need for the life of this component.
 * @param {Element} element Element to decorate.
 * @protected
 */
mcore.Cooliris.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);

  this.nav_ = this.dom_.getElementsByClass('cooliris-nav', element)[0];
  this.navContents_ = this.dom_.getFirstElementChild(this.nav_);

  this.cats_ = this.dom_.getElementsByClass('cooliris-cats', this.nav_)[0];
  this.catsBtn_ = this.dom_.getElementsByClass('cooliris-cats-btn',
      this.nav_)[0];

  this.wall_ = this.dom_.getElementsByClass('cooliris-wall', element)[0];
  var flashObj = this.createFlashObject();
  this.addChild(flashObj, /* opt_render */ false);
  flashObj.render(this.wall_);
};


/**
 * Setup click handlers for the navigation bar that'll change the active feed.
 */
mcore.Cooliris.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  var eh = this.getHandler();
  eh.listen(this.nav_, goog.events.EventType.CLICK,
      this.handleNavClick_);
  eh.listen(this.catsBtn_, goog.events.EventType.CLICK,
      this.handleCategoriesToggle_);
};


/**
 * Create the flash object for the actual cooliris wall.
 * @return {!goog.ui.media.FlashObject} An instantiated UI component.
 * @protected
 */
mcore.Cooliris.prototype.createFlashObject = function() {
  var flashObj = new goog.ui.media.FlashObject(mcore.Cooliris.FLASH_URL,
      this.dom_);
  flashObj.addFlashVars(this.flashVars_);
  flashObj.setSize(this.size_[0], this.size_[1]);
  flashObj.setWmode(goog.ui.media.FlashObject.Wmodes.TRANSPARENT);
  flashObj.setBackgroundColor('transparent');
  flashObj.setAllowScriptAccess(
      goog.ui.media.FlashObject.ScriptAccessLevel.ALWAYS);
  return flashObj;
};


/**
 * Display a different feed when an element with a 'data-feed' attribute
 * is clicked on.
 * @param {goog.events.Event} e The click event.
 * @private
 */
mcore.Cooliris.prototype.handleNavClick_ = function(e) {
  var target = /** @type {Element} */ (e.target);
  var btn = this.dom_.getAncestorByTagNameAndClass(target, undefined,
      'cooliris-feed');
  if (btn) {
    var feed = btn.getAttribute('data-feed');
    if (feed && feed != this.feedUrl_) {
      goog.global['cooliris']['embed']['setFeedURL'](feed);
      this.feedUrl_ = feed;
      this.setActiveFeed(btn.id);
    }
  }
};


/**
 * Expand or contract the categories list on click.
 * @param {goog.events.Event} e The click event.
 * @private
 */
mcore.Cooliris.prototype.handleCategoriesToggle_ = function(e) {
  if (this.cats_.style.display == 'block') {
    this.cats_.style.display = 'none';
  } else {
    var fx = new mcore.fx.SlideIntoView(this.cats_, 250);
    this.getHandler().listen(fx, goog.fx.Animation.EventType.BEGIN,
        this.maybeMakeNavScrollable_);
    fx.play();
  }
  var arrow = goog.dom.getLastElementChild(this.catsBtn_);
  goog.dom.classes.toggle(arrow, 'down');
};


/**
 * Once the animation starts we can check to see if the full categories list
 * can be contained within the nav bar, and if necessary we enable scrolling.
 * @param {goog.fx.AnimationEvent} e The animation event.
 * @private
 */
mcore.Cooliris.prototype.maybeMakeNavScrollable_ = function(e) {
  // FIXME: This check always evaluates to true.
  var navBounds = goog.style.getBounds(this.nav_);
  var catBounds = goog.style.getBounds(this.cats_);
  if (!navBounds.contains(catBounds)) {
    this.navContents_.style.overflow = 'scroll';
    this.navContents_.style.overflowX = 'visible';
  }
};


/** @inheritDoc */
mcore.Cooliris.prototype.disposeInternal = function() {
  this.nav_ = null;
  this.navContents_ = null;
  this.cats_ = null;
  this.catsBtn_ = null;
  this.wall_ = null;
  this.flashVars_ = null;
  this.size_ = null;
  this.feedUrl_ = null;
};


goog.exportSymbol('mcore.Cooliris', mcore.Cooliris);
goog.exportSymbol('mcore.Cooliris.prototype.decorate',
    mcore.Cooliris.prototype.decorate);

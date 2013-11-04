/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore.excerpts');
goog.provide('mcore.excerpts.Excerpt');

goog.require('goog.fx.dom.ResizeHeight');
goog.require('goog.style');
goog.require('goog.ui.Component');



/**
 * Component to show an excerpt with a 'more' link for the fulltext.
 *
 * @param {goog.dom.DomHelper=} opt_domHelper Optional DOM helper.
 * @constructor
 * @extends {goog.ui.Component}
 */
mcore.excerpts.Excerpt = function(opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * Flag to indicate whether the excerpt or full is shown.
   * @type {!boolean}
   */
  this.isExcerptShown = false;

  /**
   * The element which contains just the excerpt text.
   * @type {Element}
   */
  this.excerpt = null;

  /**
   * A separate element which contains the full text.
   * @type {Element}
   */
  this.fulltext = null;

  /**
   * A rendered element which triggers a show/hide.
   * @type {Element}
   */
  this.toggleButton = null;

  /**
   * A lazy-loaded animation for sliding the full text height into view.
   * @type {goog.fx.dom.ResizeHeight}
   * @private
   */
  this.anim_ = null;
};
goog.inherits(mcore.excerpts.Excerpt, goog.ui.Component);


/**
 * The last known height of the excerpt element.
 * @type {number}
 */
mcore.excerpts.Excerpt.prototype.excerptHeight;


/**
 * The last known height of the fulltext element.
 * @type {number}
 */
mcore.excerpts.Excerpt.prototype.fulltextHeight;


/**
 * Parse the given element DOM into fulltext and excerpt elements.
 *
 * @param {Element} element The excerpt/fulltext wrapper element to decorate.
 */
mcore.excerpts.Excerpt.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
  var dom = this.dom_;
  this.fulltext = dom.getElementsByClass('mcore-excerpt-fulltext', element)[0];
  this.excerpt = dom.getElementsByClass('mcore-excerpt', element)[0];
  this.toggleButton = dom.createDom('span',
      'underline-hover mcore-excerpt-toggle clickable');
};


/**
 * Setup a toggle click event and do some quick calculations, just to be safe.
 *
 * Either excerptHeight or fulltextHeight will be overriden each time that
 * animateToggle() is called. The reason for this is that goog.style.getSize()
 * returns the wrong height when the element is hidden, it seems. We don't
 * know at this point whether the fulltext or the excerpt is shown, so we
 * just calculate both.
 */
mcore.excerpts.Excerpt.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  this.excerptHeight = goog.style.getSize(this.excerpt).height;
  this.fulltextHeight = goog.style.getSize(this.fulltext).height;
  this.getHandler().listen(this.toggleButton, goog.events.EventType.CLICK,
      this.onToggleClick_);
};


/**
 * Remove the toggle click event.
 */
mcore.excerpts.Excerpt.prototype.exitDocument = function() {
  goog.base(this, 'exitDocument');
  this.getHandler().unlisten(this.toggleButton, goog.events.EventType.CLICK,
      this.onToggleClick_);
};


/**
 * Instantly show the excerpt or the full text.
 * @param {boolean} show True to show the excerpt, False for fulltext.
 */
mcore.excerpts.Excerpt.prototype.showExcerpt = function(show) {
  this.excerpt.style.display = show ? 'block' : 'none';
  this.fulltext.style.display = show ? 'none' : 'block';
  this.injectToggle(show ? this.excerpt : this.fulltext);
  this.toggleButton.innerHTML = show ? '&raquo;' : '&laquo;';
  this.isExcerptShown = show;
};


/**
 * Animate the showing or hiding of the excerpt text.
 */
mcore.excerpts.Excerpt.prototype.animateToggle = function() {
  if (this.anim_) {
    this.anim_.dispose();
  }
  if (this.isExcerptShown) {
    // recalculate this while it's visible to ensure its accuracy
    this.excerptHeight = goog.style.getSize(this.excerpt).height;
    goog.style.setHeight(this.fulltext, this.excerptHeight);
    this.showExcerpt(false);
    this.anim_ = new goog.fx.dom.ResizeHeight(this.fulltext,
        this.excerptHeight, this.fulltextHeight, 250);
  } else {
    // recalculate this while it's visible to ensure its accuracy
    this.fulltextHeight = goog.style.getSize(this.fulltext).height;
    this.anim_ = new goog.fx.dom.ResizeHeight(this.fulltext,
        this.fulltextHeight, this.excerptHeight, 250);
    // we can't swap the elements immediately or there'd be nothing
    // to animate. wait until the animation completes, then swap them.
    this.getHandler().listenOnce(this.anim_,
        goog.fx.Animation.EventType.END,
        this.onShowExcerptAnimationEnd_);
  }
  // ensure animation events bubble up through this component
  this.anim_.setParentEventTarget(this);
  this.anim_.play();
};


/**
 * Inject the toggle button into the approximate ideal spot.
 *
 * @param {Element} element The element to inject the toggle in.
 * @protected
 */
mcore.excerpts.Excerpt.prototype.injectToggle = function(element) {
  var dom = this.dom_;
  var lastParagraph = dom.getLastElementChild(element);
  // TODO: Ensure lastParagraph is actually a paragraph.
  //       Otherwise, inject below.
  dom.appendChild(lastParagraph, dom.createTextNode(' '));
  dom.appendChild(lastParagraph, this.toggleButton);
};


/**
 * Animate the toggle when the button is clicked.
 *
 * This function is a simple proxy that is removed by the compiler.
 *
 * @param {goog.events.Event} e event.
 * @private
 */
mcore.excerpts.Excerpt.prototype.onToggleClick_ = function(e) {
  this.animateToggle();
};


/**
 * Once we're done animating from fulltext to excerpt, swap the elements.
 *
 * This function is a simple proxy that is removed by the compiler.
 *
 * @param {goog.events.Event} e event.
 * @private
 */
mcore.excerpts.Excerpt.prototype.onShowExcerptAnimationEnd_ = function(e) {
  this.showExcerpt(true);
};

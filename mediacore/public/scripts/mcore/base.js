/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under an MIT style license.
 * See LICENSE.txt in the main project directory, for more information.
 **/

goog.provide('mcore');
goog.provide('mcore.initPage');

goog.require('goog.array');
goog.require('goog.dom');
goog.require('goog.ui.LabelInput');
goog.require('mcore.Cooliris');
goog.require('mcore.comments.CommentForm');
goog.require('mcore.excerpts.Excerpt');
goog.require('mcore.players.Controller');
goog.require('mcore.players.FlashPlayer');
goog.require('mcore.players.JWPlayer');
goog.require('mcore.players.Html5Player');
goog.require('mcore.players.IframePlayer');
goog.require('mcore.players.SublimePlayer');
goog.require('mcore.players.MultiPlayer');


/**
 * Setup all the page elements. This should be called at the bottom of
 * the document.
 */
mcore.initPage = function() {
  var searchInput = goog.dom.getElement('nav-search-input');
  if (searchInput) {
    var searchLabel = new goog.ui.LabelInput(searchInput.alt);
    searchLabel.decorate(searchInput);
  }

  var mediaBox = goog.dom.getElement('media-box');
  if (mediaBox) {
    var commentForm = goog.dom.getElement('post-comment-form');
    if (commentForm) {
      var cf = new mcore.comments.CommentForm();
      cf.decorate(commentForm);
    }

    var excerpt = goog.dom.getElement('description-excerpt');
    if (excerpt &&
        goog.dom.getElementsByClass('mcore-excerpt', excerpt).length) {
      var exc = new mcore.excerpts.Excerpt();
      exc.decorate(excerpt);
      exc.showExcerpt(true);
    }
  }

  mcore.players.Controller.pageLoaded();
};


goog.exportSymbol('mcore.initPage', mcore.initPage);

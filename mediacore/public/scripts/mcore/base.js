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

goog.provide('mcore');
goog.provide('mcore.initPage');

goog.require('goog.array');
goog.require('goog.dom');
goog.require('mcore.excerpts.Excerpt');
goog.require('mcore.likes.LikeThis');


/**
 * Setup all the page elements. This should be called at the bottom of
 * the document.
 */
mcore.initPage = function() {
  var likeButtons = goog.dom.getElementsByTagNameAndClass('a', 'meta-likes');
  goog.array.forEach(likeButtons, function(element) {
    var like = new mcore.likes.LikeThis();
    like.decorate(element);
  });

  var mediaBox = goog.dom.getElement('media-box');
  if (mediaBox) {
    var excerpt = goog.dom.getElement('description-excerpt');
    if (excerpt &&
        goog.dom.getElementsByClass('mcore-excerpt', excerpt).length) {
      var exc = new mcore.excerpts.Excerpt();
      exc.decorate(excerpt);
      exc.showExcerpt(true);
    }
  }
};


goog.exportSymbol('mcore.initPage', mcore.initPage);

/**
 * This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
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
/**
 * NotifyComment injects a new comment into the
 * page to inform the user that their comment was
 * received.
 *
 * @author Melanie Wright <mel@simplestation.com>
 */
var NotifyComment = new Class({

	Extends: Options,

	options: {
		form: 'post-comment-form',
		injectRelativeSelector: 'div.comments h3',
		injectRelative: 'before',
		commentDivClass: 'no-comments',
		message: 'Thanks for your comment! We will post it just as soon as our moderator approves it.',
	},

	form: null,
	overTextMGR: null,
	errorFields: new Hash(),

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form);

		this.form.addEvent('submit', this.submitForm.bind(this));
	},

	submitForm: function(e){
		this.form.set('send', {onComplete: function(response) {
			this.injectComment(response);
		}.bind(this)});
		this.form.send();
		return false;
	},

	injectComment: function(json){
		json = json ? JSON.decode(json) : {};

		var errors = new Hash(json.success? {} : json.errors);

		// clear errors for elements that don't need them
		var correctedErrors = this.errorFields.filter(function(errorDiv, element) {
			return !errors.has(element);
		}.bind(this));
		
		correctedErrors.each(function(errorDiv, element){
			// clear div
			errorDiv.dispose();
			this.errorFields.erase(element);
		}.bind(this));

		if(!json.success) {
			// create new error divs for errors that don't have one yet
			errors.each(function(error, element){
				if (!this.errorFields.has(element)) {
					var errorDiv = new Element('div', {'class':'field-error', html:error});
					errorDiv.inject($(element).getParent(), 'after');
					this.errorFields.set(element, errorDiv);
				}
			}.bind(this));

			OverText.update();

			return;
		}

		var commentDiv = new Element('div', {'class': this.options.commentDivClass});
		var topDiv = new Element('div', {'class':'top'});
		var bodyDiv = new Element('div', {'class':'body', html: this.options.message});
		var bottomDiv = new Element('div', {'class':'bottom'});
		commentDiv.adopt(topDiv, bodyDiv, bottomDiv);
		commentDiv.inject($$(this.options.injectRelativeSelector)[0], this.options.injectRelative);

		// clear the form
		this.form.reset();
		OverText.update();
	}
});

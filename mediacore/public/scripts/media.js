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
var MetaHover = new Class({

	Implements: [Events, Class.Binds],

	Binds: ['toggle', 'hide'],

	initialize: function(wrapper){
		this.wrapper = $(wrapper);
		if (!this.wrapper) return;
		this.hover = this.wrapper.getElement('div.meta-hover').set('opacity', 0);
		this.btn = this.wrapper.getElement('.meta').addEvent('click', this.toggle);
		this.input = this.hover.getElement('input').addEvent('focus', function(e){
			e.target.select();
		});
		this.wrapper.addEvent('mouseleave', this.hide);
		this.hover.addEvent('mouseleave', this.hide);
	},

	toggle: function(e){
		if ($type(e) == 'event') e.stop();
		this.hover.setStyle('display', 'block').fade('toggle');
		this.fireEvent('toggle');
		return this;
	},

	hide: function(e){
		if ($type(e) == 'event') e.stop();
		this.hover.fade('out');
		return this;
	}

});

var ShareHover = new Class({

	Extends: MetaHover,

	initialize: function(wrapper){
		this.parent(wrapper);
		this.hover.getElements('a').addEvent('click', function(e){
			if (/^mailto:/.test(e.target.href)) return true;
			window.open(e.target.href);
			return false;
		});
	}

});

window.addEvent('domready', function(){
	var excerpt = $('desc-excerpt');
	if (excerpt) {
		var full = $('desc-full'), fullY = full.getDimensions().y;
		full.hide();
		excerpt.show();
		var more = new Element('span', {id: 'desc-more', 'class': 'underline-hover', text: 'more'}).addEvent('click', function(){
			full.setStyle('height', excerpt.getDimensions().y);
			excerpt.hide();
			full.show().tween('height', fullY);
		}).inject((excerpt.getLast() || excerpt).appendText(' '), 'bottom');
	}
	var embed = new MetaHover('embedthis');
	var share = new ShareHover('sharethis');
	embed.btn.addEvent('focus', share.hide);
	share.btn.addEvent('focus', embed.hide);
	$('likethis').addEvent('focus', share.hide).addEvent('focus', embed.hide);
	var c = $$('li.comment:first-child cite a');
	if (c.length) c[0].addEvent('focus', share.hide).addEvent('focus', embed.hide);
	$('name').addEvent('focus', share.hide).addEvent('focus', embed.hide);
});

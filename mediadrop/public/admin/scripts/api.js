/**
 * This file is a part of MediaDrop (http://www.mediadrop.net),
 * Copyright 2009-2013 MediaDrop contributors
 * For the exact contribution history, see the git revision log.
 * The source code contained in this file is licensed under the GPLv3 or
 * (at your option) any later version.
 * See LICENSE.txt in the main project directory, for more information.
 **/

var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
var elem = null;
generate_random_string = function(){
	var string_length = 20;
	var randomstring = '';
	for (var i=0; i<string_length; i++) {
		var rnum = Math.floor(Math.random() * chars.length);
		randomstring += chars.substring(rnum,rnum+1);
	};
	elem.set('value', randomstring);
}
window.addEvent('domready', function() {
	elem = $('key_api_secret_key');
	var gen = new Element('a', {'href': '#', 'text': mcore_api_generate_text, 'id':'generate_key'})
			.addEvent('click',  generate_random_string, [elem]);
	elem.set('styles',{'width': elem.getScrollSize().x-100});
	gen.inject(elem, 'after');
});

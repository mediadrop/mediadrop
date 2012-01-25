/**
 * This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
 * The source code contained in this file is licensed under the GPL.
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

window.addEvent('domready', function(){
	var button = $('edit-album-art').addEvent('click', function(){
		SqueezeBox.fromElement($('album-art-wrapper'), {handler: 'clone'});
		$('album_art').browse();
	});
});

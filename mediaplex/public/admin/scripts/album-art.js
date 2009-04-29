window.addEvent('domready', function(){
	var button = $('edit-album-art').addEvent('click', function(){
		SqueezeBox.fromElement($('album-art-box'), {
			handler: 'fittedClone'
		});
	});

/*$('album-art-wrapper').getParent('form').addEvent('submit', function(){
		
	});*/
});

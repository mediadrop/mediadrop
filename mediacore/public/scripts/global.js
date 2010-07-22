window.addEvent('domready', function(){
	var searchLbl = $('nav-search-input');
	if (searchLbl) var l = new OverText(searchLbl, {wrap: true, positionOptions: {x: 14, y: 12}});
});

window.addEvent('domready', function(){
	var likeBtns = $$('a.meta-likes').addEvent('click', function(e){
		var btn = $(new Event(e).stop().target);
		if (btn.get('tag') != 'a') {
            btn = btn.getParent('a');
        }
		var req = new Request({url: btn.get('href'), onComplete: function(resp) {
			if (resp) {
                new Element('span', {'html': resp.toInt() + ' <strong>' + btn.getFirst('strong').get('html') + '</strong>',
                    'class': btn.className}).replaces(btn);
            }
		}}).send();
	});
});

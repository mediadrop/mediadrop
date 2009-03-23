/**
 * Insert class="rounded" for each table and wrap tables in:
 *
 *<div class="rounded">
 *	<div class="rounded-top-beige">
 *		<div class="rounded-top-left"></div>
 *		<div class="rounded-top-right"></div>
 *	</div>
 *		
 *(if table has tfoot chooses beige)
 *	<div class="rounded-bottom-white">
 *		<div class="rounded-bottom-left"></div>
 *		<div class="rounded-bottom-right"></div>
 *	</div>
 *</div>
*/
var RoundedCorners = new Class({
	initialize: function() {
		var tables = $$('table');
		tables.each(function(t) {
			t.addClass('rounded-table');
			var wrappingDiv = new Element('div', {
				'class': 'rounded'
			});
			var topDiv = new Element('div', {
				'class': 'rounded-top-beige'
			});
			var topLDiv = new Element('div', {
				'class': 'rounded-top-left'
			});
			var topRDiv = new Element('div', {
				'class': 'rounded-top-right'
			});
			var bottomClass = t.getChildren('tfoot').length > 0? 'rounded-bottom-beige' : 'rounded-bottom-white';
			var bottomDiv = new Element('div', {
				'class': bottomClass
			});
			var bottomLDiv = new Element('div', {
				'class': 'rounded-bottom-left'
			});
			var bottomRDiv = new Element('div', {
				'class': 'rounded-bottom-right'
			});

			wrappingDiv.wraps(t);
			topDiv.inject(wrappingDiv, 'top');
			bottomDiv.inject(wrappingDiv, 'bottom');
			topLDiv.inject(topDiv);
			topRDiv.inject(topDiv);
			bottomLDiv.inject(bottomDiv);
			bottomRDiv.inject(bottomDiv);
		});
	}
});
window.addEvent('domready', function(){
	var rc = new RoundedCorners();
});

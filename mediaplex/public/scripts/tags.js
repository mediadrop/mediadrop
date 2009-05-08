var TagSlider = new Class({
	Extends: Options,
	options: {
		container: 'mediaplex-tags',
		fxOptions: {transition: 'quad:in:out'},
		button: 'mediaplex-ctrls-tags',
		slideWrapperStyles: {clear: 'both'}
	},

	container: null,
	button: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.container = $(this.options.container).set('slide', this.fxOptions);
		this.container.slide('hide');
		if (this.options.slideWrapperStyles) {
			this.container.get('slide').wrapper.setStyles(this.options.slideWrapperStyles);
		}
		this.button = $(this.options.button).addEvent('click', this.slideToggle.bind(this));
	},

	slideToggle: function(){
		this.button.toggleClass('active');
		this.container.slide('toggle');
		return false;
	}
});

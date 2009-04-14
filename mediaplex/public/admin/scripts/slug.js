var SlugManager = new Class({

	Extends: Options,

	options: {
		slugField: 'slug',
		slugWrapper: 'slug-container',
		masterField: 'title',
		stub: 'slug-stub',
		stubWrapper: 'slug-stub-wrapper',
		stubParent: 'title-label',
		editSlugBtn: 'slug-edit'
	},

	slugField: null,
	slugWrapper: null,
	masterField: null,
	stub: null,
	stubWrapper: null,
	stubField: null,

	initialize: function(opts){
		this.setOptions(opts);

		this.slugField = $(this.options.slugField);
		this.slugWrapper = $(this.options.slugWrapper);
		this.masterField = $(this.options.masterField);

		this._hide(this.slugWrapper, true);

		var slug = this.slugField.get('value');
		this.stub = new Element('span', {text: slug, id: this.options.stub});
		this.stubField = new Element('input', {type: 'hidden', name: 'slug', value: slug});

		var editSlugBtn = new Element('span', {text: 'Edit', 'class': 'link', id: this.options.editSlugBtn});
		editSlugBtn.addEvent('click', this.showSlugField.bind(this));

		this.stubWrapper = new Element('div', {id: this.options.stubWrapper})
			.grab(new Element('span', {text: 'Slug:'})).appendText(' ')
			.grab(this.stub).appendText(' ')
			.grab(this.stubField)
			.grab(editSlugBtn)
			.inject($(this.options.stubParent), 'top');

		updateSlugFn = this.updateSlug.bind(this);
		this.masterField.addEvent('change', updateSlugFn);
		editSlugBtn.addEvent('click', function(){
			this.masterField.removeEvent('change', updateSlugFn);
		}.bind(this));
	},

	showSlugField: function(){
		this._hide(this.stubWrapper, true);
		this._hide(this.slugWrapper, false);
		this.stubField.destroy();
	},

	updateSlug: function(){
		var slug = this.slugify(this.masterField.get('value'));
		this.slugField.set('value', slug);
		this.stubField.set('value', slug);
		this.stub.set('text', slug);
	},

	_hide: function(field, flag){
		field.setStyle('display', (flag ? 'none' : 'block'));
	},

	slugify: function(title){
		return title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
	}
});

window.addEvent('domready', function(){
	smgr = new SlugManager();
});

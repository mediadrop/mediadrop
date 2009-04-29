var StatusForm = new Class({
	Extends: Options,

	options: {
		form: '',
		statusField: '',
		updateButton: ''
	},

	form: null,
	statusField: null,
	updateButton: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.updateStatus.bind(this));
		this.statusField = $(this.options.statusField);
		this.updateButton = $(this.options.updateButton);
	},

	saveStatus: function(e){
		this.form.get('send').addEvent('success', this.updateForm.bind(this)).send();
		return false;
	},

	updateForm: function(text){
		console.log(text);
		var resp = JSON.decode(text);
		console.log(resp);
	}
});

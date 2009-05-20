var StatusForm = new Class({
	Extends: Options,

	options: {
		form: 'update-status-form',
		submitReq: {noCache: true}
	},

	form: null,
	submitReq: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.saveStatus.bind(this));
	},

	saveStatus: function(){
		if (!this.submitReq) {
			var submitOpts = $extend({url: this.form.action}, this.options.submitReq);
			this.submitReq = new Request.HTML(submitOpts)
				.addEvent('success', this.updateForm.bind(this));
		}
		this.submitReq.send(this.form);
		return false;
	},

	updateForm: function(tree){
		var formContents = $$(tree).getChildren();
		this.form.empty().adopt(formContents);
	}
});

var StatusForm = new Class({
	Extends: Options,

	options: {
		form: 'update-status-form',
		statusList: 'status-list',
		updateButton: 'update-status',
		inProgressClass: 'status-list-inprogress',
		completeClass: 'status-list-complete',
		pendingClass: 'status-list-pending'
	},

	form: null,
	statusList: null,
	updateButton: null,

	initialize: function(opts){
		this.setOptions(opts);
		this.form = $(this.options.form).addEvent('submit', this.saveStatus.bind(this));
		this.form.get('send').addEvent('success', this.updateForm.bind(this));
		this.statusList = $(this.options.statusList);
		this.updateButton = $(this.options.updateButton);
	},

	saveStatus: function(){
		this.form.send();
		return false;
	},

	updateForm: function(resp){
		resp = JSON.decode(resp);
		var currStatus = this.statusList.getChildren('.' + this.options.inProgressClass)[0];
		currStatus.addClass(this.options.completeClass).removeClass(this.options.inProgressClass);
		currStatus.set('text', currStatus.get('text').replace('in progress', 'complete'));
		var nextStatus = currStatus.getNext();
		if (nextStatus) {
			nextStatus.addClass(this.options.inProgressClass).removeClass(this.options.pendingClass);
			nextStatus.set('text', nextStatus.get('text').replace('pending', 'in progress'));
			this.updateButton.set('value', resp.buttonText);
		} else {
			currStatus.set('text', 'published');
			this.updateButton.destroy();
		}
	}
});

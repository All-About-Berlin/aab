import { validateForm } from '/js/utils/form.mjs';

export default {
	data() {
		return {
			isLoading: false,
			notes: '',
			emailAddress: null, // Not named 'email' so userDefaultsMixin doesn't load it from localStorage
			subscribeToNewsletter: false,
			stages: [
				'start',
				'email',
				'finish',
				'error',
			],
			inputsToFocus: {
				email: () => this.$refs.emailInput.$el,
			},
		};
	},
	computed: {
		submittedOnDate(){
			return this.steps.application.date
				? new Date(this.steps.application.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })
				: null;
		},
		showFeedbackLink(){
			return !window.location.pathname.startsWith('/guides/immigration-office/wait-times');
		},
		showRestOfForm(){
			return this.steps.application.completed;
		},
		feedbackComplete(){
			return Object.values(this.steps).every(s => s.completed);
		},
	},
	methods: {
		async nextStage(){
			if(validateForm(this.$el)){
				if(this.stage === 'start'){
					this.goToStage((this.emailAddress || this.feedbackComplete) ? 'finish' : 'email');
				}
				else{
					this.goToStage('finish');
				}
			}
		},
		onStepCompletionChange(key){
			const changedStepIndex = Object.keys(this.steps).indexOf(key);
			Object.values(this.steps).forEach((step, index) => {
				if(index < changedStepIndex && this.steps[key].completed){
					step.completed = true;
				}
				if(index > changedStepIndex && !this.steps[key].completed){
					step.completed = false;
				}
			})
		},
		minimumStepDate(step){
			const stepList = Object.values(this.steps);
			const previousStep = stepList[stepList.indexOf(step) - 1];
			return previousStep?.date ?? null;
		},
	},
}

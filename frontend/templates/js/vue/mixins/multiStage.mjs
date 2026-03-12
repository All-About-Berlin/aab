import { validateForm } from '/js/utils/form.mjs';

export default {
	data: function () {
		return {
			stages: [],
			stageIndex: 0,
			inputsToFocus: {},
		}
	},
	computed: {
		stage(){
			return this.stages[this.stageIndex];
		},
	},
	methods: {
		goToStart(){
			this.stageIndex = 0;
		},
		nextStage(){
			if(validateForm(this.$el)){
				this.stageIndex += 1;
			}
		},
		previousStage(){
			this.stageIndex -= 1;
		},
		goToStage(stageName){
			this.stageIndex = this.stages.indexOf(stageName);
		}
	},
	watch: {
		stageIndex(newStageIndex){
			this.$nextTick(() => {
				// Focus on the first form item in the list when changing steps
				const inputToFocusFunction = this.inputsToFocus[this.stages[newStageIndex]];
				if(inputToFocusFunction){
					const inputToFocus = inputToFocusFunction();
					if(inputToFocus){
						inputToFocus.focus();
					}
				}
			});
		},
	}
}
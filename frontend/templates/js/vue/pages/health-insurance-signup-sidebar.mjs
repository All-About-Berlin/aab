import store from '/js/vue/pages/health-insurance-signup-store.mjs';

const STEPS = [
	{ key: 'start', label: 'Start' },
	{ key: 'occupation', label: 'Occupation' },
	{ key: 'situation', label: 'Job information' },
	{ key: 'contactInfo', label: 'Contact information' },
];

export default {
	data(){
		return { steps: STEPS };
	},
	computed: {
		stageIndex(){ return store.stageIndex; },
		maxProgress(){ return store.stages.length - 1; },
		currentStage(){ return store.stages[store.stageIndex]; },
	},
	template: `
		<div class="sidebar no-print" aria-label="Signup progress">
			<h2>Steps</h2>
			<progress
				aria-label="Form progress"
				:max="maxProgress"
				:value="stageIndex"></progress>
			<ol>
				<li
					v-for="step in steps"
					:key="step.key"
					:class="{ current: step.key === currentStage }">
					{{ step.label }}
				</li>
			</ol>
		</div>
	`,
};

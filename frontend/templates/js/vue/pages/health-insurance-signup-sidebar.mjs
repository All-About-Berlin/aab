import store from '/js/vue/pages/health-insurance-signup-store.mjs';

export default {
	computed: {
		stages(){
			return Object.fromEntries(
				Object.entries(store.sidebarStages)
					.filter(([k, s]) => s.enabled && s.label)
			);
		},
		currentStage(){
			return store.currentSidebarStage;
		},
		currentStageIndex(){
			return Object.keys(this.stages).findIndex(k => k === this.currentStage);
		},
		stageCount(){
			return Object.keys(this.stages).length;
		}
	},
	template: `
		<div class="sidebar no-print" aria-label="Signup progress">
			<h2>Steps</h2>
			<progress
				aria-label="Form progress"
				:max="stageCount - 1"
				:value="currentStageIndex"></progress>
			<ol>
				<li
					v-for="(stage, stageKey) in stages"
					:key="stageKey"
					:class="{ current: stageKey === currentStage }">
					{{ stage.label }}
				</li>
			</ol>
		</div>
	`,
};

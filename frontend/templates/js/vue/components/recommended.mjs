import { showTooltip } from '/js/components/tooltip.mjs';

export default {
	data() {
		return { showTooltip };
	},
	template: `
		<a target="_blank" class="recommended" aria-label="Recommended option" href="/glossary/Recommended" @click.prevent="showTooltip"></a>
	`,
}
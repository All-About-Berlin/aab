export default {
	props: {
		placeholder: String,
	},
	computed: {
		hasContent() {
			const slot = this.$slots.default?.[0];
			return slot?.tag || slot?.text?.trim();
		}
	},
	template: `
	<output :class="{placeholder: !hasContent}" :title="hasContent ? '' : 'This information is required'">
		<slot v-if="hasContent"></slot>
		<template v-else>{{ placeholder }}</template>
	</output>`,
}
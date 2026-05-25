import Glossary from '/js/vue/components/glossary.mjs';
import Vue from '/js/vue/vue.mjs';

export default function initializePriceTable() {
	window.addEventListener('DOMContentLoaded', () => {
		const el = document.querySelector('.price-table');
		if (!el) return;

		new Vue({
			el,
			components: {
				Glossary,
			},
			data() {
				return {
					recommendedOption: null,
				};
			},
		});
	});
}

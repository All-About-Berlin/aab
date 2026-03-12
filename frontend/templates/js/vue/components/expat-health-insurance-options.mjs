import Glossary from '/js/vue/components/glossary.mjs';
import Price from '/js/vue/components/price.mjs';
import healthInsuranceOptionsMixin from '/js/vue/mixins/healthInsuranceOptions.mjs';
import LogoFeather from '/js/vue/components/icons/logo-feather.mjs';
import LogoHansemerkur from '/js/vue/components/icons/logo-hansemerkur.mjs';

export default {
	mixins: [healthInsuranceOptionsMixin],
	components: {
		Glossary,
		Price,
		LogoFeather,
		LogoHansemerkur,
	},
	computed: {
		isExpatOnlyOption() {
			return (
				this.results.asList.filter(o => o.eligible && o.id !== 'other').length === 1
				&& this.results.asList[0].id === 'expat'
			);
		},
	},
	template: `
		<div class="health-insurance-options">
			<h2 v-if="!isExpatOnlyOption">Expat health insurance options</h2>
			<p v-if="!isExpatOnlyOption">
				These options are valid for a <glossary>National Visa</glossary> application.
				<template v-if="occupation === 'selfEmployed'">They might not be accepted when you <a target="_blank" href="/guides/renew-german-freelance-visa">renew your freelance visa</a>.</template>
			</p>
			<ul class="buttons list">
				<li>
					<a href="/out/feather-expats" target="_blank" class="recommended">
						<logo-feather/>
						<div>
							<h3>Feather</h3>
							<p>An English-speaking insurer from Berlin.</p>
						</div>
						<price :amount="optionPrice('expat', 'feather-basic')" per-month></price>
					</a>
				</li>
				<li>
					<a href="/out/hansemerkur-expats" target="_blank">
						<logo-hansemerkur></logo-hansemerkur>
						<div>
							<h3>HanseMerkur</h3>
							<p>A reliable German health insurer.</p>
						</div>
						<price :amount="optionPrice('expat', 'hansemerkur-basic')" per-month></price>
					</a>
				</li>
			</ul>
		</div>
	`
}
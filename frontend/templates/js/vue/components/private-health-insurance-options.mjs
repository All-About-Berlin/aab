import Eur from '/js/vue/components/eur.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import Price from '/js/vue/components/price.mjs';

import healthInsuranceOptionsMixin from '/js/vue/mixins/healthInsuranceOptions.mjs';

export default {
	components: {
		Eur,
		Glossary,
		Price,
	},
	mixins: [healthInsuranceOptionsMixin],
	methods: {
		option(planType) {
			return this.results.private.options.filter(o => o.id === planType)[0];
		},
	},
	template: `
		<div class="health-insurance-options">
			<h2>Private health insurance options</h2>
			<hr>
			<div class="two-columns private-cost">
				<div>
					<h3>Basic coverage</h3>
					<ul class="pros">
						<li>Covers all necessary healthcare</li>
					</ul>
					<ul class="cons">
						<li>High <glossary term="Selbstbeteiligung">deductible</glossary> (<eur :amount="option('basic').deductible"></eur>/year)</li>
						<li>No <glossary term="Krankentagegeld">sickness allowance</glossary></li>
					</ul>
					<price :amount="option('basic').total.personalContribution" per-month></price>
				</div>
				<div>
					<h3>Premium coverage</h3>
					<ul class="pros">
						<li>Covers the best available healthcare</li>
						<li>No <glossary term="Selbstbeteiligung">deductible</glossary></li>
						<li>Generous <glossary term="Krankentagegeld">sickness allowance</glossary></li>
					</ul>
					<price :amount="option('premium').total.personalContribution" per-month></price>
				</div>
			</div>

			<details class="cost-explanation">
				<summary>Cost explanation</summary>
				<p>These are two example plans. One is as cheap as possible. The other is as good as possible. It should give you an idea of the price range.</p>
				<details>
					<summary class="price-line">
						Base cost
						<price
							:from="option('basic').baseContribution"
							:to="option('premium').baseContribution"
							per-month></price>
					</summary>
					<p>This is the basic cost of your private health insurance.</p>
				</details>
				<details>
					<summary class="price-line">
						Sickness allowance
						<price
							:from="0"
							:to="option('premium').krankentagegeld"
							per-month></price>
					</summary>
					<p><glossary term="Krankentagegeld">Sickness allowance</glossary> is optional, but recommended. If you are too sick to work, you get paid <eur :amount="option('premium').krankentagegeldPayoutPerDay"></eur>. You can adjust this amount.</p>
				</details>
				<details>
					<summary class="price-line">
						Long-term care insurance
						<price :amount="option('premium').pflegeversicherung" per-month></price>
					</summary>
					<p>
						It pays for your healthcare when you are older. It's required.
					</p>
				</details>
				<details v-if="childrenCount">
					<summary class="price-line">
						Insurance for your {{ childOrChildren }}
						<price
							:from="option('basic').total.childrenCost"
							:to="option('premium').total.childrenCost"
							per-month></price>
					</summary>
					<p>
						With private health insurance, you must pay extra to cover your children.
					</p>
				</details>
				<details class="total" v-if="option('basic').total.employerContribution">
					<summary class="price-line">
						Your employer pays
						<price
							:from="option('basic').total.employerContribution"
							:to="option('premium').total.employerContribution"
							per-month></price>
					</summary>
					<p>Your employer pays half of your private health insurance. They pay no more than half the cost of public health insurance.</p>
				</details>
				<details class="total">
					<summary class="price-line highlighted">
						Your pay
						<price
							:from="option('basic').total.personalContribution"
							:to="option('premium').total.personalContribution"
							per-month></price>
					</summary>
					<p>This is what you pay every month for health insurance. This is a <glossary term="steuerlich absetzbar">tax-deductible</glossary> expense.</p>
				</details>
			</details>

			<hr>
			<p>These are just two plans. There are hundreds of other options. Let our expert find the best one for you. It's 100% free.</p>
		</div>
	`
}
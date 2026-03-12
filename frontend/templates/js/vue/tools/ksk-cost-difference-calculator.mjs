import Collapsible from '/js/vue/components/collapsible.mjs';
import Eur from '/js/vue/components/eur.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import Price from '/js/vue/components/price.mjs';
import { healthInsurance, taxes } from '/js/utils/constants.mjs';
import { kskOption, gkvOptions } from '/js/utils/healthInsurance.mjs';
import { estimateMonthlyPensionContributions } from '/js/utils/pensionRefund.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default {
	components: {
		Collapsible,
		Eur,
		IncomeInput,
		Price,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			yearlyIncome: userDefaults.yearlyIncome,
		}
	},
	computed: {
		minIncome(){
			return Math.floor(healthInsurance.kskMinimumIncome / 1000) * 1000;
		},
		maxIncome() {
			const maxContributionIncome = Math.max(healthInsurance.maxMonthlyIncome * 12, taxes.beitragsbemessungsgrenze.currentYear.west);
			return Math.ceil(maxContributionIncome / 1000) * 1000;
		},
		healthInsuranceCostKsk() {
			return kskOption(this.yearlyIncome / 12, 25, 0).total.personalContribution;
		},
		healthInsuranceCostNormal() {
			return gkvOptions({
				age: 25,
				childrenCount: 0,
				hoursWorkedPerWeek: 40,
				monthlyIncome: this.yearlyIncome / 12,
				occupation: 'selfEmployed',
			}).find(o => o.id === 'tk').total.personalContribution;
		},
		pensionCost() {
			return estimateMonthlyPensionContributions(new Date().getFullYear(), this.yearlyIncome / 12, false);
		},
		amountSaved() {
			return this.healthInsuranceCostNormal - (this.healthInsuranceCostKsk + this.pensionCost);
		}
	},
	template: `
		<collapsible
			aria-label="Künstlersozialkasse cost difference calculator"
			aria-description="Calculate the cost difference between Künstlersozialkasse members and regular freelancers."
			class="ksk-cost-difference-calculator"
			:static="static">

			<template v-slot:header>KSK cost calculator</template>

			<div class="range-input">
				<label :for="uid('range-income')" v-if="yearlyIncome < maxIncome">
					<strong><eur :amount="yearlyIncome"></eur></strong>/year income
				</label>
				<label :for="uid('range-income')" v-if="yearlyIncome >= maxIncome">
					<strong><eur :amount="yearlyIncome"></eur></strong>/year or more
				</label>
				<span class="range-prefix no-mobile no-print" @click="yearlyIncome -= (yearlyIncome - 1000) <= minIncome ? 0 : 1000">€</span>
				<input
					:aria-labelledby="uid('range-income')"
					:id="uid('range-income')"
					v-model.number="yearlyIncome"
					type="range"
					class="no-print"
					step="1000"
					:min="minIncome"
					:max="maxIncome"
					tabindex="0">
				<span class="range-suffix no-mobile no-print" @click="yearlyIncome += (yearlyIncome + 1000) >= maxIncome ? 0 : 1000">€</span>
			</div>
			<div class="two-columns private-cost">
				<div>
					<h3>KSK members</h3>
					<p class="price-line">
						Health insurance
						<price :amount="healthInsuranceCostKsk" per-month></price>
					</p>
					<p class="price-line">
						Pension
						<price :amount="pensionCost" per-month></price>
					</p>
					<p class="price-line highlighted">
						Total
						<price :amount="healthInsuranceCostKsk + pensionCost" per-month></price>
					</p>
				</div>
				<div>
					<h3>Other freelancers</h3>
					<p class="price-line">
						Health insurance
						<price :amount="healthInsuranceCostNormal" per-month></price>
					</p>
					<p class="price-line">
						Pension
						<price :amount="0" per-month></price>
					</p>
					<p class="price-line highlighted">
						Total
						<price :amount="healthInsuranceCostNormal" per-month></price>
					</p>
				</div>
			</div>
			<p>
				<template v-if="amountSaved < 0">You pay <eur :amount="amountSaved * -1"></eur> more per month, but</template>
				<template v-if="amountSaved >= 0">You save <eur :amount="amountSaved"></eur> per month <em>and</em></template>
				you invest <eur :amount="pensionCost * 2"></eur> per month in your public pension.
			</p>
		</collapsible>
	`
}
import AgeInput from '/js/vue/components/age-input.mjs';
import ChildrenInput from '/js/vue/components/children-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import Eur from '/js/vue/components/eur.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import OccupationInput from '/js/vue/components/occupation-input.mjs';
import Price from '/js/vue/components/price.mjs';
import Radio from '/js/vue/components/radio.mjs';
import StateInput from '/js/vue/components/state-input.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

import { healthInsurance, pensions, occupations, pflegeversicherung, taxes } from '/js/utils/constants.mjs';
import { roundCurrency } from '/js/utils/currency.mjs';
import { germanStateNames, isEastGerman } from '/js/utils/germanStates.mjs';
import { pkvOptions } from '/js/utils/healthInsurance.mjs';
import { formatPercent } from '/js/utils/number.mjs';
import { calculateTax } from '/js/utils/tax.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default {
	components: {
		AgeInput,
		ChildrenInput,
		Collapsible,
		Eur,
		Glossary,
		IncomeInput,
		OccupationInput,
		Price,
		Radio,
		StateInput,
		Tabs,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			age: userDefaults.age,
			childrenCount: userDefaults.childrenCount,
			church: userDefaults.church,
			customZusatzbeitrag: userDefaults.customZusatzbeitrag,
			germanState: userDefaults.germanState,
			healthInsuranceType: userDefaults.healthInsuranceType,
			yearlyIncome: userDefaults.yearlyIncome,
			inputIncome: 0,
			isMarried: userDefaults.isMarried,
			occupation: userDefaults.occupation,
			privateHealthInsuranceCost: userDefaults.privateHealthInsuranceCost,
			taxClass: userDefaults.taxClass,

			// Non-tax settings
			showExtraQuestions: false,
			useMonthlyIncome: userDefaults.useMonthlyIncome,
			highlightedSection: null,

			// Constants
			colors: {
				healthInsurance: '#FDB366',
				publicPension: '#FEDA8B',
				unemploymentInsurance: '#EAECCC',
				incomeTax: '#F67E4B',
				solidarityTax: '#C2E4EF',
				churchTax: '#98CAE1',
				disposableIncome: '#4A7BB7',
				totalDeductions: '#CD683D',
			},
			formatPercent,
			germanStateNames,
			occupations,
			pensions,
			pflegeversicherung,
			healthInsuranceMaxMonthlyIncome: healthInsurance.maxMonthlyIncome,
			taxes,
		}
	},
	mounted(){
		if(this.useMonthlyIncome){
			this.inputIncome = Math.round(this.yearlyIncome / 12);
		}
		else{
			this.inputIncome = this.yearlyIncome;
		}
	},
	computed: {
		isPayingNormalHealthInsurancePrice() {
			return !this.flag('kv-public-min-contribution') && !this.flag('kv-public-max-contribution')
		},
		hasSponsoredHealthInsurance() {
			return ['ehic', 'familienversicherung-spouse', 'familienversicherung-parents'].includes(this.healthInsuranceType);
		},
		disposableIncomeRatio() {
			// Percentage you keep vs you pay as taxes
			return Math.round(Math.max(this.result.disposableIncome / this.inputIncome, 0) * 100)
		},

		isPayingChurchTax() { return this.church !== 'other' },
		monthOrYear() { return this.useMonthlyIncome ? 'month' : 'year' },

		customGkv() {
			return this.result.healthInsuranceOptions.public.options.find(o => o.id === 'custom');
		},

		availableHealthInsuranceTypes() {
			const healthInsuranceTypes = {
				ehic: this.flag('kv-ehic'),
				'familienversicherung-spouse': this.flag('kv-familienversicherung-spouse'),
				'familienversicherung-parents': this.flag('kv-familienversicherung-parents'),
				private: this.flag('kv-private'),
			};

			// Pick different health insurance if this one is not available.
			if(this.healthInsuranceType in healthInsuranceTypes && !healthInsuranceTypes[this.healthInsuranceType]){
				this.healthInsuranceType = 'public-tk';
			}

			return healthInsuranceTypes;
		},
		privateHealthInsuranceSavings() {
			if(this.healthInsuranceType.startsWith('public') && this.availableHealthInsuranceTypes.private){
				const options = pkvOptions({
					occupation: this.occupation,
					monthlyIncome: this.monthlyIncome,
					hoursWorkedPerWeek: 40,
					age: this.age,
					childrenCount: this.childrenCount
				}).map(o => o.total.personalContribution).sort();
				const privatePrice = options[0] * (this.useMonthlyIncome ? 1 : 12);
				const maxSavings = this.result.healthInsurance - privatePrice;
				if(maxSavings > 0){
					return maxSavings;
				}
			}
		},
		zusatzbeitragRange() {
			return {
				min: Math.floor(this.result.healthInsuranceOptions.public.options[0].zusatzbeitrag.totalRate * 100 * 10) / 10,
				max: Math.ceil(this.result.healthInsuranceOptions.public.options.at(-1).zusatzbeitrag.totalRate * 100 * 10) / 10,
			};
		},

		beitragsbemessungsgrenze() {
			return taxes.beitragsbemessungsgrenze.currentYear[isEastGerman(this.germanState) ? 'east' : 'west'];
		},

		monthlyIncome() {
			return this.useMonthlyIncome ? this.inputIncome : this.inputIncome / 12
		},
		incomeInputRange() {
			return {
				min: this.useMonthlyIncome ? 250 : 5000,
				max: this.useMonthlyIncome ? 12500 : 150000,
				step: this.useMonthlyIncome ? 250 : 5000,
			};
		},
		availableTaxClasses() {
			const taxClasses = Object.entries({
				1: !this.isMarried,
				2: !this.isMarried && !occupations.isLowIncome(this.monthlyIncome) && this.childrenCount > 0,
				3: this.isMarried,
				4: this.isMarried && !occupations.isLowIncome(this.monthlyIncome),
				5: this.isMarried,
				6: occupations.isEmployed(this.occupation),
			})
				.filter(([key, value]) => value)
				.map(([key, value]) => parseInt(key, 10));

			// Pick different tax class if this one is not available.
			if(!taxClasses.includes(this.taxClass)) {
				this.taxClass = taxClasses[0];
			}

			return taxClasses;
		},
		result() {
			const calculationOptions = {
				germanState: this.germanState,
				isPayingChurchTax: !!this.isPayingChurchTax,
				occupation: this.occupation,
				age: +this.age,
				isMarried: !!this.isMarried,
				childrenCount: +this.childrenCount,
				taxClass: +this.taxClass,
				healthInsuranceType: this.healthInsuranceType,
			};

			// Health insurance - public or private
			if(this.healthInsuranceType === 'private') {
				calculationOptions.fixedHealthInsuranceCost = +this.privateHealthInsuranceCost;
			}
			else if(this.hasSponsoredHealthInsurance) {
				calculationOptions.fixedHealthInsuranceCost = 0;
			}
			else {
				// The rate paid for the Zusatzbeitrag
				if (this.healthInsuranceType === 'public-custom') {
					calculationOptions.zusatzbeitrag = this.customZusatzbeitrag / 100;
				}
				else{
					const insurerKey = this.healthInsuranceType.split('-')[1];
					const selectedInsurer = healthInsurance.companies[insurerKey] || healthInsurance.companies.tk;
					calculationOptions.zusatzbeitrag = selectedInsurer.zusatzbeitrag;
				}
			}

			const calculation = calculateTax(this.yearlyIncome, calculationOptions);

			if (this.useMonthlyIncome) {
				calculation.churchTax = roundCurrency(calculation.churchTax / 12);
				calculation.disposableIncome = roundCurrency(calculation.disposableIncome / 12);
				calculation.healthInsurance = roundCurrency(calculation.healthInsurance / 12);
				calculation.income = roundCurrency(calculation.income / 12);
				calculation.incomeTax = roundCurrency(calculation.incomeTax / 12);
				calculation.publicPension = roundCurrency(calculation.publicPension / 12);
				calculation.solidarityTax = roundCurrency(calculation.solidarityTax / 12);
				calculation.taxableIncome = roundCurrency(calculation.taxableIncome / 12);
				calculation.totalDeductions = roundCurrency(calculation.totalDeductions / 12);
				calculation.unemploymentInsurance = roundCurrency(calculation.unemploymentInsurance / 12);
			}

			return calculation;
		},

		// UI stuff
		salaryOrIncome() {
			return occupations.salaryOrIncome(this.occupation);
		},
		svgPaths() {
			// Generate the paths for the SVG pie chart
			let cumulativeRadians = 0;
			return [
				'healthInsurance', 'publicPension', 'unemploymentInsurance', 'incomeTax', 'solidarityTax', 'churchTax', 'disposableIncome',
				'totalDeductions', // This must stay at the end
			].reduce((paths, key) => {
				const percentage = this.result[key] / this.inputIncome;
				if(key === 'totalDeductions'){ cumulativeRadians = 0 } // The pie slice for totalDeductions starts over at 0deg
				const circleStartCoordinates = [Math.cos(cumulativeRadians), Math.sin(cumulativeRadians)];
				cumulativeRadians += 2 * Math.PI * percentage;
				const circleEndCoordinates = [Math.cos(cumulativeRadians), Math.sin(cumulativeRadians)];
				paths[key] = `
					M ${circleStartCoordinates[0]} ${circleStartCoordinates[1]}
					A 1 1 0 ${percentage > 0.5 ? 1 : 0} 1 ${circleEndCoordinates[0]} ${circleEndCoordinates[1]}
					L 0 0
				`;
				return paths;
			}, {});
		}
	},
	watch: {
		inputIncome(newIncome){
			this.yearlyIncome = this.useMonthlyIncome ? newIncome * 12 : newIncome;
		},
		useMonthlyIncome(monthly){
			this.yearlyIncome = monthly ? this.inputIncome * 12 : this.inputIncome;
		},
	},
	methods: {
		flag(flagName){
			return this.result.flags.has(flagName);
		},
		spouseTaxClass(taxClass) {
			if(taxClass === 3) return 5;
			else if(taxClass === 5) return 3;
			else return 4;
		},
		toggleExtraQuestions() {
			this.showExtraQuestions = !this.showExtraQuestions;
			if(!this.showExtraQuestions) {
				// When collapsing the questions, make sure that the calculator stays in the viewport
				this.$nextTick(() => {
					const collapsibleEl = this.$refs.collapsible.$el;
					if(collapsibleEl.getBoundingClientRect().bottom > window.innerHeight) {
						collapsibleEl.scrollIntoView(false);
					}
					if (collapsibleEl.getBoundingClientRect().top < 0) {
						collapsibleEl.scrollIntoView();
					}
				});
			}
		},
		toggleUseMonthlyIncome(){
			this.useMonthlyIncome = !this.useMonthlyIncome;
			if(this.useMonthlyIncome){
				this.inputIncome = Math.round(this.inputIncome / 12);
			}
			else{
				this.inputIncome *= 12;
			}
		},
		monthlyYearlyCost(monthlyAmount) {
			return this.useMonthlyIncome ? monthlyAmount : monthlyAmount * 12;
		}
	},
	// TODO: Spouse's familienversicherung
	template: `
		<collapsible
			aria-description="Calculate how much income tax and social contributions you pay on your salary."
			aria-label="German tax calculator"
			class="income-tax-calculator"
			ref="collapsible"
			:static="static">
			<template v-slot:header>German tax calculator</template>

			<div class="range-input">
				<label :for="uid('range-income')">
					<strong><eur :amount="inputIncome"></eur></strong>/{{ monthOrYear }} {{ salaryOrIncome }}
				</label>
				<span class="range-prefix no-mobile no-print">€</span>
				<input
					:aria-labelledby="uid('range-income')"
					:id="uid('range-income')"
					v-model.number="inputIncome"
					type="range"
					class="no-print"
					:step="incomeInputRange.step"
					:min="incomeInputRange.min"
					:max="incomeInputRange.max"
					tabindex="0">
				<span class="range-suffix no-mobile no-print">€</span>
				<a class="no-print" :class="showExtraQuestions ? 'hide-options' : 'show-options'" @click.prevent="toggleExtraQuestions" href="#">
					{{ showExtraQuestions ? 'Hide options' : 'Show options' }}
				</a>
			</div>
			<template v-if="showExtraQuestions">
				<div class="form-group show-errors">
					<label :for="uid('income')">
						{{ salaryOrIncome === 'salary' ? 'Salary' : 'Income' }}
					</label>
					<div class="input-group">
						<income-input :id="uid('income')" v-model="inputIncome"></income-input>&nbsp;€
						<button class="toggle" @click="toggleUseMonthlyIncome">per {{ monthOrYear }}</button>
					</div>
				</div>
				<div class="form-group">
					<label :for="uid('occupation')">
						Occupation
					</label>
					<occupation-input :id="uid('occupation')" v-model="occupation"></occupation-input>
				</div>
				<div class="form-group">
					<label :for="uid('germanState')">
						Where do you work?
					</label>
					<state-input east-west-berlin :id="uid('germanState')" v-model="germanState"></state-input>
				</div>
				<hr>
				<div class="form-group show-errors">
					<label :for="uid('age')">
						Age
					</label>
					<div class="input-group">
						<age-input :id="uid('age')" v-model="age"></age-input>
						years old
					</div>
				</div>
				<div class="form-group">
					<label :for="uid('church')">
						Religion
					</label>
					<select :id="uid('church')" v-model="church">
						<option value="ev">Evangelical Church</option>
						<option value="rk">Roman Catholic Church</option>
						<option value="jg">Jewish Community</option>
						<option value="ak">Old Catholic Church</option>
						<option value="fg">Free Religious communities</option>
						<option disabled>──────────</option>
						<option value="other">Other</option>
					</select>
					<span v-if="isPayingChurchTax" class="input-instructions">You must pay <glossary term="Kirchensteuer">church tax</glossary>.</span>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('health-insurance-type')">
						Health insurance
					</label>
					<select :id="uid('health-insurance-type')" v-model="healthInsuranceType">
						<optgroup label="Public health insurance">
							<option value="public-tk">Most popular option - TK</option>
							<option value="public-hkk">Cheapest option - hkk</option>
							<option value="public-aok">Most expensive option - AOK Nordost</option>
							<option value="public-custom">Other public health insurance</option>
						</optgroup>
						<optgroup label="Private health insurance">
							<option value="private" :disabled="!availableHealthInsuranceTypes.private">Private health insurance</option>
						</optgroup>
						<optgroup label="Other">
							<option value="familienversicherung-parents" :disabled="!availableHealthInsuranceTypes['familienversicherung-parents']">Insured by parents</option>
							<option value="familienversicherung-spouse" :disabled="!availableHealthInsuranceTypes['familienversicherung-spouse']">Insured by spouse</option>
							<option value="ehic" :disabled="!availableHealthInsuranceTypes.ehic">Insured by another EU country</option>
						</optgroup>
						<option value="unknown">I don't know</option>
					</select>
					<span v-if="healthInsuranceType === 'unknown'" class="input-instructions">We will use an average option.</span>
					<a class="input-instructions internal-link" v-if="healthInsuranceType === 'unknown'" href="/guides/german-health-insurance" target="_blank">How to choose health insurance</a>
				</div>
				<div class="form-group show-errors" v-if="healthInsuranceType === 'private'">
					<label :for="uid('health-insurance-cost')">
						Insurance cost
					</label>
					<div class="input-group">
						<income-input :id="uid('health-insurance-cost')" v-model="privateHealthInsuranceCost"></income-input>
						€&nbsp;per month
					</div>
					<span class="input-instructions" v-if="occupations.isEmployed(occupation)">Enter the total cost, even if your employer pays half of it.</span>
				</div>
				<div class="form-group show-errors" v-if="healthInsuranceType === 'public-custom'">
					<label :for="uid('zusatzbeitrag')">
						<glossary term="Zusatzbeitrag">Insurer surcharge</glossary>
					</label>
					<div class="input-group">
						<input class="percent-input"
							type="number"
							inputmode="numeric"
							min="0"
							step="any"
							pattern="[0-9]*\.?[0-9]+"
							:id="uid('zusatzbeitrag')"
							@focus="$event.target.select()"
							v-model.number="customZusatzbeitrag">
						&nbsp;%
						<input type="range" :min="zusatzbeitragRange.min" :max="zusatzbeitragRange.max" step="0.1" v-model.number="customZusatzbeitrag">
					</div>
				</div>
				<hr>
				<div class="form-group">
					<span class="label">
						Marriage
					</span>
					<tabs
						aria-label="Are you married?"
						v-model="isMarried"
						:id="uid('isMarried')"
						:options="[{label: 'Married', value: true}, {label: 'Not married', value: false}]"></tabs>
				</div>
				<div class="form-group">
					<label :for="uid('children-count')">
						Children
					</label>
					<children-input :id="uid('children-count')" v-model="childrenCount"></children-input>
				</div>
				<hr v-if="occupations.isEmployed(occupation)">
				<div class="form-group" v-if="occupations.isEmployed(occupation)">
					<span class="label">
						<glossary term="Steuerklasse">Tax class</glossary>
					</span>
					<radio
						v-if="availableTaxClasses.includes(1)"
						v-model="taxClass"
						:value="1">
						<div>Tax class 1</div>
						<span class="input-instructions">If you are not married</span>
					</radio>
					<radio
						v-if="availableTaxClasses.includes(2)"
						v-model="taxClass"
						:value="2">
						<div>Tax class 2</div>
						<span class="input-instructions">If you raise children alone</span>
					</radio>
					<radio
						v-if="availableTaxClasses.includes(3)"
						v-model="taxClass"
						:value="3">
						<div>Tax class 3</div>
						<span class="input-instructions">If you earn more than your spouse</span>
					</radio>
					<radio
						v-if="availableTaxClasses.includes(4)"
						v-model="taxClass"
						:value="4">
						<div>Tax class 4</div>
						<span class="input-instructions">If you earn around the same as your spouse</span>
					</radio>
					<radio
						v-if="availableTaxClasses.includes(5)"
						v-model="taxClass"
						:value="5">
						<div>Tax class 5</div>
						<span class="input-instructions">If you earn less than your spouse</span>
					</radio>
					<radio
						v-if="availableTaxClasses.includes(6)"
						v-model="taxClass"
						:value="6">
						<div>Tax class 6</div>
						<span class="input-instructions">If you calculate taxes for a second job</span>
					</radio>
				</div>
				<hr>
			</template>
			<div class="column-with-pie-chart">
				<svg viewBox="-1 -1 2 2" class="pie-chart">
					<title>Pie chart of the taxes you pay in Germany</title>
					<circle cx="0" cy="0" r="1" :fill="colors.disposableIncome"
						@mouseEnter="highlightedSection = 'disposableIncome'" @mouseLeave="highlightedSection = null">
						<title>Disposable income</title>
					</circle>
					<path :d="svgPaths.healthInsurance" :fill="colors.healthInsurance"
						@mouseEnter="highlightedSection = 'healthInsurance'" @mouseLeave="highlightedSection = null">
						<title>Health insurance</title>
					</path>
					<path :d="svgPaths.publicPension" :fill="colors.publicPension"
						@mouseEnter="highlightedSection = 'publicPension'" @mouseLeave="highlightedSection = null">
						<title>Public pension</title>
					</path>
					<path :d="svgPaths.unemploymentInsurance" :fill="colors.unemploymentInsurance"
						@mouseEnter="highlightedSection = 'unemploymentInsurance'" @mouseLeave="highlightedSection = null">
						<title>Unemployment insurance</title>
					</path>
					<path :d="svgPaths.incomeTax" :fill="colors.incomeTax"
						@mouseEnter="highlightedSection = 'incomeTax'" @mouseLeave="highlightedSection = null">
						<title>Income tax</title>
					</path>
					<path :d="svgPaths.solidarityTax" :fill="colors.solidarityTax"
						@mouseEnter="highlightedSection = 'solidarityTax'" @mouseLeave="highlightedSection = null">
						<title>Solidarity surcharge</title>
					</path>
					<path :d="svgPaths.churchTax" :fill="colors.churchTax"
						@mouseEnter="highlightedSection = 'churchTax'" @mouseLeave="highlightedSection = null">
						<title>Church tax</title>
					</path>
				</svg>
				<div aria-label="List of the social contributions you pay">
					<details>
						<summary class="price-line" :class="{highlighted: highlightedSection === 'healthInsurance'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.healthInsurance"/></circle>
							</svg>
							Health insurance
							<price :amount="result.healthInsurance"></price>
						</summary>
						<p v-if="healthInsuranceType === 'private'">
							Your <glossary term="private Krankenversicherung">private health insurance</glossary> costs <eur :amount="privateHealthInsuranceCost"></eur> per month.
							<template v-if="customGkv.baseContribution.employerContribution > 0">Your employer pays half of it.</template>
						</p>
						<template v-if="healthInsuranceType.startsWith('public') || healthInsuranceType === 'unknown'">
							<p>
								<glossary term="gesetzliche Krankenversicherung">Public health insurance</glossary> pays for healthcare when you need it.
								<template v-if="flag('kv-public-min-contribution')">
									Your income is very low, so you pay the <glossary term="Mindestbeitrag">minimum price</glossary>.
								</template>
								<template v-if="flag('kv-public-max-contribution')">
									You earn more than <eur :amount="monthlyYearlyCost(healthInsuranceMaxMonthlyIncome)"></eur> per {{ monthOrYear }}, so you pay the <glossary term="Höchstbeitrag">maximum price</glossary>.
								</template>
							</p>
							<p v-if="flag('kv-public-pflegeversicherung-surcharge')">
								You pay a bit more for <glossary term="Pflegeversicherung">long-term care insurance</glossary>, because you are over {{ pflegeversicherung.defaultRateMaxAge }} years old and you don't have children.
							</p>
						</template>
						<template v-if="hasSponsoredHealthInsurance">
							<p v-if="hasSponsoredHealthInsurance && healthInsuranceType === 'familienversicherung-spouse'">You are covered by your spouse's health insurance.</p>
							<p v-if="hasSponsoredHealthInsurance && healthInsuranceType === 'familienversicherung-parents'">You are covered by your parents' health insurance.</p>
							<p v-if="hasSponsoredHealthInsurance && healthInsuranceType === 'ehic'">You are covered by your health insurance in another EU country.</p>
						</template>
						<p v-if="privateHealthInsuranceSavings">You can save up to <eur :amount="privateHealthInsuranceSavings"></eur></strong> per month if you <a target="_blank" href="/guides/german-health-insurance#private-health-insurance">switch to private health insurance</a>.</p>

						<template v-if="healthInsuranceType.startsWith('public') || healthInsuranceType === 'unknown'">
							<p class="price-line">
								Base cost
								<span class="price no-mobile"
									v-if="isPayingNormalHealthInsurancePrice"
									v-html="formatPercent(customGkv.baseContribution.personalRate * 100, true, 1)"></span>
								<price :amount="monthlyYearlyCost(customGkv.baseContribution.personalContribution)"></price>
							</p>
							<p class="price-line">
								<glossary term="Pflegeversicherung">Long-term care insurance</glossary>
								<span class="price no-mobile"
									v-if="isPayingNormalHealthInsurancePrice"
									v-html="formatPercent(customGkv.pflegeversicherung.personalRate * 100, true, 1)"></span>
								<price :amount="monthlyYearlyCost(customGkv.pflegeversicherung.personalContribution)"></price>
							</p>
							<p class="price-line">
								<glossary term="Zusatzbeitrag">Insurer surcharge</glossary>
								<span class="price no-mobile"
									v-if="isPayingNormalHealthInsurancePrice"
									v-html="formatPercent(customGkv.zusatzbeitrag.personalRate * 100, true, 1)"></span>
								<price :amount="monthlyYearlyCost(customGkv.zusatzbeitrag.personalContribution)"></price>
							</p>
							<p class="price-line" v-if="customGkv.baseContribution.employerContribution > 0">
								Total
								<span class="price no-mobile"
									v-if="isPayingNormalHealthInsurancePrice"
									v-html="formatPercent(customGkv.total.personalRate * 100, true, 1)"></span>
								<price :amount="monthlyYearlyCost(customGkv.total.personalContribution)"></price>
							</p>
						</template>
					</details>
					<details v-if="result.publicPension > 0">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'publicPension'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.publicPension"/></circle>
							</svg>
							Public pension
							<price :amount="result.publicPension"></price>
						</summary>
						<p>
							<glossary term="gesetzliche Rentenversicherung">Public pension insurance</glossary> pays for your pension when you retire.
							<template v-if="yearlyIncome > beitragsbemessungsgrenze">
								You earn more than <eur :amount="monthlyYearlyCost(beitragsbemessungsgrenze / 12)"></eur> per {{ monthOrYear }}, so you pay the maximum contribution.
							</template>
							<template v-else>
								It costs <template v-html="formatPercent(pensions.contributionRates.currentYear)"></template> of your income.
							</template>
						</p>
						<p class="price-line">
							Your employer pays
							<span class="price no-mobile" v-if="yearlyIncome <= beitragsbemessungsgrenze" v-html="formatPercent(pensions.contributionRates.currentYear / 2)"></span>
							<price :amount="result.publicPension"></price>
						</p>
						<p class="price-line">
							You pay
							<span class="price no-mobile" v-if="yearlyIncome <= beitragsbemessungsgrenze" v-html="formatPercent(pensions.contributionRates.currentYear / 2)"></span>
							<price :amount="result.publicPension"></price>
						</p>
					</details>
					<details v-if="result.unemploymentInsurance > 0">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'unemploymentInsurance'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.unemploymentInsurance"/></circle>
							</svg>
							Unemployment insurance
							<price :amount="result.unemploymentInsurance"></price>
						</summary>
						<p>
							<glossary term="/Arbeitslosenversicherung">Unemployment insurance</glossary> pays for <glossary term="ALG I">unemployment benefits</glossary> if you lose your job.
							<template v-if="yearlyIncome > beitragsbemessungsgrenze">
								You earn more than <eur :amount="monthlyYearlyCost(beitragsbemessungsgrenze / 12)"></eur> per {{ monthOrYear }}, so you pay the maximum contribution.
							</template>
							<template v-else>
								It costs {{ formatPercent(taxes.arbeitslosenversicherungRate * 2 * 100) }} of your income.
							</template>
						</p>
						<p class="price-line" v-if="customGkv.baseContribution.employerContribution > 0">
							Your employer pays
							<span class="price no-mobile" v-if="yearlyIncome <= beitragsbemessungsgrenze" v-html="formatPercent(taxes.arbeitslosenversicherungRate * 100)"></span>
							<price :amount="result.unemploymentInsurance"></price>
						</p>
						<p class="price-line" v-if="customGkv.baseContribution.employerContribution > 0">
							You pay
							<span class="price no-mobile" v-if="yearlyIncome <= beitragsbemessungsgrenze" v-html="formatPercent(taxes.arbeitslosenversicherungRate * 100)"></span>
							<price :amount="result.unemploymentInsurance"></price>
						</p>
					</details>
					<details v-if="result.incomeTax > 0">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'incomeTax'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.incomeTax"/></circle>
							</svg>
							Income tax
							<price :amount="result.incomeTax"></price>
						</summary>
						<p v-if="occupations.isEmployed(occupation)">
							This is the <glossary term="Einkommensteuer">income tax</glossary> you pay directly from your paycheque. It's missing some {{ childrenCount > 0 ? 'big ' : '' }}tax deductions. When you file a <glossary term="Steuererklärung">tax declaration</glossary>, you can get {{ childrenCount > 0 ? 'a lot of ' : 'some ' }}money back{{ childrenCount > 0 ? ', especially when you have children' : '' }}.
						</p>
						<p class="price-line">
							Taxable income
							<price :amount="result.taxableIncome"></price>
						</p>
						<p class="price-line">
							Income tax rate
							<output class="price" v-html="formatPercent(result.incomeTax / result.taxableIncome * 100, true, 1)"></output>
						</p>
					</details>
					<details v-if="result.solidarityTax > 0">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'solidarityTax'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.solidarityTax"/></circle>
							</svg>
							Solidarity surcharge
							<price :amount="result.solidarityTax"></price>
						</summary>
						<p>
							If you pay more than <eur :amount="taxes.solidarity.minIncomeTax"></eur>/year in income tax, you must pay a <glossary term="Solidaritätszuschlag">solidarity surcharge</glossary>. It's a percentage of your <glossary term="Einkommensteuer">income tax</glossary>.
						</p>
						<p v-if="flag('soli-mid-rate')">
							Solidarity surcharge is {{ formatPercent(taxes.solidarity.milderungszoneRate * 100) }} of all <glossary term="Einkommensteuer">income tax</glossary> above <eur :amount="taxes.solidarity.minIncomeTax"></eur>.
						</p>
						<p v-if="flag('soli-max-rate')">
							The solidarity surcharge is {{ formatPercent(taxes.solidarity.maxRate * 100) }} of your <glossary term="Einkommensteuer">income tax</glossary>.
						</p>
					</details>
					<details v-if="isPayingChurchTax">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'churchTax'}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="0.7" :fill="colors.churchTax"/></circle>
							</svg>
							Church tax
							<price :amount="result.churchTax"></price>
						</summary>
						<p>Your church collects a <glossary term="Kirchensteuer">church tax</glossary>. In {{ germanStateNames[germanState].en }}, the church tax is {{ formatPercent(result.churchTaxRate * 100) }} of your <glossary term="Einkommensteuer">income tax</glossary>.</p>
						<p v-if="result.churchTax === 0 && result.incomeTax === 0">Your income is too low to pay income tax, so you don't pay church tax.</p>
					</details>
					<details class="total">
						<summary class="price-line" :class="{highlighted: !highlightedSection}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="1" fill="currentColor"/></circle>
								<path :d="svgPaths.totalDeductions" :fill="colors.incomeTax"></path>
							</svg>
							You pay {{ formatPercent(100 - disposableIncomeRatio) }}
							<price :amount="result.totalDeductions"></price>
						</summary>
						<p>This is what you pay for all taxes and social contributions. <template v-if="occupations.isEmployed(occupation)">They take this from your paycheck.</template></p>
					</details>
					<details class="total">
						<summary class="price-line" :class="{highlighted: highlightedSection === 'disposableIncome' || !highlightedSection}">
							<svg id="svg" viewBox="-1 -1 2 2" class="pie-chart" aria-hidden="true">
								<circle cx="0" cy="0" r="1" fill="currentColor"/></circle>
								<path :d="svgPaths.disposableIncome" :fill="colors.disposableIncome"></path>
							</svg>
							You keep {{ formatPercent(disposableIncomeRatio) }}
							<price :amount="result.disposableIncome"></price>
						</summary>
						<p>This is your <glossary term="Netto income">net income</glossary>. It's how much money you keep after taxes and other deductions. It's your money. You can spend it.</p>
					</details>
				</div>
			</div>
			<template v-if="privateHealthInsuranceSavings">
				<hr>
				<p>
					You can save up to <eur :amount="privateHealthInsuranceSavings"></eur></strong> per {{ monthOrYear }} if you <a target="_blank" href="/guides/german-health-insurance#private-health-insurance">switch to private health insurance</a>.
				</p>
			</template>
		</collapsible>
	`
}
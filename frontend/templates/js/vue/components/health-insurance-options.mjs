import Eur from '/js/vue/components/eur.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconBank from '/js/vue/components/icons/bank.mjs';
import IconFamily from '/js/vue/components/icons/family.mjs';
import IconProtection from '/js/vue/components/icons/protection.mjs';
import IconPassport from '/js/vue/components/icons/passport.mjs';
import Price from '/js/vue/components/price.mjs';
import PublicHealthInsuranceOptions from '/js/vue/components/public-health-insurance-options.mjs';

import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { occupations } from '/js/utils/constants.mjs';
import { formatCurrency } from '/js/utils/currency.mjs';
import healthInsuranceOptionsMixin from '/js/vue/mixins/healthInsuranceOptions.mjs';


export default {
	mixins: [uniqueIdsMixin, healthInsuranceOptionsMixin],
	components: {
		Eur,
		Glossary,
		IconBank,
		IconFamily,
		IconProtection,
		IconPassport,
		Price,
		PublicHealthInsuranceOptions,
	},
	computed: {
		mainOptions(){
			return this.results.asList.map(r => r.id).filter(id => ['public', 'private', 'expat'].includes(id));
		},
		intro(){
			let output = '';
			if(this.flag('free')){
				output += " You might also qualify for free health insurance.";
			}
			else if(this.mainOptions.length === 1){
				output += " It's your only option.";
			}

			if(this.flag('private-income-too-low')){
				output += " Your income is too low for private health insurance.";
			}
			if(!this.results.public.eligible){
				output += " You don't qualify for public health insurance.";
			}

			if(output){
				const options = new Intl.ListFormat('en-US', {style: 'long', type: 'disjunction'}).format(this.mainOptions);
				output = `You must choose <strong>${options} health insurance</strong>. ${output.trim()}`;
			}

			return output;
		},

		minCostByOption() {
			return Object.fromEntries(
				this.results.asList.map(result => {
					const minCost = Math.min(
						...result.options.map(o => o?.total?.personalContribution || Infinity)
					);
					return [result.id, minCost === Infinity ? undefined : minCost];
				})
			);
		},

		/***************************************************
		* Clarification for each option
		***************************************************/

		clarification(){
			if(occupations.isStudent(this.occupation)){
				return this.studentClarification;
			}
			else if(occupations.isSelfEmployed(this.occupation)){
				return this.selfEmployedClarification;
			}
			else if(occupations.isEmployed(this.occupation)){
				return this.employeeClarification;
			}
			// There is no Azubi or unemployed clarification
			return {};
		},
		employeeClarification(){
			if(this.results.private.eligible){
				if(this.minCostByOption.public > this.minCostByOption.private){
					return {
						private: "It's cheaper because you are young and you have a good income. You pay less <em>and</em> get better coverage.",
						public: "It's more expensive because it costs a percentage of your income.",
					}
				}
				else {
					return { private: "In your situation, private only makes sense if you want better coverage or faster doctor appointments. Public health insurance is cheaper."}
				}
			}
			return {};
		},
		selfEmployedClarification(){
			const output = {};
			const publicHI = this.results.public.eligible;
			const privateHI = this.results.private.eligible;
			const expatHI = this.results.expat.eligible;
			const avoidExpat = "Avoid this option if you can. The coverage is too limited, and you can't use it to renew your freelance visa.";

			if(publicHI && privateHI){
				if(this.minCostByOption.public > this.minCostByOption.private){
					output.private = "This is a great option because you are young and you have a good income. You can get better coverage <em>and</em> pay less.";
					output.public = "This is a safer option because the cost matches your income. Choose this if you have an unstable income.";
				}
				else {
					output.private = "In your situation, private only makes sense if you want better coverage or faster doctor appointments. Public health insurance is cheaper.";
				}
				output.expat = avoidExpat;
			}
			else if(publicHI && expatHI && !privateHI){
				output.public = "This is the best long-term option. It's more expensive, but you get much better coverage.";
				output.expat = "Avoid this option if you can. Public health insurance is much better. If you choose this option, you can't switch to public later.";
			}
			else if(privateHI && expatHI && !publicHI){
				output.private = "This is the best long-term option."
				output.expat = avoidExpat;
			}
			else if(expatHI && !privateHI && !publicHI){
				output.expat = "This is not a great option, but you have no other choice. Switch to public or private health insurance when you can.";
			}
			return output;
		},
		studentClarification(){
			if(this.flag('public-tariff-student')){ // Students under 30
				return {
					public: "This is the best option for students under 30 years old.",
					expat: "It's cheaper, but the coverage is much worse. Public health insurance is a better option.",
					private: "It's more expensive, but you can choose better coverage and faster doctor appointments.",
				};
			}
			else if(this.flag('public-student-over-30')){
				return {
					expat: "It's cheap, but the coverage is much worse.",
					private: "This is a good option for students over 30 years old.",
					public: "It's more expensive because you are too old for the student tariff. It can still be a good option.",
				};
			}
		},

		familienversicherungText() {
			const parents = this.flag('familienversicherung-parents');
			const spouse = this.flag('familienversicherung-spouse');
			let sponsors = null;
			if(parents && spouse){
				sponsors = 'your parents or your spouse have';
			}
			else if(spouse){
				sponsors = 'your spouse has';
			}
			else if(parents){
				sponsors = 'your parents have';
			}

			return `If ${sponsors} public health insurance, it covers you for free.`;
		},
	},
	methods: {
		flag(flagName){
			return this.results.flags.has(flagName);
		},
		eur(num) {
			return formatCurrency(num, false, '€', false);
		},
		learnMoreUrl(id){ return `/guides/german-health-insurance#${id}-health-insurance` },

		prosAndCons(insuranceType){
			if(insuranceType === 'public'){
				const pros = [
					"The cost adjusts to your income",
					"It covers all necessary healthcare",
				];
				if(this.childrenCount){
					pros.push(`It covers your ${this.childOrChildren} for free`);
				}
				return {
					pros,
					cons: [
						"Longer wait times to see a specialist",
						"Limited dental coverage",
					],
				};
			}
			else if(insuranceType === 'private'){
				const cons = ["It costs the same if you lose your job"];
				if(this.childrenCount){
					cons.push(`You must pay to cover your ${this.childOrChildren}`);
				}
				return {
					pros: [
						"Choose the coverage you want",
						"Get doctor appointments faster",
					],
					cons,
				};
			}
			else if(insuranceType === 'expat'){
				return {
					pros: [
						"Cheaper than full health insurance",
					],
					cons: [
						"Very limited coverage",
						"It's a bad long-term option",
					],
				};
			}
		},
	},
	template: `
		<div class="health-insurance-options">
			<h2>Your options</h2>
			<p v-html="intro" v-if="intro"></p>
			<ul class="buttons list" v-if="mainOptions.length > 1">
				<li v-for="option in results.asList" v-if="option.eligible && option.id !== 'other'" :key="option.id">
					<button class="button" @click="selectOption(option.id + 'Options')" :aria-label="option.name">
						<div>
							<h3 v-text="option.name"></h3>
							<p v-if="clarification[option.id]" v-html="clarification[option.id]"></p>
						</div>
						<price v-if="minCostByOption[option.id]" :amount="minCostByOption[option.id]" per-month></price>
						<div class="two-columns" v-if="prosAndCons(option.id)">
							<ul class="pros">
								<li v-for="pro in prosAndCons(option.id).pros" v-text="pro" :key="pro"></li>
							</ul>
							<ul class="cons">
								<li v-for="con in prosAndCons(option.id).cons" v-text="con" :key="con"></li>
							</ul>
						</div>
					</button>
				</li>
			</ul>

			<public-health-insurance-options @select="selectOption" v-bind="$props" v-if="mainOptions.length === 1 && results.public.eligible"></public-health-insurance-options>
			<expat-health-insurance-options @select="selectOption" v-bind="$props" v-if="mainOptions.length === 1 && results.expat.eligible"></expat-health-insurance-options>
			<template v-if="results.other.eligible">
				<hr>
				<h3 v-text="results.other.name"></h3>
				<ul class="buttons list">
					<li v-for="subOption in results.other.options" :key="subOption.id">
						<a v-if="subOption.id === 'familienversicherung'" @click="selectOption(subOption.id)" title="Learn more about family health insurance" href="/guides/german-health-insurance#free-health-insurance" target="_blank">
							<icon-family/>
							<div>
								<h3>Family health insurance</h3>
								<p v-text="familienversicherungText"></p>
							</div>
							<price :amount="0" per-month></price>
						</a>
						<a v-if="subOption.id === 'social-benefits'" @click="selectOption(subOption.id)" title="Learn more about state-sponsored health insurance" href="/guides/german-health-insurance#free-health-insurance" target="_blank">
							<icon-bank/>
							<div>
								<h3>Social benefits</h3>
								<p>If you get <glossary term="ALG I">unemployment benefits</glossary>, <glossary>Bürgergeld</glossary> or <glossary>Elterngeld</glossary>, you get free public health insurance.</p>
							</div>
							<price :amount="0" per-month></price>
						</a>
						<a v-if="subOption.id === 'ehic'" @click="selectOption(subOption.id)" title="Learn more about the EHIC" href="/guides/german-health-insurance#insurance-from-other-eu-countries" target="_blank">
							<icon-passport/>
							<div>
								<h3>European Health Insurance Card</h3>
								<p>Your insurance from another EU country might cover you in Germany.</p>
							</div>
							<price :amount="0" per-month></price>
						</a>
						<a v-if="subOption.id === 'ksk'" @click="selectOption(subOption.id)" title="Learn more about the KSK" href="/guides/ksk-kuenstlersozialkasse" target="_blank">
							<icon-protection/>
							<div>
								<h3>Join the <glossary>Künstlersozialkasse</glossary></h3>
								<p>If you are an artist, the KSK can pay half of your public health insurance. This is a really good deal.</p>
							</div>
							<price :amount="optionPrice('other', subOption.id)" per-month></price>
						</a>
					</li>
				</ul>
			</template>
		</div>
	`
}
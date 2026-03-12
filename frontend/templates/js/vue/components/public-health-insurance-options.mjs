import Eur from '/js/vue/components/eur.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import LogoBarmer from '/js/vue/components/icons/logo-barmer.mjs';
import LogoTk from '/js/vue/components/icons/logo-tk.mjs';
import Price from '/js/vue/components/price.mjs';

import healthInsuranceOptionsMixin from '/js/vue/mixins/healthInsuranceOptions.mjs';
import { healthInsurance, occupations, pflegeversicherung } from '/js/utils/constants.mjs';
import { formatCurrency } from '/js/utils/currency.mjs';
import { isWerkstudent } from '/js/utils/healthInsurance.mjs';
import { formatPercent } from '/js/utils/number.mjs';

export default {
	components: {
		Eur,
		Glossary,
		LogoBarmer,
		LogoTk,
		Price,
	},
	mixins: [healthInsuranceOptionsMixin],
	data(){
		return {
			formatPercent,
			healthInsurance,
			pflegeversicherung,
		}
	},
	computed: {
		tariff(){
			return this.results.public.options[0].tariff;
		},
		tariffName() {
			return {
				azubi: 'apprentice',
				azubiFree: 'apprentice',
				employee: 'employee',
				midijob: 'midijob',
				selfEmployed: 'self-employed',
				selfPay: 'self-pay',
				student: 'student',
			}[this.tariff];
		},
		baseContributionRate() {
			return this.formatPercent(this.results.public.options[0].baseContribution.totalRate * 100);
		},
		cheapestOption() {
			return this.results.public.options[0];
		},
		mostExpensiveOption() {
			return this.results.public.options.at(-1);
		},
		technikerKrankenkasseUrl() {
			if(occupations.isStudent(this.occupation)){
				return "/out/tk-signup-students";
			}
			else if(occupations.isEmployed(this.occupation)){
				return "/out/tk-signup-employees";
			}
			return "/out/feather-tk-signup";
		},
		isMinijobTariff(){
			return (
				occupations.isMinijob(this.occupation, this.monthlyIncome)
				&& this.tariff === 'selfPay'  // You could have a minijob with the student tariff
			);
		},
		isStudentOver30(){
			return occupations.isStudent(this.occupation) && this.age >= 30;
		},
		isMinContribution(){
			return this.monthlyIncome <= healthInsurance.minMonthlyIncome;
		},
		isMaxContribution(){
			return this.monthlyIncome >= healthInsurance.maxMonthlyIncome;
		},
		isNotWerkstudent(){
			return occupations.isStudent(this.occupation) && !isWerkstudent(this.occupation, this.monthlyIncome, this.hoursWorkedPerWeek);
		},
		isPublicOnlyOption() {
			return (
				this.results.asList.filter(o => o.eligible && o.id !== 'other').length === 1
				&& this.results.asList[0].id === 'public'
			);
		},
	},
	methods: {
		option(id){
			return this.results.public.options.filter(o => o.id === id)[0];
		},
		selectOption(option){
			this.$emit('select', option);
		},
		eur(num) {
			return formatCurrency(num, false, '€', false);
		},
	},
	template: `
		<div class="health-insurance-options">
			<h2 v-if="!isPublicOnlyOption">Public health insurance options</h2>
			<p>Choose an insurer. There are dozens of them, but their cost and coverage are almost the same.</p>

			<ul class="buttons list">
				<li>
					<a class="recommended" title="Sign up with Techniker Krankenkasse" :href="technikerKrankenkasseUrl" target="_blank">
						<logo-tk/>
						<div>
							<h3 v-text="option('tk').name"></h3>
							<p>The biggest public health insurer. They speak English.</p>
						</div>
						<price :amount="option('tk').total.personalContribution" per-month></price>
					</a>
				</li>
				<li>
					<a title="Sign up with BARMER" href="/out/feather-barmer-signup" target="_blank">
						<logo-barmer/>
						<div>
							<h3 v-text="option('barmer').name"></h3>
							<p>The second biggest insurer. They also speak English.</p>
						</div>
						<price :amount="option('barmer').total.personalContribution" per-month></price>
					</a>
				</li>
			</ul>

			<details class="cost-explanation">
				<summary>Cost explanation</summary>
				<p>
					You pay the <strong>{{ tariffName }} tariff</strong>.
					<template v-if="tariff === 'employee'">
						Your health insurance costs a percentage of your income. Your employer pays half of it.
					</template>
					<template v-if="tariff === 'selfEmployed' || tariff === 'azubi'">
						Your health insurance costs a percentage of your income.
					</template>
					<template v-if="tariff === 'azubiFree'">
						You make less than <eur :amount="healthInsurance.azubiFreibetrag"></eur> per month, so you get free health insurance. Your employer pays for it.
					</template>
					<template v-if="tariff === 'student'">
						Your health insurance has a fixed price.
					</template>
					<template v-if="tariff === 'selfPay'">
						<template v-if="isMinijobTariff">
							You pay the <glossary term="Mindestbeitrag">minimum price</glossary>.
						</template>
						<template v-else>
							Your health insurance costs a percentage of your income.
						</template>
					</template>
					<template v-if="tariff === 'midijob'">
						It's a cheaper tariff for low-income jobs.
					</template>

					<template v-if="isStudentOver30">
						You can't get the student tariff because you are over 30 years old.
					</template>
					<template v-else-if="isNotWerkstudent && hoursWorkedPerWeek > 20">
						You can't get the student tariff because you work more than 20 hours per week.
					</template>
					<template v-else-if="isNotWerkstudent && hoursWorkedPerWeek <= 20">
						You can't get the student tariff because your income is too high.
					</template>

					<template v-if="childrenCount">
						It covers your {{ childOrChildren }} <glossary term="Familienversicherung">for free</glossary>.
					</template>
				</p>
				<hr>
				<details>
					<summary class="price-line">
						Base cost
						<price :amount="cheapestOption.baseContribution.totalContribution" per-month></price>
					</summary>
					<p>
						<template v-if="isMinijobTariff">
							You have a minijob, so you pay the <glossary term="Mindestbeitrag">minimum price</glossary>. It's {{ baseContributionRate }} of <eur :amount="healthInsurance.minMonthlyIncome"></eur> }}.
						</template>
						<template v-else-if="isMinContribution">
							You make less than <eur :amount="healthInsurance.minMonthlyIncome"></eur> per month, so you pay the <glossary term="Mindestbeitrag">minimum price</glossary>. It's {{ baseContributionRate }} of <eur :amount="healthInsurance.minMonthlyIncome"></eur>.
						</template>
						<template v-else-if="isMaxContribution">
							You make more than <eur :amount="healthInsurance.maxMonthlyIncome"></eur> per month, so you pay the <glossary term="Höchstbeitrag">maximum price</glossary>. It's {{ baseContributionRate }} of <eur :amount="healthInsurance.maxMonthlyIncome"></eur>.
						</template>
						<template v-else-if="tariff === 'midijob'">
							You make less than <eur :amount="healthInsurance.maxMidijobIncome"></eur> per month, so you pay the midijob tariff. It's cheaper than the normal tariff.
						</template>
						<template v-else-if="tariff === 'student'">
							You pay the student tariff; the base cost is a fixed price.
						</template>
						<template v-else>
							You pay {{ baseContributionRate }} of your income.
						</template>
						This cost is the same for all insurers.
					</p>
				</details>
				<details>
					<summary class="price-line">
						Insurer surcharge
						<price
							:from="cheapestOption.zusatzbeitrag.totalContribution"
							:to="mostExpensiveOption.zusatzbeitrag.totalContribution"
							per-month></price>
					</summary>
					<p>
						Insurers can charge more for better services. Each insurer has a different surcharge. The average surcharge is {{ formatPercent(healthInsurance.averageZusatzbeitrag * 100) }} of your income.
					</p>
				</details>
				<details>
					<summary class="price-line">
						Long-term care insurance
						<price :amount="cheapestOption.pflegeversicherung.totalContribution" per-month></price>
					</summary>
					<p>
						It pays for your healthcare when you are older.
						<template v-if="isMaxContribution">
							You pay the <glossary term="Höchstbeitrag">maximum price</glossary>, because you make more than <eur :amount="healthInsurance.maxMonthlyIncome"></eur> per month.
						</template>
						<template v-else>
							You pay {{ formatPercent(cheapestOption.pflegeversicherung.totalRate * 100) }} of your income.
							<template v-if="age > pflegeversicherung.defaultRateMaxAge && childrenCount === 0">
								You pay more because you are over {{ pflegeversicherung.defaultRateMaxAge }} years old and you don't have children.
							</template>
							<template v-else-if="age <= pflegeversicherung.defaultRateMaxAge">
								You pay less because you are under {{ pflegeversicherung.defaultRateMaxAge + 1 }} years old.
							</template>
							<template v-else>
								You pay less because you have children.
							</template>
						</template>
						The cost is the same for all insurers.
					</p>
				</details>
				<details>
					<summary class="price-line">
						Your employer pays
						<price
							:from="cheapestOption.total.employerContribution"
							:to="mostExpensiveOption.total.employerContribution"
							per-month></price>
					</summary>
					<p v-if="tariff === 'selfEmployed'">
						You are self-employed, so you don't get help from an employer.
					</p>
					<p v-if="tariff === 'azubiFree'">
						When you make less than <eur :amount="healthInsurance.azubiFreibetrag"></eur> per month, your employer pays for your health insurance.
					</p>
					<p v-if="tariff === 'selfPay' && !isMinijobTariff">
						You are unemployed, so you don't get help from an employer.
					</p>
					<p v-if="isMinijobTariff">
						When you have a <glossary term="Minijob">minijob</glossary>, your employer does not pay for your health insurance.
					</p>
					<p v-if="tariff === 'employee'">
						Your employer pays half of your health insurance.
					</p>
					<p v-if="tariff === 'midijob'">
						Your employer pays part of your health insurance.
					</p>
					<p v-if="tariff === 'student'">
						Your employer does not pay for your health insurance.
					</p>
				</details>
				<details>
					<summary class="price-line highlighted">
						You pay
						<price
							:from="cheapestOption.total.personalContribution"
							:to="mostExpensiveOption.total.personalContribution"
							per-month></price>
					</summary>
					<p>
						This is what you pay for public health insurance.
						<template v-if="isMaxContribution">
							You make more than <eur :amount="healthInsurance.maxMonthlyIncome"></eur> per month, so you pay the <glossary term="Höchstbeitrag">maximum price</glossary>.
						</template>
						<template v-else-if="isMinContribution">
							You pay the <glossary term="Mindestbeitrag">minimum price</glossary>, because you make less than <eur :amount="healthInsurance.minMonthlyIncome"></eur> per month.
						</template>
						<template v-else-if="tariff === 'azubiFree'">
							You pay nothing, because you make less than <eur :amount="healthInsurance.azubiFreibetrag"></eur> per month. Your employer pays for your insurance.
						</template>
						This is a <glossary term="steuerlich absetzbar">tax-deductible</glossary> expense.
					</p>
				</details>
			</details>
		</div>
	`
}
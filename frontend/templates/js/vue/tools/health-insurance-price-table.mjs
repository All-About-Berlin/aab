import Glossary from '/js/vue/components/glossary.mjs';
import Price from '/js/vue/components/price.mjs';
import Tabs from '/js/vue/components/tabs.mjs';
import { healthInsurance } from '/js/utils/constants.mjs';
import { getHealthInsuranceOptions } from '/js/utils/healthInsurance.mjs';

const studentAge = 22;
const employeeAge = 30;
const freelancerAge = 25;

function round5(n) {
	return Math.round(n / 5) * 5;
}

function priceRange(minOpts, maxOpts = minOpts) {
	if (!minOpts.length) return null;

	const from = round5(minOpts[0].total.personalContribution);
	const to = round5(maxOpts.at(-1).total.personalContribution);
	return { from, to };
}

function getOptions(params) {
	return getHealthInsuranceOptions({
		childrenCount: 0,
		sortByPrice: true,
		...params
	});
}

function expat() {
	const opts = getOptions({
		occupation: 'unemployed',
		age: studentAge,
	});
	return {
		from: opts.expat.options[0].total.personalContribution,
	};
}

function publicStudent() {
	const min = getOptions({
		age: 20,
		hoursWorkedPerWeek: 0,
		monthlyIncome: 0,
		occupation: 'studentUnemployed'
	});
	const max = getOptions({
		age: 28,
		hoursWorkedPerWeek: 0,
		monthlyIncome: 0,
		occupation: 'studentUnemployed'
	});
	return priceRange(min.public.options, max.public.options);
}

function publicEmployee() {
	const min = getOptions({
		occupation: 'employee',
		age: 20,
		monthlyIncome: healthInsurance.maxMidijobIncome + 1,
		occupation: 'employee'
	});
	const max = getOptions({
		occupation: 'employee',
		age: 50,
		monthlyIncome: healthInsurance.maxMonthlyIncome,
	});
	return priceRange(min.public.options, max.public.options);
}

function publicFreelancer() {
	const min = getOptions({
		occupation: 'selfEmployed',
		hoursWorkedPerWeek: 40,
		monthlyIncome: healthInsurance.minMonthlyIncome,
		hasGermanPublicHealthInsurance: true, // Required to access GKV as freelancer
	});
	const max = getOptions({
		occupation: 'selfEmployed',
		hoursWorkedPerWeek: 40,
		monthlyIncome: healthInsurance.maxMonthlyIncome,
		hasGermanPublicHealthInsurance: true, // Required to access GKV as freelancer
	});
	return priceRange(min.public.options, max.public.options);
}

function privateStudent() {
	const min = getOptions({
		age: 20,
		hoursWorkedPerWeek: 0,
		monthlyIncome: 0,
		occupation: 'studentUnemployed'
	});
	const max = getOptions({
		age: 28,
		hoursWorkedPerWeek: 0,
		monthlyIncome: 0,
		occupation: 'studentUnemployed'
	});
	return priceRange(min.private.options, max.private.options);
}

function privateEmployee() {
	const opts = getOptions({
		occupation: 'employee',
		age: employeeAge,
		monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome,
	});
	return priceRange(opts.private.options);
}

function privateFreelancer() {
	const opts = getOptions({
		age: 35,
		hoursWorkedPerWeek: 40,
		monthlyIncome: healthInsurance.maxMonthlyIncome,
		occupation: 'selfEmployed'
	});
	return priceRange(opts.private.options);
}

export default {
	components: {
		Glossary,
		Price,
		Tabs,
	},
	data() {
		return {
			occupation: 'employee',
		};
	},
	computed: {
		occupationTabs() {
			return [
				{ value: 'employee',   label: 'Employees'   },
				{ value: 'student',    label: 'Students'    },
				{ value: 'freelancer', label: 'Freelancers' },
			];
		},
		priceMatrix() {
			return {
				expat: {
					student:    expat(),
					employee:   expat(),
					freelancer: expat(),
				},
				public: {
					student:    publicStudent(),
					employee:   publicEmployee(),
					freelancer: publicFreelancer(),
				},
				private: {
					student:    privateStudent(),
					employee:   privateEmployee(),
					freelancer: privateFreelancer(),
				},
			};
		},
	},
	template: `
		<div class="health-insurance-price-table">
			<tabs v-model="occupation" :options="occupationTabs"></tabs>
			<h2>Our prices</h2>
			<hr>
			<div class="three-columns">
				<div>
					<h3><glossary term="Expat health insurance">Expat</glossary></h3>
					<p v-if="occupation === 'employee'">Basic coverage until you start working.</p>
					<p v-else>Basic coverage for your first visa application.</p>
					<price v-if="priceMatrix.expat[occupation]" v-bind="priceMatrix.expat[occupation]" per-month></price>
					<span class="price" v-else><small>Not available</small></span>
				</div>
				<div>
					<h3><glossary term="gesetzliche Krankenversicherung">Public</glossary></h3>
					<p>Simple, reliable long-term health insurance.</p>
					<price v-if="priceMatrix.public[occupation]" v-bind="priceMatrix.public[occupation]" per-month></price>
					<span class="price" v-else><small>Not available</small></span>
				</div>
				<div>
					<h3><glossary term="private Krankenversicherung">Private</glossary></h3>
					<p>Custom long-term coverage, faster doctor appointments.</p>
					<price v-if="priceMatrix.private[occupation]" v-bind="priceMatrix.private[occupation]" per-month></price>
					<span class="price" v-else><small>Not available</small></span>
				</div>
			</div>
		</div>
	`,
};

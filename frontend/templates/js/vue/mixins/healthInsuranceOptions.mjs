import { getHealthInsuranceOptions } from '/js/utils/healthInsurance.mjs';

export default {
	props: {
		age: Number,
		childrenCount: Number,
		hasGermanPublicHealthInsurance: Boolean,
		hasEUPublicHealthInsurance: Boolean,
		hoursWorkedPerWeek: Number,
		isApplyingForFirstVisa: Boolean,
		isMarried: Boolean,
		monthlyIncome: Number,
		occupation: String,
		customZusatzbeitrag: Number,
	},
	computed: {
		results() {
			return getHealthInsuranceOptions({
				...this.$props,
				sortByPrice: true
			});
		},
		childOrChildren(){ return this.childrenCount === 1 ? 'child' : 'children' },
	},
	methods: {
		selectOption(option){
			this.$emit('select', option);
		},
		optionPrice(type, id){
			return this.results[type].options.find(o => o.id === id).total.personalContribution;
		},
	},
}
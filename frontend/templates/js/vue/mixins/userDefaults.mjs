import { salaries, healthInsurance } from '/js/utils/constants.mjs';

export const userDefaults = {  // Percentages are stored as full amounts, unlike elsewhere
	age: 25,
	childrenCount: 0,
	church: 'other',
	customZusatzbeitrag: 1.5,
	isMarried: false,
	occupation: 'employee',
	germanState: 'be-east',
	useMonthlyIncome: false,
	yearlyIncome: Math.round(salaries.medianIncome/100) * 100,
	healthInsuranceType: 'unknown',
	privateHealthInsuranceCost: 550, // € per month
	publicHealthInsuranceZusatzbeitrag: healthInsurance.averageZusatzbeitrag, // %
	taxClass: 1,

	empty: null, // Just to highlight that this field saves/loads user input, but is null by default
};

export const userDefaultsMixin = {
	mounted(){
		const availableKeys = new Set(Object.keys(this.$data));
		const desiredStringKeys = new Set([
			'church',
			'countryOfResidence',
			'dateOfBirth',  // YYYY-MM-DD string
			'email',
			'fullName',
			'germanState',
			'healthInsuranceType',
			'modificationKey',
			'citizenshipModificationKey',
			'nationality',
			'occupation',
			'phone',
			'religion',
		]);

		const desiredNumberKeys = new Set([
			'age',
			'childrenCount',
			'privateHealthInsuranceCost',
			'publicHealthInsuranceZusatzbeitrag',
			'taxClass',
			'yearlyIncome',
		]);

		const desiredBooleanKeys = new Set([
			'hasEUPublicHealthInsurance',
			'hasGermanPublicHealthInsurance',
			'isApplyingForFirstVisa',
			'isMarried',
			'useMonthlyIncome',
			'worksOver20HoursPerWeek',
		]);

		availableKeys.intersection(desiredStringKeys).forEach(key => {
			this[key] = this.getDefault(key);
			this.$watch(key, function (newVal) {
				this.setDefault(key, newVal);
			})
		});

		availableKeys.intersection(desiredNumberKeys).forEach(key => {
			this[key] = this.getDefaultNumber(key);
			this.$watch(key, function (newVal) {
				this.setDefaultNumber(key, newVal);
			})
		});

		availableKeys.intersection(desiredBooleanKeys).forEach(key => {
			this[key] = this.getDefaultBoolean(key);
			this.$watch(key, function (newVal) {
				this.setDefaultBoolean(key, newVal);
			})
		});
	},
	methods: {
		// Try:
		// - The 'xxx' in localStorage
		// - The this.xxx
		// - The userDefaults.xxx
		getDefault(key){
			let value = null;
			try {
				value = localStorage.getItem(key)
			} catch (e) {}

			if(value != null){ // Also matches undefined
				return value;
			}
			else if(this[key] !== undefined){  // null is an accepted value
				return this[key];
			}
			return userDefaults[key] || null;
		},
		getDefaultNumber(key){ // Returns null or a number
			const defaultValue = this.getDefault(key);
			return defaultValue === null ? defaultValue : +defaultValue;
		},
		getDefaultBoolean(key){ // Returns true, false or null
			const defaultValue = this.getDefault(key);
			if(defaultValue === null){
				return defaultValue;
			}
			return defaultValue === 'false' ? false : !!defaultValue; // localStorage stores strings, so "true" or "false"
		},
		setDefault(key, value) {
			if(value === null || value === undefined){
				localStorage.removeItem(key);
				return;
			}
			try {
				localStorage.setItem(key, value);
				userDefaults[key] = value;
			} catch (e) {}
		},
		setDefaultNumber(key, value) {
			this.setDefault(key, +value)
		},
		setDefaultBoolean(key, value) {
			this.setDefault(key, !!value)
		},
	}
}
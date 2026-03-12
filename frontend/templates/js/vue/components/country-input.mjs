import { countriesInEnglish } from '/js/utils/countries.mjs';

export default {
	props: {
		value: String,
		placeholder: {
			type: String,
			default: 'Choose a country',
		},
		excludeGermany: {
			type: Boolean,
			default: false,
		},
		countryCode: {
			type: Boolean,
			default: false,
		},
	},
	data() {
		return {
			sortedCountries: Object.entries(countriesInEnglish).sort((a, b) => a[1].localeCompare(b[1])).filter(c => c[0] !== 'DE' || !this.excludeGermany),
		}
	},
	computed: {
		recommendedCountries(){
			const recommendations = new Set(
				(navigator.languages || [])
					.map(lang => lang.substring(3).toUpperCase())
					.filter(countryCode => countryCode !== 'DE')
					.map(countryCode => countryCode in countriesInEnglish ? [countryCode, countriesInEnglish[countryCode]] : null)
					.filter(Boolean)
			);
			if(!this.excludeGermany){
				recommendations.add(["DE", countriesInEnglish.DE]);
			}
			return recommendations;
		},
	},
	template: `
		<select autocomplete="country-name" :value="value" @input="$emit('input', $event.target.value)" :class="{placeholder: !value}">
			<option disabled hidden default value="">{{ placeholder }}</option>
			<option
				:value="countryCode ? code : name"
				v-for="[code, name] in recommendedCountries"
				:key="code + '-recommended'">{{ name }}</option>
			<option disabled v-if="recommendedCountries">──────────</option>
			<option
				:value="countryCode ? code : name"
				v-for="[code, name] in sortedCountries"
				:key="code">{{ name }}</option>
		</select>
	`,
};
import { germanStateNames, isEastGerman } from '/js/utils/germanStates.mjs';

export default {
	props: {
		value: {
			type: String,
			default: null,
		},
		placeholder: {
			type: String,
			default: 'Choose a state',
		},
		eastWestBerlin: {
			type: Boolean,
			default: false,
		},
		output: {
			type: String,
			default: 'abbr',
		},
	},
	computed: {
		states(){
			return Object.entries(germanStateNames)
				.filter(
					([key]) => (this.eastWestBerlin ? (key !== 'be') : !key.startsWith('be-'))
				)
				.sort((a, b) => a[1].de.localeCompare(b[1].de));
		},
	},
	methods: {
		onInput(event){
			this.$emit('input', event.target.value);
		},
		optionValue(abbr){
			const stateName = germanStateNames[abbr];
			return {
				abbr: abbr,
				germanName: stateName.de,
				englishName: stateName.en,
			}[this.output];
		}
	},
	template: `
	<select :value="value" @input="onInput" :class="{placeholder: !value}">
		<option disabled hidden default :value="null" v-text="placeholder"></option>
		<option v-for="[abbr, state] in states" :key="abbr" :value="optionValue(abbr)">{{ state.en }}</option>
	</select>
	`,
}
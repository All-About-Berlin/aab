export default {
	props: {
		value: Number,
		placeholder: {
			type: String,
			default: 'Number of children',
		},
	},
	template: `
		<select class="children-input" :value="value" @input="$emit('input', Number($event.target.value))" :class="{placeholder: value == null}">
			<option disabled hidden default :value="null" v-text="placeholder"></option>
			<option :value="0">No children</option>
			<option :value="1">1 child</option>
			<option :value="2">2 children</option>
			<option :value="3">3 children</option>
			<option :value="4">4 children</option>
			<option :value="5">5 children</option>
			<option :value="6">6+ children</option>
		</select>
	`,
}
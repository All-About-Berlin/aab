export default {
	props: ['value'],
	methods: {
		parsedValue(val) {
			let parsed = parseFloat(val);
			return isNaN(parsed) ? val : parsed;
		}
	},
	template: `
		<input class="age-input"
			type="text"
			inputmode="numeric"
			pattern="[0-9]*"
			placeholder="25"
			:value.number="value"
			maxlength="2"
			@input="$emit('input', parsedValue($event.target.value))"
			@focus="$event.target.select()">
	`,
}
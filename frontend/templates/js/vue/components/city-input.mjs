export default {
	props: ['value'],
	template: `
		<input
			title="City"
			placeholder="Berlin"
			type="text"
			autocomplete="address-level2"
			:value="value"
			@input="$emit('input', $event.target.value)">
	`,
}
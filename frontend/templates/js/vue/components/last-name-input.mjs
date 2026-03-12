export default {
	props: ['value'],
	template: `
		<input type="text"
			class="last-name-input"
			placeholder="Smith"
			autocomplete="family-name"
			title="Last name"
			:value="value"
			@input="$emit('input', $event.target.value)">
	`,
}
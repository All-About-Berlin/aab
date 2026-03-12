export default {
	props: ['value'],
	template: `
		<input type="text"
			class="full-name-input"
			placeholder="Alex Smith"
			autocomplete="name"
			title="Full name"
			:value="value"
			@input="$emit('input', $event.target.value)">
	`,
}
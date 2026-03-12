export default {
	props: ['value'],
	template: `
		<input type="email"
			class="email-input"
			placeholder="contact@example.com"
			autocomplete="email"
			title="Email address"
			:value="value"
			@input="$emit('input', $event.target.value)">
	`,
}
export default {
	props: {
		value: String,
		required: Boolean,
	},
	template: `
		<input
			class="postalcode-input"
			placeholder="12345"
			type="text"
			inputmode="numeric"
			pattern="[0-9]{5}"
			minlength="5"
			maxlength="5"
			autocomplete="postal-code"
			title="Postal code (Postleitzahl)"
			:value="value"
			:required="required"
			@input="$emit('input', $event.target.value)"
			>
	`,
}
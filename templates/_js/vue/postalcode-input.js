{% include '_js/vue.js' %}
{% js %}{% raw %}
Vue.component('postalcode-input', {
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
			v-on:input="$emit('input', $event.target.value)"
			:required="required"
			>
	`,
});
{% endraw %}{% endjs %}
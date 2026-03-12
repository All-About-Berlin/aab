export default {
	model: {
		prop: 'selectedValue',
		event: 'change'
	},
	props: {
		selectedValue: [String, Number, Boolean], // The v-model value
		value: [String, Number, Boolean], // This input's value when selected

		id: String,
		disabled: Boolean,
	},
	template: `
		<label class="checkbox">
			<input
				type="radio"
				:id="id"
				:value="value"
				:checked="value === selectedValue"
				:disabled="disabled"
				@change="$emit('change', value)"
				/>
			<slot></slot>
		</label>
	`,
}
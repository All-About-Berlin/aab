export default {
	props: {
		id: String,
		value: Boolean,
		disabled: Boolean,
	},
	template: `
		<label class="checkbox">
			<input
				type="checkbox"
				:id="id"
				:disabled="disabled"
				:checked="value"
				@input="$emit('input', $event.target.checked)"
				/>
			<slot></slot>
		</label>
	`,
}
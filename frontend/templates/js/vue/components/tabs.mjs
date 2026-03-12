export default {
	props: {
		value: [Number, String, Boolean],
		options: Array,
		required: Boolean,
		id: String,
	},
	template: `
		<fieldset class="tabs" :required="required">
			<template v-for="option in options">
				<input
					type="radio"
					v-model="value"
					:id="id + option.value"
					:name="id"
					:required="required"
					:value="option.value"
					:key="id + option.value"
					@input="$emit('input', option.value)">
				<label
					:for="id + option.value"
					:key="id + option.value + '-label'"
					v-text="option.label"></label>
			</template>
		</fieldset>
	`,
}
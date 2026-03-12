export default {
	props: {
		value: String,
		placeholder: {
			type: String,
			default: 'Choose an occupation',
		},
	},
	template: `
	<select :value="value" @input="$emit('input', $event.target.value)" :class="{placeholder: !value}">
		<option disabled hidden default value="">{{ placeholder }}</option>
		<optgroup label="Employee">
			<option value="employee">Employee</option>
			<option value="azubi">Apprentice (Azubi)</option>
		</optgroup>
		<optgroup label="Student">
			<option value="studentEmployee">Working student</option>
			<option value="studentSelfEmployed">Self-employed student</option>
			<option value="studentUnemployed">Unemployed student</option>
		</optgroup>
		<optgroup label="Other">
			<option value="selfEmployed">Self-employed / freelancer</option>
			<option value="unemployed">Unemployed</option>
		</optgroup>
	</select>
	`,
}
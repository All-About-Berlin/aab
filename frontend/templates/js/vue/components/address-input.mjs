export default {
	props: {
		value: String,
		home: Boolean,
		work: Boolean,
		abroad: Boolean,
		placeholder: {
			type: String,
			default: null,
		},
	},
	computed: {
		placeholderAddress(){
			if(this.placeholder){
				return this.placeholder;
			}
			else if(this.home) {
				return 'Wohnungstraße 123\n12345 Berlin'
			}
			else if(this.work){
				return 'Arbeitstraße 123\n12345 Berlin'
			}
			else if(this.abroad){
				return '123 Maple Street, Apt. 102\nMontreal, Quebec, H3E 1J4\nCanada'
			}
			return "Musterstraße 123\n12345 Berlin"
		},
		autocomplete(){
			let type = '';
			if(this.home) {
				type = 'home'
			}
			else if (this.home){
				type = 'work'
			}
			return `${type} street-address`
		}
	},
	template: `
		<textarea
			class="address-input"
			:autocomplete="autocomplete"
			:placeholder="placeholderAddress"
			:value="value"
			@input="$emit('input', $event.target.value)"
			required></textarea>
	`,
};
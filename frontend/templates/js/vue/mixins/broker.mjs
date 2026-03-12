import { healthInsurance } from '/js/utils/constants.mjs';

export default {
	data() {
		return {
			broker: {
				id: 'seamus-wolf',
				name: 'Seamus',
				fullName: 'Seamus Wolf',
				phoneNumber: '+491626969454',
				phoneNumberPretty: '+49 162 6969454',
				he: 'he',
				him: 'him',
				his: 'his',
			},
		}
	},
	methods: {
		capitalize(word){
			return word.charAt(0).toUpperCase() + word.slice(1);
		},
	}
}
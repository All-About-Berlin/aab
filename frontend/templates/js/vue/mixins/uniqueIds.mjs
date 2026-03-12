export default {
	data: function () {
		return {
			uniqueId: Math.floor(Math.random() * 10000),
		}
	},
	methods: {
		uid(elementId){
			return `${elementId}-${this.uniqueId}`;
		},
	}
}
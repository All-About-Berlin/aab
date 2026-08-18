import multiStageMixin from '/js/vue/mixins/multiStage.mjs';

export default {
	components: {},
	mixins: [multiStageMixin],
	data() {
		return {
			stages: [
				'start',
				'thank-you',
				'error',
			],
		};
	},
};

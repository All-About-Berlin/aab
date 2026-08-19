import Tabs from '/js/vue/components/tabs.mjs';

export default {
	components: { Tabs },
	props: {
		id: { type: String, required: true },
		value: Boolean,
		disabled: Boolean,
		required: Boolean,
	},
	data(){
		return {
			options: [
				{ label: 'Yes', value: true },
				{ label: 'No', value: false },
			],
		};
	},
	computed: {
		labelId(){
			return `${this.id}-label`;
		},
	},
	methods: {
		toggle(){
			if(this.disabled) return;
			this.$emit('input', !this.value);
		},
	},
	template: `
		<div class="yes-no-input">
			<span :id="labelId" class="yes-no-input-label" @click="toggle"><slot></slot></span>
			<tabs
				:id="id"
				:value="value"
				:options="options"
				:required="required"
				:aria-labelledby="labelId"
				@input="$emit('input', $event)"></tabs>
		</div>
	`,
}

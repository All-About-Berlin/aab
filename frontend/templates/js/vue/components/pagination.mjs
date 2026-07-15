export default {
	props: {
		pageCount: Number,
		value: Number,
	},
	computed: {
		pageNumbers(){
			return Array.from({length: this.pageCount}, (_, i) => i + 1);
		},
	},
	methods: {
		selectPage(page){
			this.$emit('input', Number(page));
		},
	},
	template: `
		<nav class="buttons bar" aria-label="Pagination" v-if="pageCount > 1">
			<button aria-label="Previous page" class="button previous" :disabled="value === 1" @click="selectPage(value - 1)"></button>
			<select @input="selectPage($event.target.value)" :value="value">
				<option v-for="n in pageNumbers" :value="n" :key="n" v-text="n"></option>
			</select>
			<button aria-label="Next page" class="button next" :disabled="value === pageCount" @click="selectPage(value + 1)"></button>
		</nav>
	`,
}
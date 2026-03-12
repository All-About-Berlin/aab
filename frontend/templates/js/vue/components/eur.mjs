import { formatCurrency } from '/js/utils/currency.mjs';
import { getCurrencyTooltipText } from '/js/utils/exchangeRates.mjs';

export default {
	props: {
		amount: Number,
		cents: Boolean,
		noSymbol: Boolean,
		locale: String,
	},
	data(){
		return {
			tooltipText: null,
		}
	},
	created(){
		this.updateTooltipText();
	},
	computed: {
		formattedAmount(){
			return formatCurrency(this.amount, this.cents, false, false, this.locale);
		}
	},
	methods: {
		async updateTooltipText(){
			this.tooltipText = (await getCurrencyTooltipText(this.amount ?? '')) || null;
		}
	},
	watch: {
		amount(){
			this.updateTooltipText();
		}
	},
	template: `
		<span>{{ noSymbol ? '' : '€'}}<span class="currency" :data-currencies="tooltipText">{{ formattedAmount }}</span></span>
	`,
}
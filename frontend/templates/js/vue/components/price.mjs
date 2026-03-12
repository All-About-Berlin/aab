import { getCurrencyTooltipText } from '/js/utils/exchangeRates.mjs';
import { formatCurrency } from '/js/utils/currency.mjs';

export default {
	props: {
		from: Number,
		to: Number,
		cents: Boolean,
		amount: Number,
		perMonth: Boolean,
		locale: String,
	},
	data(){
		return {
			fromTooltipText: '',
			toTooltipText: '',
		}
	},
	created(){
		this.updateTooltipTexts();
	},
	computed: {
		showFrom(){
			return this.from != null && !this.to;
		},
		showRange(){
			return this.to != null && this.formattedAmount(this.from ?? this.amount) !== this.formattedAmount(this.to)
		},
	},
	methods: {
		formattedAmount(amount) {
			return formatCurrency(amount, this.cents, false, false, this.locale);
		},
		async updateTooltipTexts(){
			this.fromTooltipText = await getCurrencyTooltipText(this.from ?? this.amount ?? '');
			this.toTooltipText = await getCurrencyTooltipText(this.to ?? '');
		}
	},
	watch: {
		amount(){
			this.updateTooltipTexts();
		},
		from(){
			this.updateTooltipTexts();
		},
		to(){
			this.updateTooltipTexts();
		},
	},
	template: `
		<span class="price">
			<small v-if="showFrom">From&nbsp;</small>€<span class="currency" :data-currencies="fromTooltipText">{{ formattedAmount(from ?? amount) }}</span><template v-if="showRange">&ndash;<span class="currency" :data-currencies="toTooltipText">{{ formattedAmount(to) }}</span></template><small v-if="perMonth">&nbsp;/&nbsp;month</small>
		</span>
	`,
}
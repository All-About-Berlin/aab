import { getCurrencyTooltipText } from '/js/utils/exchangeRates.mjs';

export default function initializeCurrencyTooltips(){
	window.addEventListener("DOMContentLoaded", function() {
		document.querySelectorAll('.currency').forEach(element => {
			getCurrencyTooltipText(element.textContent).then(text => {
				if(text) {
					element.dataset.currencies = text;
				};
			});
		});
	});
}
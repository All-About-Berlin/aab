export function roundCurrency(num, roundDown=false) {
	if(roundDown) {
		return Math.floor(num * 100) / 100;
	}
	return Math.round(num * 100) / 100;
}

// TODO: Remove html param
export function formatCurrency(num, includeCents=false, currency='€', html=false, locale='en-GB') {
	const decimalsToShow = includeCents ? 2 : 0;
	let formattedNum = roundCurrency(num)
		.toLocaleString(locale, {
			minimumFractionDigits: decimalsToShow,
			maximumFractionDigits: decimalsToShow,
		});

	if(formattedNum === '-0.00'){
		formattedNum = '0.00';
	}
	else if(formattedNum === '-0'){
		formattedNum = '0';
	}
	return currency ? `${currency}${formattedNum}` : formattedNum;
}
export function formatPercent(num, addSymbol=true, maxDecimals=3) {
	const formattedNum = num.toLocaleString('en-GB', {
		minimumFractionDigits: 0,
		maximumFractionDigits: maxDecimals,
	});
	return addSymbol ? `${formattedNum}%` : formattedNum;
}
const countryCodeToCurrencyCode = {
	AF: "AFN",
	AL: "ALL",
	DZ: "DZD",
	AS: "USD",
	AO: "AOA",
	AI: "XCD",
	AQ: "XCD",
	AG: "XCD",
	AR: "ARS",
	AM: "AMD",
	AW: "AWG",
	AU: "AUD",
	AZ: "AZN",
	BS: "BSD",
	BH: "BHD",
	BD: "BDT",
	BB: "BBD",
	BZ: "BZD",
	BJ: "XOF",
	BM: "BMD",
	BT: "BTN",
	BO: "BOB",
	BA: "BAM",
	BW: "BWP",
	BV: "NOK",
	BR: "BRL",
	IO: "USD",
	BN: "BND",
	BG: "BGN",
	BF: "XOF",
	BI: "BIF",
	KH: "KHR",
	CM: "XAF",
	CA: "CAD",
	CV: "CVE",
	KY: "KYD",
	CF: "XAF",
	TD: "XAF",
	CL: "CLP",
	CN: "CNY",
	CX: "AUD",
	CC: "AUD",
	CO: "COP",
	KM: "KMF",
	CG: "XAF",
	CK: "NZD",
	CR: "CRC",
	HR: "EUR",
	CU: "CUP",
	CZ: "CZK",
	DK: "DKK",
	DJ: "DJF",
	DM: "XCD",
	DO: "DOP",
	TP: "USD",
	EG: "EGP",
	SV: "SVC",
	GQ: "XAF",
	ER: "ERN",
	ET: "ETB",
	FK: "FKP",
	FO: "DKK",
	FJ: "FJD",
	PF: "XPF",
	GA: "XAF",
	GM: "GMD",
	GE: "GEL",
	GH: "GHS",
	GI: "GIP",
	GL: "DKK",
	GD: "XCD",
	GU: "USD",
	GN: "GNF",
	GY: "GYD",
	HT: "HTG",
	HM: "AUD",
	HN: "HNL",
	HK: "HKD",
	HU: "HUF",
	IS: "ISK",
	IN: "INR",
	ID: "IDR",
	IR: "IRR",
	IQ: "IQD",
	IL: "ILS",
	CI: "XOF",
	JM: "JMD",
	JP: "JPY",
	JO: "JOD",
	KZ: "KZT",
	KE: "KES",
	KI: "AUD",
	KW: "KWD",
	KG: "KGS",
	LA: "LAK",
	LB: "LBP",
	LS: "LSL",
	LR: "LRD",
	LY: "LYD",
	LI: "CHF",
	MK: "MKD",
	MW: "MWK",
	MY: "MYR",
	MV: "MVR",
	ML: "XOF",
	MH: "USD",
	MU: "MUR",
	MX: "MXN",
	FM: "USD",
	MD: "MDL",
	MN: "MNT",
	MS: "XCD",
	MA: "MAD",
	MZ: "MZN",
	NA: "NAD",
	NR: "AUD",
	NP: "NPR",
	AN: "ANG",
	NC: "XPF",
	NZ: "NZD",
	NI: "NIO",
	NE: "XOF",
	NG: "NGN",
	NU: "NZD",
	NF: "AUD",
	KP: "KPW",
	GB: "GBP",
	MP: "USD",
	NO: "NOK",
	OM: "OMR",
	PK: "PKR",
	PW: "USD",
	PA: "PAB",
	PG: "PGK",
	PY: "PYG",
	PE: "PEN",
	PH: "PHP",
	PL: "PLN",
	PR: "USD",
	QA: "QAR",
	RO: "RON",
	RU: "RUB",
	RW: "RWF",
	SH: "SHP",
	KN: "XCD",
	LC: "XCD",
	VC: "XCD",
	WS: "WST",
	ST: "STD",
	SA: "SAR",
	SN: "XOF",
	RS: "RSD",
	SC: "SCR",
	SL: "SLL",
	SG: "SGD",
	SB: "SBD",
	SO: "SOS",
	ZA: "ZAR",
	GS: "GBP",
	KR: "KRW",
	SS: "SSP",
	LK: "LKR",
	SD: "SDG",
	SR: "SRD",
	SJ: "NOK",
	SZ: "SZL",
	SE: "SEK",
	CH: "CHF",
	SY: "SYP",
	TJ: "TJS",
	TZ: "TZS",
	TH: "THB",
	CD: "CDF",
	TG: "XOF",
	TK: "NZD",
	TO: "TOP",
	TT: "TTD",
	TN: "TND",
	TR: "TRY",
	TM: "TMT",
	TC: "USD",
	TV: "AUD",
	UG: "UGX",
	UA: "UAH",
	AE: "AED",
	UK: "GBP",
	US: "USD",
	UM: "USD",
	UY: "UYU",
	UZ: "UZS",
	VU: "VUV",
	VN: "VND",
	VG: "USD",
	VI: "USD",
	WF: "XPF",
	EH: "MAD",
	YE: "YER",
	ZM: "ZMW"
};

// Guess the user's country from their browser language ("en-US")
// Use it to infer its top 3 preferred currencies.
// It's not reliable, but it's not important to get it right
const preferredCurrencies = Array.from(
	new Set(
		(navigator.languages || [])
			.map(l => countryCodeToCurrencyCode[l.substring(3)])
			.filter(Boolean)
			.concat(["USD", "GBP", "INR"])
	)
).slice(0, 3);

let exchangeRatesPromise = null;
function getExchangeRates(){
	if(!exchangeRatesPromise){
		exchangeRatesPromise = fetch('/api/exchangerates.json')
			.then(response => {
				if(!response.ok){
					throw new Error('Cannot retrieve exchange rates.');
				}
				return response.json()
			})
			.then(data => data.rates);
	}
	return exchangeRatesPromise;
}

async function eurToCurrency(eurValue, currencyCode) {
	const exchangeRates = await getExchangeRates();
	const usdValue = eurValue / exchangeRates.EUR;
	const value = usdValue * exchangeRates[currencyCode];
	const showCents = value < 100;
	return Intl.NumberFormat('en-US', {style: 'currency', currency: currencyCode, maximumFractionDigits: showCents ? undefined : 0}).format(value);
}

export async function getCurrencyTooltipText(elementText) {
	if(elementText == null){
		return '';
	}

	const eurValue = parseInt(elementText.toString().replaceAll(/[^0-9\.]/g, '') || NaN, 10);
	if(isNaN(eurValue) || eurValue === 0) {
		return '';
	}

	// TODO: Negative amounts
	try{
		const convertedAmounts = await Promise.all(preferredCurrencies.map(currencyCode => eurToCurrency(eurValue, currencyCode)));
		return convertedAmounts.join('\n');
	} catch(e) {
		return null;
	}
}
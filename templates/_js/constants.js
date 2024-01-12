{% js %}
const bafogBedarfssatz = {{ GKV_BAFOG_BEDARFSSATZ }};

const healthInsurance = {
	defaultTarif: {{ GKV_BASE_CONTRIBUTION }}/100,
	selfEmployedTarif: {{ GKV_SELF_EMPLOYED_BASE_CONTRIBUTION }}/100,
	studentTarif: {{ GKV_STUDENT_BASE_CONTRIBUTION }}/100,
	minMonthlyIncome: {{ GKV_MIN_INCOME }},
	maxMonthlyIncome: {{ GKV_HÖCHSTBEITRAG_MIN_INCOME }}/12,
	minFreiwilligMonthlyIncome: {{ GKV_FREIWILLIG_VERSICHERT_MIN_INCOME }}/12,
	maxFamilienvericherungIncome: {{ GKV_FAMILIENVERSICHERUNG_MAX_INCOME }},
	midijobMaxIncome: {{ MIDIJOB_MAX_INCOME }},
	avgZusatzbeitrag: {{ GKV_ZUSATZBEITRAG_AVERAGE }}/100,
	azubiFreibetrag: {{ GKV_AZUBI_FREIBETRAG }},
	nebenjobMaxIncome: {{ GKV_NEBENJOB_MAX_INCOME }},
	factorF: {{ GKV_FACTOR_F }},
	kskMinimumIncome: {{ KSK_MIN_INCOME }},
	companies: {
		average: {
			name: 'Average health insurance',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_AVERAGE }}/100,
		},
		aok: {
			name: 'AOK Nordost',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_AOK }}/100,
		},
		barmer: {
			name: 'Barmer',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_BARMER }}/100,
		},
		dak: {
			name: 'DAK',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_DAK }}/100,
		},
		hkk: {
			name: 'hkk',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_HKK }}/100,
		},
		tk: {
			name: 'Techniker Krankenkasse',
			zusatzbeitrag: {{ GKV_ZUSATZBEITRAG_TK }}/100,
		},
	},
}

const pflegeversicherung = {
	defaultTarif: {{ PFLEGEVERSICHERUNG_NO_SURCHARGE }}/100,
	surchargeTarif: {{ PFLEGEVERSICHERUNG_WITH_SURCHARGE }}/100,
	discountPerChild: {{ PFLEGEVERSICHERUNG_DISCOUNT_PER_CHILD }}/100,
	minimumChildCountForDiscount: 2,
	maximumChildCountForDiscount: 5,
	employerTarif: {{ PFLEGEVERSICHERUNG_NO_SURCHARGE }}/100/2, // Employer doesn't contribute to surcharge
	defaultTarifMaxAge: {{ PFLEGEVERSICHERUNG_NO_SURCHARGE_MAX_AGE }}, // Above this age, if you don't have kids, you pay the surchargeTarif
};

const taxes = {
	church: {
		default: {{ CHURCH_TAX_RATE }} / 100,
		bw: {{ CHURCH_TAX_RATE_BW_BY }} / 100,
		by: {{ CHURCH_TAX_RATE_BW_BY }} / 100,
	},
	arbeitslosenversicherungRate: {{ ARBEITSLOSENVERSICHERUNG_EMPLOYEE_RATE }}/100,
	beitragsbemessungsgrenze: {
		2000: { west: 4500 * 12, east: 3750 * 12 },
		2001: { west: 4500 * 12, east: 3750 * 12 },
		2002: { west: 4500 * 12, east: 3750 * 12 },
		2003: { west: 5100 * 12, east: 4250 * 12 },
		2004: { west: 5150 * 12, east: 4350 * 12 },
		2005: { west: 5200 * 12, east: 4400 * 12 },
		2006: { west: 5250 * 12, east: 4400 * 12 },
		2007: { west: 5250 * 12, east: 4550 * 12 },
		2008: { west: 5300 * 12, east: 4500 * 12 },
		2009: { west: 5400 * 12, east: 4550 * 12 },
		2010: { west: 5500 * 12, east: 4650 * 12 },
		2011: { west: 5500 * 12, east: 4800 * 12 },
		2012: { west: 5600 * 12, east: 4800 * 12 },
		2013: { west: 5800 * 12, east: 4900 * 12 },
		2014: { west: 5950 * 12, east: 5000 * 12 },
		2015: { west: 6050 * 12, east: 5200 * 12 },
		2016: { west: 6200 * 12, east: 5400 * 12 },
		2017: { west: 6350 * 12, east: 5700 * 12 },
		2018: { west: 6500 * 12, east: 5800 * 12 },
		2019: { west: 6700 * 12, east: 6150 * 12 },
		2020: { west: 6900 * 12, east: 6450 * 12 },
		2021: { west: 7100 * 12, east: 6700 * 12 },
		2022: { west: 7050 * 12, east: 6750 * 12 },
		2023: { west: 7300 * 12, east: 7100 * 12 },
		currentYear: { west: {{ BEITRAGSBEMESSUNGSGRENZE_WEST }}, east: {{ BEITRAGSBEMESSUNGSGRENZE_EAST }} }, // {{ fail_on('2024-12-31') }}
		2024: { west: {{ BEITRAGSBEMESSUNGSGRENZE_WEST }}, east: {{ BEITRAGSBEMESSUNGSGRENZE_EAST }} },
		2025: { west: {{ BEITRAGSBEMESSUNGSGRENZE_WEST }}, east: {{ BEITRAGSBEMESSUNGSGRENZE_EAST }} }, // ESTIMATED (2024)
		2026: { west: {{ BEITRAGSBEMESSUNGSGRENZE_WEST }}, east: {{ BEITRAGSBEMESSUNGSGRENZE_EAST }} }, // ESTIMATED (2024)
		2027: { west: {{ BEITRAGSBEMESSUNGSGRENZE_WEST }}, east: {{ BEITRAGSBEMESSUNGSGRENZE_EAST }} }, // ESTIMATED (2024)
	},
	grundfreibetrag: {{ GRUNDFREIBETRAG }},
	kinderfreibetrag: {{ KINDERFREIBETRAG }},
	entlastungsbetragAlleinerziehende: {{ ENTLASTUNGSBETRAG_ALLEINERZIEHENDE }},
	entlastungsbetragAlleinerziehendePerChild: {{ ENTLASTUNGSBETRAG_ALLEINERZIEHENDE_EXTRA_CHILD }},
	kindergeldPerChild: {{ KINDERGELD }},
	solidarity: { // https://www.finanztip.de/solidaritaetszuschlag/
		minIncomeTax: {{ SOLIDARITY_TAX_MILDERUNGSZONE_MIN_INCOME_TAX }},  // Above this, you pay solidarity tax
		milderungszoneRate: {{ SOLIDARITY_TAX_MILDERUNGSZONE_RATE }}, // percent of incomeTax - minIncomeTax
		maxRate: {{ SOLIDARITY_TAX_MAX_RATE }},
	},
	minVorsorgepauschal: {{ VORSORGEPAUSCHAL_MIN }},
	minVorsorgepauschalTaxClass3: {{ VORSORGEPAUSCHAL_MIN_TAX_CLASS_3 }},
	{{ fail_on('2024-12-31') }}
	incomeTaxTarifZones: {  // §32a EStG
		1: {
			formula: (x, y, z) => 0,
			minIncome: -Infinity,
			maxIncome: {{ GRUNDFREIBETRAG }},
		},
		2: {
			formula: (x, y, z) => (922.98 * y + 1400) * y,
			minIncome: {{ GRUNDFREIBETRAG }},
			maxIncome: {{ INCOME_TAX_TARIF_2_MAX_INCOME }},
		},
		3: {
			formula: (x, y, z) => (181.19 * z + 2397) * z + 1025.38,
			minIncome: {{ INCOME_TAX_TARIF_2_MAX_INCOME }},
			maxIncome: {{ INCOME_TAX_TARIF_3_MAX_INCOME }},
		},
		4: {
			formula: (x, y, z) => 0.42 * x - 10602.13,
			minIncome: {{ INCOME_TAX_TARIF_3_MAX_INCOME }},
			maxIncome: {{ INCOME_TAX_TARIF_4_MAX_INCOME }},
		},
		5: {
			formula: (x, y, z) => {{ INCOME_TAX_MAX_RATE }} / 100 * x - 18936.88,
			minIncome: {{ INCOME_TAX_TARIF_4_MAX_INCOME }},
			maxIncome: Infinity,
		},
	},
	incomeTaxClass56: {
		maxIncome1: {{ INCOME_TAX_CLASS_56_LIMIT_1 }},
		maxIncome2: {{ INCOME_TAX_CLASS_56_LIMIT_2 }},
		maxIncome3: {{ INCOME_TAX_CLASS_56_LIMIT_3 }},
	},
	maxMinijobIncome: {{ MINIJOB_MAX_INCOME }}, // Max monthly income to be considered a minijobber
	arbeitnehmerpauschale: {{ ARBEITNEHMERPAUSCHALE }}, // Fixed yearly income tax deduction for employees
	sonderausgabenPauschbetrag: {{ SONDERAUSGABEN_PAUSCHBETRAG }}, // Fixed yearly income tax deduction
};

// https://github.com/mledoze/countries/blob/master/dist/countries.json
const brexitDate = new Date(2021, 0, 1);

const pensions = {
	contractingCountries: new Set(['AL', 'AU', 'BR', 'CA', 'CL', 'IN', 'IL', 'JP', 'KR', 'MA', 'ME', 'PH', 'TN', 'TR', 'UY', 'US']),
	balkanBlockCountries: new Set(['BA', 'MK', 'RS', 'XK', 'ME']),
	disqualifyingCountries: new Set(['BA', 'MK', 'RS', 'XK', 'ME', 'TR']),
	contributionRates: {
		2000: 19.3,
		2001: 19.1,
		2002: 19.1,
		2003: 19.5,
		2004: 19.5,
		2005: 19.5,
		2006: 19.5,
		2007: 19.9,
		2008: 19.9,
		2009: 19.9,
		2010: 19.9,
		2011: 19.9,
		2012: 19.6,
		2013: 18.9,
		2014: 18.9,
		2015: 18.7,
		2016: 18.7,
		2017: 18.7,
		2018: 18.6,
		2019: 18.6,
		2020: 18.6,
		2021: 18.6,
		2022: 18.6,
		2023: 18.6,
		2024: 18.6,
		currentYear: {{ RENTENVERSICHERUNG_TOTAL_CONTRIBUTION }}, // {{ fail_on('2024-12-31') }}
		2025: 18.6, // ESTIMATED (2024)
		2026: 18.6, // ESTIMATED (2024)
	},
}

const occupations = {
	isEmployed: (occupation) => ['employee', 'azubi', 'studentEmployee'].includes(occupation),
	isSelfEmployed: (occupation) => ['selfEmployed', 'studentSelfEmployed'].includes(occupation),
	isUnemployed: (occupation) => ['unemployed', 'student'].includes(occupation),
	isMinijob: (occupation, monthlyIncome) => ['employee', 'studentEmployee'].includes(occupation) && monthlyIncome <= taxes.maxMinijobIncome,
	isLowIncome: (monthlyIncome) => monthlyIncome <= taxes.maxMinijobIncome,
};

const defaults = {  // Percentages are stored as full amounts, unlike elsewhere
	age: 25,
	childrenCount: 0,
	church: 'other',
	isMarried: false,
	occupation: 'employee',
	state: 'be-east',
	useMonthlyIncome: false,
	yearlyIncome: Math.round({{ MEDIAN_INCOME_GERMANY }}/100) * 100,
	healthInsuranceType: 'unknown',
	privateHealthInsuranceCost: 550, // € per month
	publicHealthInsuranceZusatzbeitrag: healthInsurance.companies.average.zusatzbeitrag * 100, // %
};
{% endjs %}
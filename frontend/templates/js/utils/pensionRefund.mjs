import { pensions, taxes } from '/js/utils/constants.mjs';
import { eeaCountries, euCountries } from '/js/utils/countries.mjs';

function monthsBetween(dateA, dateB) {
	const startDate = new Date(dateA);
	const endDate = new Date(dateB);
	const yearDiff = endDate.getFullYear() - startDate.getFullYear();
	const monthDiff = endDate.getMonth() - startDate.getMonth() + 1; // +1 to count partial months
	return yearDiff * 12 + monthDiff;
}

export function estimateMonthlyPensionContributions(year, monthlyIncome, isInEastGermany){
	const maxMonthlyIncome = taxes.beitragsbemessungsgrenze[year][isInEastGermany ? 'east' : 'west'] / 12;
	const taxedIncome = Math.min(maxMonthlyIncome, monthlyIncome);
	return taxedIncome * pensions.contributionRates[year] / 2 / 100;
}

export function estimateYearlyPensionContributions(year, yearlyIncome, isInEastGermany, monthsWorked = 12){
	return estimateMonthlyPensionContributions(year, yearlyIncome / 12, isInEastGermany) * monthsWorked;
}

function estimatePensionContributions(startDate, endDate, yearlyIncome, isInEastGermany) {
	const startMonth = startDate.getMonth(); // 0-based number, so December is 11
	const endMonth = endDate.getMonth();

	if (startDate.getFullYear() === endDate.getFullYear()){
		return estimateYearlyPensionContributions(endDate.getFullYear(), yearlyIncome, isInEastGermany, endMonth - startMonth + 1);
	}
	else {
		const monthsWorkedInFirstYear = 12 - startMonth;
		const monthsWorkedInLastYear = endMonth + 1;
		let total = 0;

		// Contributions for the (incomplete) first year
		total += estimateYearlyPensionContributions(startDate.getFullYear(), yearlyIncome, isInEastGermany, monthsWorkedInFirstYear);

		// Contributions for the complete years of work
		for(let year=startDate.getFullYear() + 1; year < endDate.getFullYear(); year++) {
			total += estimateYearlyPensionContributions(year, yearlyIncome, isInEastGermany)
		}

		// Contributions for the last year of work
		total += estimateYearlyPensionContributions(endDate.getFullYear(), yearlyIncome, isInEastGermany, monthsWorkedInLastYear);
		return total;
	}
}

export function calculatePensionRefund(nationality, countryOfResidence, entryDate, exitDate, yearlyIncome, isInEastGermany){
	const monthsContributed = monthsBetween(entryDate, exitDate);
	const monthsSinceLastContribution = monthsBetween(exitDate, new Date());
	const flags = new Set();
	let refundAmount = null;

	// EU resident
	if(euCountries.has(countryOfResidence) && !eeaCountries.has(nationality)){
		flags.add('not-eligible');
		flags.add('eu-resident');
	}

	// EU
	if (euCountries.has(nationality)){
		flags.add('not-eligible');
		flags.add('eu-national');
	}
	// EEA
	else if (eeaCountries.has(nationality)){
		flags.add('not-eligible');
		flags.add('eea-national');
	}
	// Contributing countries (mostly the balkans)
	else if (pensions.balkanBlockCountries.has(nationality)) {
		flags.add('balkanblock-national');
		if (pensions.disqualifyingCountries.has(countryOfResidence)) {
			flags.add('not-eligible');
			flags.add('disqualifying-country-resident');
		}
		if(monthsContributed >= 60) {
			flags.add('not-eligible');
			flags.add('over-5-years');
		}
	}
	// UK gets treated the same as EU citizens, basically.
	else if (nationality == 'GB'){
		flags.add('not-eligible');
		flags.add('uk-national');
	}
	// Israeli
	else if (nationality === 'IL') {
		flags.add('israel-national');
		if (pensions.disqualifyingCountries.has(countryOfResidence)) {
			flags.add('not-eligible');
			flags.add('disqualifying-country-resident');
		}
		else if (countryOfResidence === 'IL') {
			flags.add('not-eligible');
			flags.add('israel-resident');
		}
		else if(monthsContributed >= 60) {
			flags.add('not-eligible');
			flags.add('over-5-years');
		}
	}
	// Japanese
	else if (nationality === 'JP') {
		flags.add('japan-national');
		if (pensions.disqualifyingCountries.has(countryOfResidence)) {
			flags.add('not-eligible');
			flags.add('disqualifying-country-resident');
		}
		else if (countryOfResidence === 'JP') {
			if(monthsContributed >= 60) {
				flags.add('not-eligible');
				flags.add('over-5-years');
			}
			flags.add('japan-resident');
		}
	}
	// Turkish
	else if (nationality === 'TR') {
		flags.add('turkey-national');
		if(monthsContributed >= 60) {
			if (countryOfResidence === 'TR') {
				flags.add('turkey-resident');
			}
			else{
				flags.add('not-eligible');
				flags.add('over-5-years');
			}
		}
	}
	// Contracting country nationals
	else if (pensions.contractingCountries.has(nationality)) {
		flags.add('contracting-national');
		if (pensions.disqualifyingCountries.has(countryOfResidence)) {
			flags.add('not-eligible');
			flags.add('disqualifying-country-resident');
		}
		else if(monthsContributed >= 60) {
			flags.add('not-eligible');
			flags.add('over-5-years');
		}
	}
	else {
		flags.add('noncontracting-national');
	}

	// UK residents get treated like EU residents, basically
	if (countryOfResidence == 'GB'){
		flags.add('not-eligible');
		flags.add('uk-resident');
	}

	if(!flags.has('not-eligible')) {
		if(monthsSinceLastContribution >= 24) {
			flags.add('eligible');
		}
		else {
			flags.add('eligible-later');
		}
	}

	if(!flags.has('not-eligible') && entryDate && exitDate && yearlyIncome) {
		refundAmount = estimatePensionContributions(entryDate, exitDate, yearlyIncome, isInEastGermany);
	}

	return { flags, refundAmount };
}
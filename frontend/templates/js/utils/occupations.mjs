import { healthInsurance, taxes } from '/js/utils/constants.mjs';

// Full list: azubi, employee, selfEmployed, studentEmployee, studentSelfEmployed, studentUnemployed, unemployed
export function salaryOrIncome(occupation){
	return ['employee', 'azubi'].includes(occupation) ? 'salary' : 'income';
}

export function isEmployed(occupation){
	return ['employee', 'azubi', 'studentEmployee'].includes(occupation);
}

export function isSelfEmployed(occupation){
	return ['selfEmployed', 'studentSelfEmployed'].includes(occupation);
}

export function isUnemployed(occupation){
	return ['unemployed', 'studentUnemployed'].includes(occupation);
}

export function isStudent(occupation){
	return ['studentUnemployed', 'studentEmployee', 'studentSelfEmployed'].includes(occupation);
}

export function isLowIncome(monthlyIncome){
	return monthlyIncome <= taxes.maxMinijobIncome;
}

export function isMinijob(occupation, monthlyIncome){
	// Note: A minijob does not guarantee the minijob (self-pay) tariff.
	// A student with a minijob would still pay the student tariff.
	return (
		isEmployed(occupation)
		&& occupation !== 'azubi' // No minijob tariff for an Ausbildung
		&& monthlyIncome <= taxes.maxMinijobIncome
	);
}

function isMidijob(occupation, monthlyIncome){
	// No midijob tariff for Azubis
	// https://www.haufe.de/sozialwesen/versicherungen-beitraege/auszubildende-besonderheiten-bei-den-neuen/besonderheiten-bei-der-beitragsberechnung_240_94670.html
	return (
		isEmployed(occupation)
		&& occupation !== 'azubi'
		&& !isMinijob(occupation, monthlyIncome)
		&& monthlyIncome <= healthInsurance.maxMidijobIncome
	);
}
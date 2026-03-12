import { taxes } from '/js/utils/constants.mjs';
import { calculateIncomeTax, calculateChurchTax, calculateSolidarityTax, calculateUnemploymentInsurance } from '/js/utils/tax.mjs';
import { assert } from '/js/libs/chai.mjs';

describe('calculateUnemploymentInsurance', () => {
	const testCases = [
		{
			name: 'an employee with a very high income in West Germany',
			args: [200000, 'employee', false],
			output: {
				flags: ['max-contribution'],
				unemploymentInsurance: taxes.beitragsbemessungsgrenze.currentYear.west * taxes.arbeitslosenversicherungRate,
			},
		},
		{
			name: 'an employee with a very high income in East Germany',
			args: [200000, 'employee', true],
			output: {
				flags: ['max-contribution'],
				unemploymentInsurance: taxes.beitragsbemessungsgrenze.currentYear.east * taxes.arbeitslosenversicherungRate,
			},
		},
		{
			name: 'an employee with a very high income in East Germany',
			args: [50000, 'employee', true],
			output: {
				flags: [],
				unemploymentInsurance: 50000 * taxes.arbeitslosenversicherungRate,
			},
		},
		{
			name: 'a freelancer',
			args: [200000, 'selfEmployed', true],
			output: {
				flags: ['optional'],
				unemploymentInsurance: 0,
			},
		},
		{
			name: 'a minijobber',
			args: [taxes.maxMinijobIncome * 12, 'employee', false],
			output: {
				flags: ['none', 'minijob',],
				unemploymentInsurance: 0,
			},
		},
		{
			name: 'an Azubi',
			args: [taxes.maxMinijobIncome * 12, 'azubi', false],
			output: {
				flags: ['azubi'],
				unemploymentInsurance: taxes.maxMinijobIncome * 12 * taxes.arbeitslosenversicherungRate,
			},
		},
		{
			name: 'an unemployed person',
			args: [2000, 'unemployed', false],
			output: {
				flags: ['none', 'unemployed',],
				unemploymentInsurance: 0,
			},
		},
	];

	testCases.forEach(testCase => {
		it(`calculates the correct values for ${testCase.name}`, function() {
			const output = calculateUnemploymentInsurance(...testCase.args);
			testCase.output.flags = Array.from(testCase.output.flags).sort();
			output.flags = Array.from(output.flags).sort();
			assert.deepEqual(testCase.output, output);
		});
	});
});

describe.skip('calculateIncomeTax', () => {
	const incomeTax9990 = 0;
	const incomeTax14900 = 863;
	const incomeTax58500 = 15233;
	const incomeTax60000 = 15863;
	const incomeTax277000 = 107003;
	const incomeTax280000 = 108328;

	const testCases = [ // https://einkommensteuertabellen.finanz-tools.de/grundtabelle/2022
		{
			yearlyIncome: 0, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-1'],
				incomeTax: 0,
			},
		},
		{
			yearlyIncome: 9990, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-1'],
				incomeTax: incomeTax9990,
			},
		},
		{
			yearlyIncome: 14900, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-2'],
				incomeTax: incomeTax14900,
			},
		},
		{
			yearlyIncome: 58500, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-3'],
				incomeTax: incomeTax58500,
			},
		},
		{
			yearlyIncome: 60000, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-4'],
				incomeTax: incomeTax60000,
			},
		},
		{
			yearlyIncome: 277000, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-4'],
				incomeTax: incomeTax277000,
			},
		},
		{
			yearlyIncome: 280000, splittingTarif: false,
			output: {
				flags: ['income-tax-bracket-5'],
				incomeTax: incomeTax280000,
			},
		},
		{
			yearlyIncome: 0, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-1', 'splittingtarif'],
				incomeTax: 0,
			},
		},
		{
			yearlyIncome: 9990 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-1', 'splittingtarif'],
				incomeTax: incomeTax9990,
			},
		},
		{
			yearlyIncome: 14900 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-2', 'splittingtarif'],
				incomeTax: incomeTax14900 * 2,
			},
		},
		{
			yearlyIncome: 58500 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-3', 'splittingtarif'],
				incomeTax: incomeTax58500 * 2,
			},
		},
		{
			yearlyIncome: 60000 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-4', 'splittingtarif'],
				incomeTax: incomeTax60000 * 2,
			},
		},
		{
			yearlyIncome: 277000 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-4', 'splittingtarif'],
				incomeTax: incomeTax277000 * 2,
			},
		},
		{
			yearlyIncome: 280000 * 2, splittingTarif: true,
			output: {
				flags: ['income-tax-bracket-5', 'splittingtarif'],
				incomeTax: incomeTax280000 * 2,
			},
		},
	];

	testCases.forEach(testCase => {
		it(`calculates the correct values for a ${testCase.yearlyIncome}€ income`, function() {
			const output = calculateIncomeTax(testCase.yearlyIncome, testCase.splittingTarif);
			testCase.output.flags = Array.from(testCase.output.flags).sort();
			output.flags = Array.from(output.flags).sort();
			assert.deepEqual(output, testCase.output);
		});
	});
});

describe('calculateChurchTax', () => {
	const testCases = [
		{
			incomeTax: 1500, germanState: 'hh',
			output: {
				churchTax: 1500 * 0.09,
				churchTaxRate: 0.09,
			},
		},
		{
			incomeTax: 1500, germanState: 'bw',
			output: {
				churchTax: 1500 * 0.08,
				churchTaxRate: 0.08,
			},
		},
		{
			incomeTax: 0, germanState: 'bw',
			output: {
				churchTax: 0,
				churchTaxRate: 0.08,
			},
		},
	];

	testCases.forEach(testCase => {
		it(`calculates the correct values for a ${testCase.incomeTax}€ income tax`, function() {
			const output = calculateChurchTax(testCase.incomeTax, testCase.germanState);
			assert.deepEqual(testCase.output, output);
		});
	});
});

describe.skip('calculateSolidarityTax', () => {
	const testCases = [
		{
			incomeTax: 15212,
			output: {
				flags: new Set(['soli-zero']),
				solidarityTax: 0,
			},
		},
		{
			incomeTax: 17140,
			output: {
				flags: new Set(['soli-mid-rate']),
				solidarityTax: 21.89,
			},
		},
		{
			incomeTax: 25975,
			output: {
				flags: new Set(['soli-mid-rate']),
				solidarityTax: 1073.26,
			},
		},
		{
			incomeTax: 27310,
			output: {
				flags: new Set(['soli-mid-rate']),
				solidarityTax: 1232.12,
			},
		},
		{
			incomeTax: 138588,
			output: {
				flags: new Set(['soli-max-rate']),
				solidarityTax: 7622.34,
			},
		},
	];

	testCases.forEach(testCase => {
		it(`calculates the correct values for a ${testCase.incomeTax}€ income tax`, function() {
			const output = calculateSolidarityTax(testCase.incomeTax);
			assert.deepEqual(testCase.output, output);
		});
	});
});
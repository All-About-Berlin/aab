import { formatCurrency } from '/js/utils/currency.mjs';
import { assert } from '/js/libs/chai.mjs';

describe('formatCurrency', () => {
	const testCases = [
		{
			args: [1234567.89, true],
			output: '€1,234,567.89',
		},
		{
			args: [1234567.89, true, '$'],
			output: '$1,234,567.89',
		},
		{
			args: [1234567.89, true, null],
			output: '1,234,567.89',
		},
		{
			args: [1234567.89, false],
			output: '€1,234,568',
		},
		{
			args: [1234567.89, false, '$'],
			output: '$1,234,568',
		},
		{
			args: [567.89, false],
			output: '€568',
		},
		{
			args: [567.89, true],
			output: '€567.89',
		},
		{
			args: [4567.89, false],
			output: '€4,568',
		},
		{
			args: [4567.89, true],
			output: '€4,567.89',
		},
		{
			args: [1234567.89, false, null],
			output: '1,234,568',
		},
		{
			args: [7.84 + 4.28, true, null], // Floating error test
			output: '12.12',
		},
		{
			args: [-0.0002, true, null], // "-0.00" test
			output: '0.00',
		},
		{
			args: [-0.01, true, null],
			output: '-0.01',
		},
		{
			args: [-0.01, false, null],
			output: '0',
		},
	];

	testCases.forEach(testCase => {
		it(`calculates the correct values`, function() {
			const output = formatCurrency(...testCase.args);
			assert.equal(output, testCase.output);
		});
	});
});
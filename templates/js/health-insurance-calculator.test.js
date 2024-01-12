import { hasFlag, notHasFlag } from './test-utils.js';

const round = roundCurrency;
const equal = assert.equal;

function hasStudentTarif(output) {
	equal(output.tarif, 'student');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.studentTarif * bafogBedarfssatz));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.companies.tk.zusatzbeitrag * bafogBedarfssatz));
	equal(
		output.pflegeversicherung.totalContribution,
		round(pflegeversicherung.defaultTarif * bafogBedarfssatz));
	equal(output.options.tk.total.employerContribution, 0);
	notHasFlag(output, 'student-30plus')();
}
function hasStudentTarifWithExtraPflegeversicherung(output) {
	equal(output.tarif, 'student');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.studentTarif * bafogBedarfssatz));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.companies.tk.zusatzbeitrag * bafogBedarfssatz));
	equal(
		output.pflegeversicherung.totalContribution,
		round(pflegeversicherung.surchargeTarif * bafogBedarfssatz));
	equal(output.options.tk.total.employerContribution, 0);
	notHasFlag(output, 'student-30plus')();
}

function hasMinimumSelfEmployedTarif(output) {
	equal(output.tarif, 'selfEmployed');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.selfEmployedTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.minMonthlyIncome * pflegeversicherung.defaultTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'min-contribution')();
}
function hasMinimumSelfEmployedTarifWithExtraPflegeversicherung(output) {
	equal(output.tarif, 'selfEmployed');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.selfEmployedTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.minMonthlyIncome * pflegeversicherung.surchargeTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'min-contribution')();
}

function hasMaximumSelfEmployedTarif(output) {
	equal(output.tarif, 'selfEmployed');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.selfEmployedTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.maxMonthlyIncome * pflegeversicherung.defaultTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'max-contribution')();
}
function hasMaximumSelfEmployedTarifWithExtraPflegeversicherung(output) {
	equal(output.tarif, 'selfEmployed');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.selfEmployedTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.maxMonthlyIncome * pflegeversicherung.surchargeTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'max-contribution')();
}

function hasMinimumSelfPayTarif(output) {
	equal(output.tarif, 'selfPay');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.defaultTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.minMonthlyIncome * pflegeversicherung.defaultTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'min-contribution')();
}
function hasMinimumSelfPayTarifWithExtraPflegeversicherung(output) {
	equal(output.tarif, 'selfPay');
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.defaultTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.minMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.minMonthlyIncome * pflegeversicherung.surchargeTarif));
	equal(output.options.tk.total.employerContribution, 0);
	hasFlag(output, 'min-contribution')();
}

function hasStandardTarif2001(output) {
	equal(
		output.baseContribution.totalContribution,
		round(2001 * healthInsurance.defaultTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(2001 * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(2001 * pflegeversicherung.defaultTarif));
	equal(
		output.options.tk.total.employerContribution,
		round(2001 * healthInsurance.defaultTarif / 2)
			+ round(2001 * healthInsurance.companies.tk.zusatzbeitrag / 2)
			+ round(2001 * pflegeversicherung.employerTarif)
	);
}
function hasMaxTarif(output) {
	equal(
		output.baseContribution.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultTarif));
	equal(
		output.options.tk.zusatzbeitrag.totalContribution,
		round(healthInsurance.maxMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag));
	equal(
		output.pflegeversicherung.totalContribution,
		round(healthInsurance.maxMonthlyIncome * pflegeversicherung.defaultTarif));
	equal(
		output.options.tk.total.employerContribution,
		round(
			round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultTarif / 2)
			+ round(healthInsurance.maxMonthlyIncome * healthInsurance.companies.tk.zusatzbeitrag / 2)
			+ round(healthInsurance.maxMonthlyIncome * pflegeversicherung.employerTarif)
		));
	hasFlag(output, 'max-contribution')();
}

describe('calculateHealthInsuranceContributions', () => {
	describe('married people with a low income', () => {
		const output = calculateHealthInsuranceContributions({
			age: 40,
			childrenCount: 0,
			isMarried: true,
			occupation: 'unemployed',
			monthlyIncome: taxes.maxMinijobIncome,
		});
		it('can use their spouse\'s insurance', hasFlag(output, 'familienversicherung-spouse'));
	});

	describe('unmarried people with a low income', () => {
		const output = calculateHealthInsuranceContributions({
			age: 40,
			childrenCount: 0,
			isMarried: false,
			occupation: 'unemployed',
			monthlyIncome: taxes.maxMinijobIncome,
		});
		it('can\'t use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
	});

	describe('students', () => {
		describe('a 22 year old student with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 23 year old student with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 25 year old student with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 25,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 25,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 29 year old student with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 29,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 29,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 30 year old student with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 30,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 30,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the minimum rate (minijob)', () => {
				hasFlag(outputWithKids, 'minijob')();
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('can\'t get the student tarif', hasFlag(outputNoKids, 'student-30plus'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe(`a 22 year old student with a ${taxes.maxMinijobIncome + 1}€ job`, () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe(`a 22 year old student with a ${taxes.maxMinijobIncome + 1}€ job`, () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the student rate', () => {
				hasStudentTarif(outputWithKids);
				hasStudentTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a student with a 20 hr/week, 1500€/month job', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: 1500,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: 1500,
			});

			it('must pay the student rate', () => {
				notHasFlag(outputNoKids, 'not-nebenjob')();
				hasStudentTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a student with a 20 hr/week, 2001€/month job', () => {
			const output = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'studentEmployee',
				monthlyIncome: 2001,
			});

			it('must pay the employee rate due to their high income', () => {
				hasStandardTarif2001(output);
				equal(output.tarif, 'employee');
				hasFlag(output, 'not-nebenjob')();
			});

			it('can\'t get the student tarif due to their high income', hasFlag(output, 'not-nebenjob'));
			it('can\'t get private health insurance', notHasFlag(output, 'private'));
			it('can\'t use their EHIC card', notHasFlag(output, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(output, 'familienversicherung-parents'));
		});

		// TODO: Students with freelance income
	});

	describe('unemployed people', () => {
		describe('a 17 year old unemployed person', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 17,
				childrenCount: 1,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 17,
				childrenCount: 0,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});

			it('must pay the minimum rate', () => {
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('an 18 year old unemployed person', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 18,
				childrenCount: 1,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 18,
				childrenCount: 0,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});

			it('must pay the minimum rate', () => {
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 22 year old unemployed person', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});

			it('must pay the minimum rate', () => {
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarif(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('does not pay more for Pflegeversicherung if he has no kids', notHasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 23 year old unemployed person', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'unemployed',
				monthlyIncome: 0,
			});

			it('must pay the minimum rate', () => {
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});
	});

	describe('employees', () => {
		describe('a 17 year old employee with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 17,
				childrenCount: 1,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 17,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the minijob tarif', () => {
				hasFlag(outputWithKids, 'minijob')();
				hasFlag(outputNoKids, 'minijob')();
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarif(outputNoKids);
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe('a 22 year old employee with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the minijob tarif', () => {
				hasFlag(outputWithKids, 'minijob')();
				hasFlag(outputNoKids, 'minijob')();
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarif(outputNoKids);
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe('a 23 year old employee with a minijob', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the minijob tarif', () => {
				hasFlag(outputWithKids, 'minijob')();
				hasFlag(outputNoKids, 'minijob')();
				hasMinimumSelfPayTarif(outputWithKids);
				hasMinimumSelfPayTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can use their EHIC card', hasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('does not pay more for Pflegeversicherung if he has kids', notHasFlag(outputWithKids, 'pflegeversicherung-surcharge'));
			it('pays more for Pflegeversicherung if he has no kids', hasFlag(outputNoKids, 'pflegeversicherung-surcharge'));
		});

		describe('a 17 year old employee with a 2001€ job', () => {
			const output = calculateHealthInsuranceContributions({
				age: 17,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: 2001,
			});

			it('must pay the employee rate', () => {
				hasStandardTarif2001(output);
				equal(output.tarif, 'employee');
			});

			it('does not pay the minijob tarif', notHasFlag(output, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(output, 'private'));
			it('can\'t use their EHIC card', notHasFlag(output, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(output, 'familienversicherung-parents'));
		});

		describe('an 18 year old employee with a 2001€ job', () => {
			const output = calculateHealthInsuranceContributions({
				age: 19,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: 2001,
			});

			it('must pay the employee rate', () => {
				hasStandardTarif2001(output);
				equal(output.tarif, 'employee');
			});

			it('does not pay the minijob tarif', notHasFlag(output, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(output, 'private'));
			it('can\'t use their EHIC card', notHasFlag(output, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(output, 'familienversicherung-parents'));
		});

		describe(`a 23 year old employee with a ${taxes.maxMinijobIncome + 1}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the midijob tarif', () => {
				equal(outputWithKids.tarif, 'midijob');
				equal(outputWithKids.baseContribution.totalContribution, 52.71);
				equal(outputWithKids.options.tk.zusatzbeitrag.totalContribution, 4.33);
				equal(outputWithKids.pflegeversicherung.totalContribution, 12.28);
				equal(outputNoKids.tarif, 'midijob');
				equal(outputNoKids.baseContribution.totalContribution, 52.71);
				equal(outputNoKids.options.tk.zusatzbeitrag.totalContribution, 4.33);
				equal(outputNoKids.pflegeversicherung.totalContribution, 14.44);
			});

			it('must pay a smaller share than the employer', () => {
				equal(outputWithKids.options.tk.total.employerContribution, 69.19);
				equal(outputNoKids.options.tk.total.employerContribution, 69.17);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`a 22 year old employee with a ${taxes.maxMinijobIncome + 1}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the midijob tarif', () => {
				equal(outputNoKids.tarif, 'midijob');
				equal(outputNoKids.baseContribution.totalContribution, 52.71);
				equal(outputNoKids.options.tk.zusatzbeitrag.totalContribution, 4.33);
				equal(outputNoKids.pflegeversicherung.totalContribution, 12.28);
			});

			it('must pay a smaller share than the employer', () => {
				equal(outputNoKids.options.tk.total.employerContribution, 69.19);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`an employee with a ${taxes.maxMinijobIncome + 1}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the midijob tarif', () => {
				equal(outputNoKids.tarif, 'midijob');
				equal(outputNoKids.baseContribution.totalContribution, 52.71);
				equal(outputNoKids.options.tk.zusatzbeitrag.totalContribution, 4.33);
				equal(outputNoKids.pflegeversicherung.totalContribution, 12.28);
			});

			it('must pay a smaller share than the employer', () => {
				equal(outputNoKids.options.tk.total.employerContribution, 69.19);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`an employee with a ${healthInsurance.midijobMaxIncome}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: healthInsurance.midijobMaxIncome,
			});

			it('must pay the midijob tarif', () => {
				equal(outputNoKids.tarif, 'midijob');
				equal(outputNoKids.baseContribution.totalContribution, 292);
				equal(outputNoKids.options.tk.zusatzbeitrag.totalContribution, 24);
				equal(outputNoKids.pflegeversicherung.totalContribution, 68);
			});

			it('must pay a smaller share than the employer', () => {
				equal(outputNoKids.options.tk.total.employerContribution, 146 + 12 + 34);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`an employee with a ${healthInsurance.midijobMaxIncome + 1}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: healthInsurance.midijobMaxIncome + 1,
			});

			it('must pay the employee tarif', () => {
				equal(outputNoKids.tarif, 'employee');
			});

			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
		});

		describe('an employee with a 5000€ job', () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: 5000,
			});

			it('must pay the maximum employee tarif', () => {
				hasMaxTarif(outputNoKids);
				equal(outputNoKids.tarif, 'employee');
			});

			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
		});

		describe(`an employee with a ${healthInsurance.minFreiwilligMonthlyIncome}€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'employee',
				monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome,
			});

			it('must pay the maximum employee tarif', () => {
				hasMaxTarif(outputNoKids);
				equal(outputNoKids.tarif, 'employee');
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
		});

		describe(`an employee with a 200,000€ job`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: false,
				occupation: 'employee',
				monthlyIncome: 200000/12,
			});

			it('must pay the maximum employee tarif', () => {
				hasMaxTarif(outputNoKids);
				equal(outputNoKids.tarif, 'employee');
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
		});
	});

	describe('freelancers', () => {
		describe(`a 22 year old freelancer with a ${taxes.maxMinijobIncome}€ income`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 325,
			});
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 325,
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can use their spouse\'s insurance', hasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can use their parents\' insurance', hasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`a 22 year old freelancer with a ${taxes.maxMinijobIncome + 1}€ income`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the minimum self-employed tarif', () => {
				hasMinimumSelfEmployedTarif(output);
			});

			it('does not pay the minijob tarif', notHasFlag(output, 'minijob'));
			it('can get private health insurance', hasFlag(output, 'private'));
			it('can\'t use their EHIC card', notHasFlag(output, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(output, 'familienversicherung-parents'));
		});

		describe(`a 23 year old freelancer with a ${taxes.maxMinijobIncome + 1}€ income`, () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the minimum self-employed tarif', () => {
				hasMinimumSelfEmployedTarif(outputWithKids);
				hasMinimumSelfEmployedTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe('a 23 year old freelancer with a 1000€ income', () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 1000,
			});
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 1000,
			});

			it('must pay the minimum self-employed tarif', () => {
				hasMinimumSelfEmployedTarif(outputWithKids);
				hasMinimumSelfEmployedTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe('a 23 year old freelancer with a 5000€ job', () => {
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 5000,
			});
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'selfEmployed',
				monthlyIncome: 5000,
			});

			it('must pay the maximum self-employed tarif', () => {
				hasMaximumSelfEmployedTarif(outputWithKids);
				hasMaximumSelfEmployedTarifWithExtraPflegeversicherung(outputNoKids);
			});

			it('can get private health insurance', hasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});
	});

	describe('azubis', () => {
		describe('an Azubi with a 325€ income', () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 1,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: 325,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 23,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: 325,
			});

			it('must pay nothing', () => {
				equal(outputNoKids.tarif, 'azubi');
				equal(
					outputNoKids.baseContribution.totalContribution,
					round(325 * healthInsurance.defaultTarif));
				equal(
					outputNoKids.options.tk.zusatzbeitrag.totalContribution,
					round(325 * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputNoKids.pflegeversicherung.totalContribution,
					round(325 * pflegeversicherung.surchargeTarif));
				equal(
					round(
						round(325 * healthInsurance.defaultTarif)
						+ round(325 * healthInsurance.companies.tk.zusatzbeitrag)
						+ round(325 * pflegeversicherung.surchargeTarif)
					),
					outputNoKids.options.tk.total.employerContribution,);
				hasFlag(outputNoKids, 'azubi-free')();

				equal(outputWithKids.tarif, 'azubi');
				equal(
					outputWithKids.baseContribution.totalContribution,
					round(325 * healthInsurance.defaultTarif));
				equal(
					outputWithKids.options.tk.zusatzbeitrag.totalContribution,
					round(325 * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputWithKids.pflegeversicherung.totalContribution,
					round(325 * pflegeversicherung.defaultTarif));
				equal(
					round(
						round(325 * healthInsurance.defaultTarif)
						+ round(325 * healthInsurance.companies.tk.zusatzbeitrag)
						+ round(325 * pflegeversicherung.defaultTarif)
					),
					outputWithKids.options.tk.total.employerContribution,);
				hasFlag(outputNoKids, 'azubi-free')();
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
		});

		describe(`an Azubi with a ${taxes.maxMinijobIncome}€ income`, () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 1,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must pay the standard percentage of their income', () => {
				equal(outputNoKids.tarif, 'azubi');
				equal(
					outputNoKids.baseContribution.totalContribution,
					round(taxes.maxMinijobIncome * healthInsurance.defaultTarif));
				equal(
					outputNoKids.options.tk.zusatzbeitrag.totalContribution,
					round(taxes.maxMinijobIncome * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputNoKids.pflegeversicherung.totalContribution,
					round(taxes.maxMinijobIncome * pflegeversicherung.surchargeTarif));
				equal(outputNoKids.options.tk.total.employerContribution, 49.92);
				notHasFlag(outputNoKids, 'azubi-free')();

				equal(outputWithKids.tarif, 'azubi');
				equal(
					outputWithKids.baseContribution.totalContribution,
					round(taxes.maxMinijobIncome * healthInsurance.defaultTarif));
				equal(
					outputWithKids.options.tk.zusatzbeitrag.totalContribution,
					round(taxes.maxMinijobIncome * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputWithKids.pflegeversicherung.totalContribution,
					round(taxes.maxMinijobIncome * pflegeversicherung.defaultTarif));
				equal(outputWithKids.options.tk.total.employerContribution, 49.92);
				notHasFlag(outputWithKids, 'azubi-free')();
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('can\'t pay the Midijob tarif', notHasFlag(outputNoKids, 'midijob'));
		});

		describe(`an Azubi with a ${taxes.maxMinijobIncome + 1}€ income`, () => {
			const outputWithKids = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 1,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});
			const outputNoKids = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome + 1,
			});

			it('must pay the standard percentage of their income, not the midijob tarif', () => {
				equal(outputNoKids.tarif, 'azubi');
				equal(
					outputNoKids.baseContribution.totalContribution,
					round((taxes.maxMinijobIncome + 1) * healthInsurance.defaultTarif));
				equal(
					outputNoKids.options.tk.zusatzbeitrag.totalContribution,
					round((taxes.maxMinijobIncome + 1) * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputNoKids.pflegeversicherung.totalContribution,
					round((taxes.maxMinijobIncome + 1) * pflegeversicherung.surchargeTarif));
				equal(outputNoKids.options.tk.total.employerContribution, 50.02);
				notHasFlag(outputNoKids, 'azubi-free')();

				equal(outputWithKids.tarif, 'azubi');
				equal(
					outputWithKids.baseContribution.totalContribution,
					round((taxes.maxMinijobIncome + 1) * healthInsurance.defaultTarif));
				equal(
					outputWithKids.options.tk.zusatzbeitrag.totalContribution,
					round((taxes.maxMinijobIncome + 1) * healthInsurance.companies.tk.zusatzbeitrag));
				equal(
					outputWithKids.pflegeversicherung.totalContribution,
					round((taxes.maxMinijobIncome + 1) * pflegeversicherung.defaultTarif));
				equal(outputWithKids.options.tk.total.employerContribution, 50.02);
				notHasFlag(outputWithKids, 'azubi-free')();
			});

			it('does not pay the minijob tarif', notHasFlag(outputNoKids, 'minijob'));
			it('can\'t get private health insurance', notHasFlag(outputNoKids, 'private'));
			it('can\'t use their EHIC card', notHasFlag(outputNoKids, 'ehic'));
			it('can\'t use their spouse\'s insurance', notHasFlag(outputNoKids, 'familienversicherung-spouse'));
			it('can\'t use their parents\' insurance', notHasFlag(outputNoKids, 'familienversicherung-parents'));
			it('can\'t pay the Midijob tarif', notHasFlag(outputNoKids, 'midijob'));
		});

		describe('an Azubi with a 2001€ income', () => {
			const output = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: 2001,
			});

			it('must pay the standard percentage of their income', () => {
				hasStandardTarif2001(output);
				equal(output.tarif, 'azubi');
			});
			it('can\'t get private health insurance', notHasFlag(output, 'private'));
		});

		describe('an Azubi with a 5000€ income', () => {
			const output = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: 5000,
			});

			it('must pay the maximum employee tarif', () => {
				hasMaxTarif(output);
				equal(output.tarif, 'azubi');
			});

			it('can\'t get private health insurance', notHasFlag(output, 'private'));
		});

		describe(`an Azubi with a ${ healthInsurance.minFreiwilligMonthlyIncome }€ income`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 22,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome,
			});

			it('must pay the maximum employee tarif', () => {
				hasMaxTarif(output);
				equal(output.tarif, 'azubi');
			});

			it('can get private health insurance', hasFlag(output, 'private'));
		});
	});

	describe('parents', () => {
		describe(`a person with no children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 0,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('pays extra for Pflegeversicherung', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.surchargeTarif);
			});
		});
		describe(`a parent with 1 child`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 1,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('gets no Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif);
			});
		});
		describe(`a parent with 2 children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 2,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must get a 0.25% Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif - 0.25/100);
			});
		});
		describe(`a parent with 3 children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 3,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must get a 0.5% Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif - 0.5/100);
			});
		});
		describe(`a parent with 4 children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 4,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must get a 0.75% Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif - 0.75/100);
			});
		});
		describe(`a parent with 5 children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 5,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must get a 1% Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif - 1/100);
			});
		});
		describe(`a parent with 6 children`, () => {
			const output = calculateHealthInsuranceContributions({
				age: 32,
				childrenCount: 6,
				isMarried: true,
				occupation: 'azubi',
				monthlyIncome: taxes.maxMinijobIncome,
			});

			it('must get a 1% Pflegeversicherung discount', () => {
				equal(output.pflegeversicherung.totalRate, pflegeversicherung.defaultTarif - 1/100);
			});
		});
	});
});

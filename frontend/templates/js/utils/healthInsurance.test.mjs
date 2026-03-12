// TODO: Test custom zusatzbeitrag
import { roundCurrency } from '/js/utils/currency.mjs';
import { bafog, healthInsurance, pflegeversicherung, taxes } from '/js/utils/constants.mjs';
import { getHealthInsuranceOptions } from '/js/utils/healthInsurance.mjs';
import { assert } from '/js/libs/chai.mjs';
import { hasFlag, notHasFlag } from '/js/utils/test.mjs';

const round = roundCurrency;
const equal = assert.equal;
const defaultInsurer = Object.values(healthInsurance.companies)[0];

describe('An unemployed student', () => {
	const student = {
		occupation: 'studentUnemployed',
		monthlyIncome: 0,
		hoursWorkedPerWeek: 0,
		age: 22,
	}

	const studentTests = [
		hasStudentTariff,
		canUseSpouseInsurance,
		canUseParentsInsurance,
		cannotJoinKSK,
		earnsEnoughForPrivate,
	];

	testInsuranceOptions({
		...student,
	}, [
		...studentTests,
	]);

	describe('with EU public insurance', () => {
		testInsuranceOptions({
			...student,
			hasEUPublicHealthInsurance: true,
		}, [
			canUseEHIC,
			getsRecommended(['public', 'expat', 'private', 'other']),
		]);
	});

	describe('with German public insurance', () => {
		testInsuranceOptions({
			...student,
			hasGermanPublicHealthInsurance: true,
		}, [
			cannotUseEHIC,
			getsRecommended(['public', 'private', 'other']),
		]);
	});

	describe('without insurance', () => {
		testInsuranceOptions(student, [
			cannotUseEHIC,
			getsRecommended(['public', 'expat', 'private', 'other']),
		]);
	});

	describe('applying for a visa', () => {
		testInsuranceOptions({
			...student,
			isApplyingForFirstVisa: true,
		}, [
			mustHaveExpatInsurance,
			getsRecommended(['public', 'expat', 'private', 'other']),
		]);
	});

	describe('after 25 years old', () => {
		testInsuranceOptions({
			...student,
			age: 25,
		}, [
			getsRecommended(['public', 'expat', 'private', 'other']),
			cannotUseParentsInsurance,
		]);
	});

	describe('over 30 years old', () => {
		describe('with EU public insurance', () => {
			testInsuranceOptions({
				...student,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
				hasEUPublicHealthInsurance: true,
			}, [
				isTooOldForStudentTariff,
				getsRecommended(['expat', 'public', 'private']),
				cannotUseSpouseInsurance,
				cannotUseParentsInsurance,
			]);
		});

		describe('with German public insurance', () => {
			testInsuranceOptions({
				...student,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
				hasGermanPublicHealthInsurance: true,
			}, [
				isTooOldForStudentTariff,
				getsRecommended(['public', 'private']),
				cannotUseSpouseInsurance,
				cannotUseParentsInsurance,
			]);
		});

		describe('without insurance', () => {
			testInsuranceOptions({
				...student,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
			}, [
				getsRecommended(['expat', 'private']),
				cannotUseSpouseInsurance,
				cannotUseParentsInsurance,
			]);
		});
	});
});

describe('A working student', () => {
	const workingStudent = {
		occupation: 'studentEmployee',
		monthlyIncome: 0,
		age: 22,
	};

	const workingStudentTests = [
		cannotUseSpouseInsurance,
		cannotUseParentsInsurance,
		cannotUseEHIC,
		cannotJoinKSK,
		earnsEnoughForPrivate,
	];

	describe('working 20 hours per week', () => {
		testInsuranceOptions({
			...workingStudent,
			hoursWorkedPerWeek: 20,
			monthlyIncome: 1300,
		}, [
			hasStudentTariff,
			getsRecommended(['public', 'expat', 'private']),
			...workingStudentTests,
		]);
	});

	describe('working 21 hours per week', () => {
		testInsuranceOptions({
			...workingStudent,
			hoursWorkedPerWeek: 21,
			monthlyIncome: 1500,
		}, [
			hasMidijobTariff,
			isNotWerkstudentDueToHoursWorked,
			getsRecommended(['public']),
			...workingStudentTests,
		]);
	});

	describe(`with a minijob (€${taxes.maxMinijobIncome}/m)`, () => {
		testInsuranceOptions({
			...workingStudent,
			hoursWorkedPerWeek: 20,
			monthlyIncome: taxes.maxMinijobIncome,
		}, [
			hasStudentTariff,
			getsRecommended(['public', 'expat', 'private', 'other']),
			canUseSpouseInsurance,
			canUseParentsInsurance,
		]);
	});

	describe(`with a high income (€${Math.ceil(0.75 * healthInsurance.maxNebenjobIncome + 1)}/m)`, () => {
		testInsuranceOptions({
			...workingStudent,
			hoursWorkedPerWeek: 20,
			monthlyIncome: Math.ceil(0.75 * healthInsurance.maxNebenjobIncome + 1),
		}, [
			hasEmployeeTarif,
			getsRecommended(['public']),
			isNotWerkstudentDueToIncome,
			...workingStudentTests,
		]);
	});

	describe('over 30 years old', () => {
		describe('with EU public insurance', () => {
			testInsuranceOptions({
				...workingStudent,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
				hasEUPublicHealthInsurance: true,
			}, [
				isTooOldForStudentTariff,
				getsRecommended(['expat', 'public', 'private']),
			]);

			describe('with a minijob', () => {
				testInsuranceOptions({
					...workingStudent,
					hoursWorkedPerWeek: 10,
					monthlyIncome: taxes.maxMinijobIncome,
					age: 30,
					hasEUPublicHealthInsurance: true,
				}, [
					isTooOldForStudentTariff,
					hasMinijobTariffWithPflegeversicherungSurcharge,
					canUseSpouseInsurance,
					cannotUseParentsInsurance,
					getsRecommended(['expat', 'public', 'private', 'other']),
				]);
			});
		});

		describe('with German public insurance', () => {
			testInsuranceOptions({
				...workingStudent,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
				hasGermanPublicHealthInsurance: true,
			}, [
				isTooOldForStudentTariff,
				getsRecommended(['public', 'private']),
			]);
		});

		describe('without insurance', () => {
			testInsuranceOptions({
				...workingStudent,
				hoursWorkedPerWeek: 20,
				monthlyIncome: 1300,
				age: 30,
			}, [
				getsRecommended(['expat', 'private']),
			]);

			describe('with a minijob', () => {
				testInsuranceOptions({
					...workingStudent,
					hoursWorkedPerWeek: 10,
					monthlyIncome: taxes.maxMinijobIncome,
					age: 30,
				}, [
					getsRecommended(['expat', 'private', 'other']),
				]);
			});
		});
	});
});

describe('A self-employed student', () => {
	const selfEmployedStudent = {
		occupation: 'studentSelfEmployed',
		monthlyIncome: 1200,
		age: 22,
		hoursWorkedPerWeek: 20,
	};

	const selfEmployedStudentTests = [
		cannotUseSpouseInsurance,
		cannotUseParentsInsurance,
		cannotUseEHIC,
		earnsEnoughForPrivate,
	];

	describe('working 20 hours per week', () => {
		testInsuranceOptions({
			...selfEmployedStudent,
			hoursWorkedPerWeek: 20,
			monthlyIncome: 1300,
		}, [
			hasStudentTariff,
			getsRecommended(['public', 'expat', 'private', 'other']),
			canJoinKSK,
			...selfEmployedStudentTests,
		]);
	});

	describe('working 21 hours per week', () => {
		describe('with existing German public health insurance', () => {
			testInsuranceOptions({
				...selfEmployedStudent,
				hoursWorkedPerWeek: 21,
				monthlyIncome: 1500,
				hasGermanPublicHealthInsurance: true,
			}, [
				hasSelfEmployedTariff,
				getsRecommended(['public', 'private']),
				isNotWerkstudentDueToHoursWorked,
				cannotJoinKSK,
				...selfEmployedStudentTests,
			]);
		});

		describe('with existing EU public health insurance', () => {
			testInsuranceOptions({
				...selfEmployedStudent,
				hoursWorkedPerWeek: 21,
				monthlyIncome: 1500,
				hasEUPublicHealthInsurance: true,
			}, [
				hasSelfEmployedTariff,
				getsRecommended(['public', 'expat', 'private']),
				isNotWerkstudentDueToHoursWorked,
				cannotJoinKSK,
				...selfEmployedStudentTests,
			]);
		});

		describe('without public health insurance', () => {
			testInsuranceOptions({
				...selfEmployedStudent,
				hoursWorkedPerWeek: 21,
				monthlyIncome: 1500,
			}, [
				getsRecommended(['expat', 'private']),
				cannotJoinKSK,
				...selfEmployedStudentTests,
			]);
		});
	});

	describe(`with a really high income (€${Math.ceil(0.75 * healthInsurance.maxNebenjobIncome + 1)}/m)`, () => {
		testInsuranceOptions({
			...selfEmployedStudent,
			hoursWorkedPerWeek: 20,
			monthlyIncome: Math.ceil(0.75 * healthInsurance.maxNebenjobIncome + 1),
		}, [
			getsRecommended(['expat', 'private', 'other']),
			canJoinKSK,
			...selfEmployedStudentTests,
		]);
	});
});

describe('An apprentice', () => {
	const apprentice = {
		occupation: 'azubi',
		monthlyIncome: 1200,
		hoursWorkedPerWeek: 40,
		age: 22,
	};

	const apprenticeTests = [
		cannotUseEHIC,
		cannotJoinKSK,
		cannotGetFreeInsuranceThroughSocialBenefits,
		cannotUseSpouseInsurance,
		cannotUseParentsInsurance,
	];

	describe(`with a €${healthInsurance.azubiFreibetrag}/m income`, () => {
		testInsuranceOptions({
			...apprentice,
			monthlyIncome: healthInsurance.azubiFreibetrag,
		}, [
			hasAzubiFreeTariff,
			getsRecommended(['public']),
			...apprenticeTests,
		]);
	});

	describe(`with a minijob income (€${taxes.maxMinijobIncome}/m)`, () => {
		testInsuranceOptions({
			...apprentice,
			monthlyIncome: taxes.maxMinijobIncome,
		}, [
			hasAzubiTariff,
			getsRecommended(['public']),
			...apprenticeTests,
		]);
	});

	describe(`with a normal income (€${apprentice.monthlyIncome}/m)`, () => {
		testInsuranceOptions(apprentice, [
			hasAzubiTariff,
			getsRecommended(['public']),
			...apprenticeTests,
		]);
	});

	describe(`with a high income (€${healthInsurance.minFreiwilligMonthlyIncome}/m)`, () => {
		testInsuranceOptions({
			...apprentice,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome
		}, [
			getsRecommended(['private', 'public']),
		]);
	});

	describe(`with a very high income (€${healthInsurance.maxMonthlyIncome * 2}/m)`, () => {
		testInsuranceOptions({
			...apprentice,
			monthlyIncome: healthInsurance.maxMonthlyIncome * 2
		}, [
			paysMaximumEmployeeAmount,
			getsRecommended(['private', 'public']),
		]);
	});
});

describe('An employee', () => {
	const employee = {
		occupation: 'employee',
		monthlyIncome: 3000,
		hoursWorkedPerWeek: 40,
		age: 22,
	}

	const employeeTests = [
		cannotUseEHIC,
		cannotJoinKSK,
		cannotGetFreeInsuranceThroughSocialBenefits,
	];

	describe(`with a minijob income (€${taxes.maxMinijobIncome}/m)`, () => {
		const minijobEmployee = {
			...employee,
			monthlyIncome: taxes.maxMinijobIncome,
		};

		const minijobTests = [
			canUseSpouseInsurance,
			canUseParentsInsurance,
			doesNotEarnEnoughForPrivate,
			...employeeTests,
		];

		describe('with existing German public health insurance', () => {
			testInsuranceOptions({
				...minijobEmployee,
				hasGermanPublicHealthInsurance: true,
			}, [
				hasMinijobTariff,
				getsRecommended(['public', 'other']),
				...minijobTests,
			]);
		});

		describe('with existing EU public health insurance', () => {
			testInsuranceOptions({
				...minijobEmployee,
				hasEUPublicHealthInsurance: true,
			}, [
				hasMinijobTariff,
				getsRecommended(['public', 'expat', 'other']),
				...minijobTests,
			]);
		});

		describe('without public health insurance', () => {
			testInsuranceOptions(minijobEmployee, [
				getsRecommended(['expat', 'other']),
				...minijobTests,
			]);
		});
	});

	describe(`with a midijob income (€${healthInsurance.maxMidijobIncome}/m)`, () => {
		testInsuranceOptions({
			...employee,
			monthlyIncome: healthInsurance.maxMidijobIncome,
		}, [
			hasMidijobTariff,
			getsRecommended(['public']),
			cannotUseSpouseInsurance,
			cannotUseParentsInsurance,
			...employeeTests,
		]);
	});

	describe(`with a normal income (€${healthInsurance.minFreiwilligMonthlyIncome / 2}/m)`, () => {
		testInsuranceOptions({
			...employee,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome / 2,
		}, [
			hasEmployeeTarif,
			getsRecommended(['public']),
			cannotUseSpouseInsurance,
			cannotUseParentsInsurance,
			...employeeTests,
		]);
	});

	describe(`with a high income (€${healthInsurance.minFreiwilligMonthlyIncome}/m)`, () => {
		testInsuranceOptions({
			...employee,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome,
		}, [
			hasEmployeeTarif,
			paysMaximumEmployeeAmount,
			getsRecommended(['private', 'public']),
			cannotUseSpouseInsurance,
			cannotUseParentsInsurance,
			...employeeTests,
		]);
	});

	describe(`with a really high income (€${healthInsurance.minFreiwilligMonthlyIncome * 2}/m)`, () => {
		testInsuranceOptions({
			...employee,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome * 2,
		}, [
			hasEmployeeTarif,
			paysMaximumEmployeeAmount,
			getsRecommended(['private', 'public']),
			cannotUseSpouseInsurance,
			cannotUseParentsInsurance,
			...employeeTests,
		]);
	});

	describe('applying for a visa', () => {
		testInsuranceOptions({
			...employee,
			isApplyingForFirstVisa: true,
		}, [
			hasEmployeeTarif,
			mustHaveExpatInsurance,
			getsRecommended(['public']),
		]);
	});

	describe('after 23 years old', () => {
		testInsuranceOptions({
			...employee,
			age: 23,
		}, [
			hasEmployeeTarif,
			cannotUseParentsInsurance,
			getsRecommended(['public']),
		]);
	});
});

describe('A freelancer', () => {
	const freelancer = {
		occupation: 'selfEmployed',
		monthlyIncome: 3000,
		hoursWorkedPerWeek: 40,
		age: 22,
		hasEUPublicHealthInsurance: true,
	}

	const freelancerTests = [
		canJoinKSK,
		hasSelfEmployedTariff,
		cannotUseEHIC,
		cannotGetFreeInsuranceThroughSocialBenefits,
	];

	describe('with EU public insurance', () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome / 2,
			hasEUPublicHealthInsurance: true,
		}, [
			getsRecommended(['public', 'private', 'expat', 'other']),
		]);
	});

	describe('with German public insurance', () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome / 2,
			hasGermanPublicHealthInsurance: true,
		}, [
			getsRecommended(['public', 'private', 'other']),
		]);
	});

	describe('without insurance', () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome / 2,
			hasEUPublicHealthInsurance: false,
		}, [
			getsRecommended(['private', 'expat', 'other']),
		]);
	});

	describe(`with an income below the KSK minimum (€${healthInsurance.kskMinimumIncome}/y)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: (healthInsurance.kskMinimumIncome / 12) - 1,
		}, [
			cannotJoinKSK,
			doesNotEarnEnoughForPrivate,
			getsRecommended(['expat', 'public', 'other']),
		]);
	});

	describe(`with a negligible income (€${healthInsurance.maxFamilienversicherungIncome}/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.maxFamilienversicherungIncome,
		}, [
			paysMinimumSelfEmployedAmount,
			doesNotEarnEnoughForPrivate,
			getsRecommended(['expat', 'public', 'other']),
			canUseSpouseInsurance,
			canUseParentsInsurance,
			...freelancerTests,
		]);
	});

	describe(`with a minijob income (€${taxes.maxMinijobIncome}/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: taxes.maxMinijobIncome,
		}, [
			hasSelfEmployedTariff,
			paysMinimumSelfEmployedAmount,
			doesNotEarnEnoughForPrivate,
			getsRecommended(['expat', 'public', 'other']),
			cannotUseSpouseInsurance,
			cannotUseParentsInsurance,
			...freelancerTests,
		]);
	});

	describe(`with a low income (€1500/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: 1500,
		}, [
			doesNotEarnEnoughForPrivate,
			getsRecommended(['expat', 'public', 'other']),
			...freelancerTests,
		]);
	});

	describe(`with a normal income (€${healthInsurance.minFreiwilligMonthlyIncome / 2}/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.minFreiwilligMonthlyIncome / 2,
		}, [
			earnsEnoughForPrivate,
			getsRecommended(['public', 'private', 'expat', 'other']),
			...freelancerTests,
		]);
	});

	describe(`with a high income (€${healthInsurance.maxMonthlyIncome}/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.maxMonthlyIncome,
		}, [
			paysMaximumSelfEmployedAmount,
			earnsEnoughForPrivate,
			getsRecommended(['private', 'public', 'expat', 'other']),
			...freelancerTests,
		]);
	});

	describe(`with a very high income (€${healthInsurance.maxMonthlyIncome * 2}/m)`, () => {
		testInsuranceOptions({
			...freelancer,
			monthlyIncome: healthInsurance.maxMonthlyIncome * 2,
		}, [
			paysMaximumSelfEmployedAmount,
			earnsEnoughForPrivate,
			getsRecommended(['private', 'public', 'expat', 'other']),
			...freelancerTests,
		]);
	});
});

describe('An unemployed person', () => {
	const unemployed = {
		occupation: 'unemployed',
		monthlyIncome: 0,
		hoursWorkedPerWeek: 0,
		age: 22,
	}

	const unemployedTests = [
		canGetFreeInsuranceThroughSocialBenefits,
		canUseSpouseInsurance,
		canUseParentsInsurance,
		cannotJoinKSK,
		doesNotEarnEnoughForPrivate,
	];

	describe('with EU public insurance', () => {
		testInsuranceOptions({
			...unemployed,
			hasEUPublicHealthInsurance: true,
		}, [
			...unemployedTests,
			canUseEHIC,
			getsRecommended(['expat', 'public', 'other']),
			paysMinimumSelfPayAmount,
		]);
	});

	describe('with German public insurance', () => {
		testInsuranceOptions({
			...unemployed,
			hasGermanPublicHealthInsurance: true,
		}, [
			...unemployedTests,
			cannotUseEHIC,
			getsRecommended(['public', 'other']),
			paysMinimumSelfPayAmount,
		]);
	});

	describe('without insurance', () => {
		testInsuranceOptions(unemployed, [
			...unemployedTests,
			cannotUseEHIC,
			getsRecommended(['expat', 'other']),
		]);
	});

	describe('applying for a visa', () => {
		testInsuranceOptions({
			...unemployed,
			isApplyingForFirstVisa: true,
		}, [
			cannotGetFreeInsuranceThroughSocialBenefits,
			getsRecommended(['expat', 'other']),
		]);
	});

	describe('after 23 years old', () => {
		testInsuranceOptions({
			...unemployed,
			age: 23,
			hasEUPublicHealthInsurance: true,
		}, [
			getsRecommended(['expat', 'public', 'other']),
			paysMinimumSelfPayAmountWithSurcharge,
			cannotUseParentsInsurance,
		]);
	});

	describe('after 55 years old', () => {
		describe('with EU public insurance', () => {
			testInsuranceOptions({
				...unemployed,
				age: 55,
				hasEUPublicHealthInsurance: true,
			}, [
				canUseSpouseInsurance,
				cannotUseParentsInsurance,
				getsRecommended(['public', 'expat', 'other']),
			]);
		});

		describe('with German public insurance', () => {
			testInsuranceOptions({
				...unemployed,
				age: 55,
				hasGermanPublicHealthInsurance: true,
			}, [
				canUseSpouseInsurance,
				cannotUseParentsInsurance,
				getsRecommended(['public', 'other']),
			]);
		});

		describe('without insurance', () => {
			testInsuranceOptions({
				...unemployed,
				age: 55,
			}, [
				canUseSpouseInsurance,
				cannotUseParentsInsurance,
				getsRecommended(['expat', 'other']),
			]);
		});
	});
});

describe('A married person', () => {
	describe(`with no income`, () => {
		testInsuranceOptions({
			isMarried: true,
			occupation: 'unemployed',
			hoursWorkedPerWeek: 0,
			monthlyIncome: 0,
		}, [
			canUseSpouseInsurance,
		]);
	});

	describe(`with a negligible income (€${healthInsurance.maxFamilienversicherungIncome}/m)`, () => {
		testInsuranceOptions({
			isMarried: true,
			occupation: 'unemployed',
			hoursWorkedPerWeek: 10,
			monthlyIncome: healthInsurance.maxFamilienversicherungIncome,
		}, [
			canUseSpouseInsurance,
		]);
	});

	describe(`with a minijob income (€${taxes.maxMinijobIncome}/m)`, () => {
		testInsuranceOptions({
			isMarried: true,
			occupation: 'employee',
			hoursWorkedPerWeek: 10,
			monthlyIncome: taxes.maxMinijobIncome,
		}, [
			canUseSpouseInsurance,
		]);
	});

	describe(`with a higher income (€${taxes.maxMinijobIncome + 1}/m)`, () => {
		testInsuranceOptions({
			isMarried: true,
			occupation: 'employee',
			hoursWorkedPerWeek: 10,
			monthlyIncome: taxes.maxMinijobIncome + 1,
		}, [
			cannotUseSpouseInsurance,
		]);
	});
});

describe('An unmarried person', () => {
	testInsuranceOptions({
		isMarried: false,
		occupation: 'unemployed',
		hoursWorkedPerWeek: 0,
		monthlyIncome: 0,
	}, [
		cannotUseSpouseInsurance,
	]);
});

describe('Pflegeversicherung', () => {
	const person = {
		occupation: 'employee',
		monthlyIncome: 2000,
		hoursWorkedPerWeek: 40,
	};

	describe('for a 22 year old person', () => {
		describe('with no children', () => {
			testInsuranceOptions({
				...person,
				age: 22,
				childrenCount: 0,
			}, [
				paysPflegeversicherungDefaultRate,
			]);
		});
		describe('with 1 child', () => {
			testInsuranceOptions({
				...person,
				age: 22,
				childrenCount: 1,
			}, [
				paysPflegeversicherungDefaultRate,
			]);
		});
		describe('with 2 children', () => {
			testInsuranceOptions({
				...person,
				age: 22,
				childrenCount: 2,
			}, [
				paysPflegeversicherungDiscountRate(1),
			]);
		});
		describe('with 5 children', () => {
			testInsuranceOptions({
				...person,
				age: 22,
				childrenCount: 5,
			}, [
				paysPflegeversicherungDiscountRate(4),
			]);
		});
		describe('with 10 children', () => {
			testInsuranceOptions({
				...person,
				age: 22,
				childrenCount: 10,
			}, [
				paysPflegeversicherungDiscountRate(4),
			]);
		});
	});

	describe('for a 23 year old person', () => {
		describe('with no children', () => {
			testInsuranceOptions({
				...person,
				age: 23,
				childrenCount: 0,
			}, [
				paysPflegeversicherungSurchargeRate,
			]);
		});
		describe('with 1 child', () => {
			testInsuranceOptions({
				...person,
				age: 23,
				childrenCount: 1,
			}, [
				paysPflegeversicherungDefaultRate,
			]);
		});
		describe('with 2 children', () => {
			testInsuranceOptions({
				...person,
				age: 23,
				childrenCount: 2,
			}, [
				paysPflegeversicherungDiscountRate(1),
			]);
		});
		describe('with 5 children', () => {
			testInsuranceOptions({
				...person,
				age: 23,
				childrenCount: 5,
			}, [
				paysPflegeversicherungDiscountRate(4),
			]);
		});
		describe('with 10 children', () => {
			testInsuranceOptions({
				...person,
				age: 23,
				childrenCount: 10,
			}, [
				paysPflegeversicherungDiscountRate(4),
			]);
		});
	});
});


function testInsuranceOptions(params, tests){
	const output = getHealthInsuranceOptions({
		age: 40,
		childrenCount: 0,
		hasEUPublicHealthInsurance: false,
		hasGermanPublicHealthInsurance: false,
		hoursWorkedPerWeek: 0,
		isApplyingForFirstVisa: false,
		isMarried: true,
		monthlyIncome: 0,
		occupation: 'unemployed',
		customZusatzbeitrag: undefined,
		sortByPrice: false,
		...params,
	});
	tests.forEach(t => t(output));
}

function getsRecommended(allowedOptions){
	return function(output){
		const options = output.asList.filter(o => o.eligible).map(o => o.id);
		it(`is recommended ${allowedOptions.join(', ')} (in this order)`, () => {
			assert.deepEqual(options, allowedOptions);
		});
	}
}
function mustHaveExpatInsurance(output) {
	it('needs expat insurance', () => {
		hasFlag(output, 'gap-insurance')();
	});
}

function hasAzubiTariff(output){
	it('pays the Azubi tarif', () => {
		hasFlag(output, 'public-tariff-azubi')();
		notHasFlag(output, 'public-tariff-azubiFree')();
		notHasFlag(output, 'public-minijob')();
	});
}
function hasAzubiFreeTariff(output){
	it('gets free insurance due to their low income', () => {
		hasFlag(output, 'public-tariff-azubiFree')();
		notHasFlag(output, 'public-tariff-azubi')();
		notHasFlag(output, 'public-minijob')();
		equal(output.public.options[0].total.personalContribution, 0);
	});
}

function hasEmployeeTarif(output){
	it('pays the employee tarif', hasFlag(output, 'public-tariff-employee'));
}
function paysMaximumEmployeeAmount(output) {
	const o = output.public.options[0];

	it('pays the maximum price for employees', () => {
		hasFlag(output, 'public-max-contribution')();

		assert.deepEqual(o.baseContribution, {
			totalRate: healthInsurance.defaultRate,
			totalContribution: round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultRate),
			employerRate: healthInsurance.defaultRate / 2,
			employerContribution: round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultRate / 2),
			personalRate: healthInsurance.defaultRate / 2,
			personalContribution: round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultRate / 2),
		});

		assert.deepEqual(o.zusatzbeitrag, {
			totalRate: defaultInsurer.zusatzbeitrag,
			totalContribution: round(healthInsurance.maxMonthlyIncome * defaultInsurer.zusatzbeitrag),
			employerRate: defaultInsurer.zusatzbeitrag / 2,
			employerContribution: round(healthInsurance.maxMonthlyIncome * defaultInsurer.zusatzbeitrag / 2),
			personalRate: defaultInsurer.zusatzbeitrag / 2,
			personalContribution: round(healthInsurance.maxMonthlyIncome * defaultInsurer.zusatzbeitrag / 2),
		});

		assert.deepEqual(o.pflegeversicherung, {
			totalRate: pflegeversicherung.defaultRate,
			totalContribution: round(healthInsurance.maxMonthlyIncome * pflegeversicherung.defaultRate),
			employerRate: pflegeversicherung.employerRate,
			employerContribution: round(healthInsurance.maxMonthlyIncome * pflegeversicherung.employerRate),
			personalRate: pflegeversicherung.defaultRate - pflegeversicherung.employerRate,
			personalContribution: round(healthInsurance.maxMonthlyIncome * o.pflegeversicherung.personalRate),
		});

		equal(
			o.total.employerContribution,
			round(
				round(healthInsurance.maxMonthlyIncome * healthInsurance.defaultRate / 2)
				+ round(healthInsurance.maxMonthlyIncome * defaultInsurer.zusatzbeitrag / 2)
				+ round(healthInsurance.maxMonthlyIncome * pflegeversicherung.employerRate)
			)
		);
	});
}

function hasMinijobTariff(output, paysPflegeversicherungSurchargeRate){
	const o = output.public.options[0];

	it('pays the minimum self-pay amount (minijob)', () => {
		hasFlag(output, 'public-minijob')();
		hasFlag(output, 'public-tariff-selfPay')();
		hasFlag(output, 'public-min-contribution')();

		equal(o.baseContribution.totalContribution, round(healthInsurance.minMonthlyIncome * healthInsurance.selfPayRate));
		equal(o.zusatzbeitrag.totalContribution, round(healthInsurance.minMonthlyIncome * defaultInsurer.zusatzbeitrag));
		if(paysPflegeversicherungSurchargeRate){
			equal(o.pflegeversicherung.totalContribution, round(pflegeversicherung.surchargeRate * healthInsurance.minMonthlyIncome));
		}
		else{
			equal(o.pflegeversicherung.totalContribution, round(pflegeversicherung.defaultRate * healthInsurance.minMonthlyIncome));
		}
		equal(o.total.employerContribution, 0);
	});
}
function hasMinijobTariffWithPflegeversicherungSurcharge(output){
	return hasMinijobTariff(output, true);
}

function hasMidijobTariff(output, paysPflegeversicherungSurchargeRate){
	it('pays the midijob tariff', () => {
		hasFlag(output, 'public-tariff-midijob')();

		// TODO: Test calculation properly
	});
}

function hasSelfEmployedTariff(output){
	it('pays the self-employed tariff', () => {
		hasFlag(output, 'public-tariff-selfEmployed')();
		notHasFlag(output, 'public-minijob')();
	});
}
function paysMinimumSelfEmployedAmount(output, paysPflegeversicherungSurchargeRate) {
	const o = output.public.options[0];

	it('pays the minimum price for self-employed people', () => {
		hasFlag(output, 'public-tariff-selfEmployed')();
		hasFlag(output, 'public-min-contribution')();

		equal(o.baseContribution.totalContribution, round(healthInsurance.minMonthlyIncome * healthInsurance.selfPayRate));
		equal(o.zusatzbeitrag.totalContribution, round(healthInsurance.minMonthlyIncome * defaultInsurer.zusatzbeitrag));
		if(paysPflegeversicherungSurchargeRate){
			equal(o.pflegeversicherung.totalContribution, round(healthInsurance.minMonthlyIncome * pflegeversicherung.surchargeRate));
		}
		else{
			equal(o.pflegeversicherung.totalContribution, round(healthInsurance.minMonthlyIncome * pflegeversicherung.defaultRate));
		}
		equal(o.total.employerContribution, 0);
	});
}
function paysMaximumSelfEmployedAmount(output) {
	const o = output.public.options[0];

	it('pays the maximum price for self-employed people', () => {
		hasFlag(output, 'public-tariff-selfEmployed')();
		hasFlag(output, 'public-max-contribution')();

		equal(o.baseContribution.totalContribution, round(healthInsurance.maxMonthlyIncome * healthInsurance.selfPayRate));
		equal(o.zusatzbeitrag.totalContribution, round(healthInsurance.maxMonthlyIncome * defaultInsurer.zusatzbeitrag));
		equal(o.pflegeversicherung.totalContribution, round(healthInsurance.maxMonthlyIncome * pflegeversicherung.defaultRate));
		equal(o.total.employerContribution, 0);
	});
}

function paysMinimumSelfPayAmount(output, paysPflegeversicherungSurchargeRate){
	const o = output.public.options[0];

	it('pays the minimum self-pay price', () => {
		hasFlag(output, 'public-tariff-selfPay')();
		hasFlag(output, 'public-min-contribution')();

		equal(o.baseContribution.totalContribution, round(healthInsurance.minMonthlyIncome * healthInsurance.selfPayRate));
		equal(o.zusatzbeitrag.totalContribution, round(healthInsurance.minMonthlyIncome * defaultInsurer.zusatzbeitrag));

		if(paysPflegeversicherungSurchargeRate){
			equal(o.pflegeversicherung.totalContribution, round(healthInsurance.minMonthlyIncome * pflegeversicherung.surchargeRate));
		}
		else{
			equal(o.pflegeversicherung.totalContribution, round(healthInsurance.minMonthlyIncome * pflegeversicherung.defaultRate));
		}
		equal(o.total.employerContribution, 0);
	});
}
function paysMinimumSelfPayAmountWithSurcharge(output){
	return paysMinimumSelfPayAmount(output, true);
}

function hasStudentTariff(output) {
	const o = output.public.options[0];

	it('pays the student tariff', () => {
		hasFlag(output, 'public-tariff-student')();
		notHasFlag(output, 'public-student-over-30')();
		notHasFlag(output, 'public-not-werkstudent')();
		notHasFlag(output, 'public-minijob')();

		assert.deepEqual(o.baseContribution, {
			totalRate: healthInsurance.studentRate,
			totalContribution: round(bafog.bedarfssatz * healthInsurance.studentRate),
			employerRate: 0,
			employerContribution: 0,
			personalRate: healthInsurance.studentRate,
			personalContribution: round(bafog.bedarfssatz * healthInsurance.studentRate),
		});

		assert.deepEqual(o.zusatzbeitrag, {
			totalRate: defaultInsurer.zusatzbeitrag,
			totalContribution: round(bafog.bedarfssatz * defaultInsurer.zusatzbeitrag),
			employerRate: 0,
			employerContribution: 0,
			personalRate: defaultInsurer.zusatzbeitrag,
			personalContribution: round(bafog.bedarfssatz * defaultInsurer.zusatzbeitrag),
		});

		const pflegeversicherungRate = pflegeversicherung.defaultRate;

		assert.deepEqual(o.pflegeversicherung, {
			totalRate: pflegeversicherungRate,
			totalContribution: round(bafog.bedarfssatz * pflegeversicherungRate),
			employerRate: 0,
			employerContribution: 0,
			personalRate: pflegeversicherungRate,
			personalContribution: round(bafog.bedarfssatz * pflegeversicherungRate),
		});
	});
}
function isTooOldForStudentTariff(output){
	it('is too old to get the student tariff', hasFlag(output, 'public-student-over-30'));
}
function isNotWerkstudentDueToIncome(output, paysPflegeversicherungSurchargeRate) {
	const o = output.public.options[0];

	it('is not a Werkstudent because their income is too high', () => {
		hasFlag(output, 'public-not-werkstudent')();
		notHasFlag(output, 'public-tariff-student')();

		const income = Math.ceil(0.75 * healthInsurance.maxNebenjobIncome + 1);
		equal(o.baseContribution.totalContribution, round(income * healthInsurance.defaultRate));
		equal(o.zusatzbeitrag.totalContribution, round(income * defaultInsurer.zusatzbeitrag));
		if(paysPflegeversicherungSurchargeRate){
			equal(o.pflegeversicherung.totalContribution, round(income * pflegeversicherung.surchargeRate));
		}
		else{
			equal(o.pflegeversicherung.totalContribution, round(income * pflegeversicherung.defaultRate));
		}

	});
}
function isNotWerkstudentDueToHoursWorked(output, paysPflegeversicherungSurchargeRate) {
	it('is not a Werkstudent because they work over 20 hours per week', () => {
		hasFlag(output, 'public-not-werkstudent')();
		notHasFlag(output, 'public-tariff-student')();
		notHasFlag(output, 'public-tariff-employee')();
	});
}

function paysPflegeversicherungSurchargeRate(output){
	it('pays a Pflegeversicherung surcharge', () => {
		hasFlag(output, 'public-pflegeversicherung-surcharge')();
		equal(output.public.options[0].pflegeversicherung.totalRate, pflegeversicherung.surchargeRate);
	});
}
function paysPflegeversicherungDefaultRate(output){
	it('pays the default Pflegeversicherung rate', () => {
		notHasFlag(output, 'public-pflegeversicherung-surcharge')();
		equal(output.public.options[0].pflegeversicherung.totalRate, pflegeversicherung.defaultRate);
	});
}
function paysPflegeversicherungDiscountRate(discountTimes){
	return function(output){
		it(`pays the default Pflegeversicherung rate with a ${discountTimes} x ${pflegeversicherung.discountPerChild * 100}% discount`, () => {
			notHasFlag(output, 'public-pflegeversicherung-surcharge')();
			equal(
				output.public.options[0].pflegeversicherung.totalRate,
				pflegeversicherung.defaultRate - (pflegeversicherung.discountPerChild * discountTimes)
			);
		});
	}
}


function canUseSpouseInsurance(output){
	it('can use their spouse\'s insurance', hasFlag(output, 'familienversicherung-spouse'));
}
function cannotUseSpouseInsurance(output){
	it('cannot use their spouse\'s insurance', notHasFlag(output, 'familienversicherung-spouse'));
}

function canUseParentsInsurance(output){
	it('can use their parents\' insurance', hasFlag(output, 'familienversicherung-parents'));
}
function cannotUseParentsInsurance(output){
	it('cannot use their parents\' insurance', notHasFlag(output, 'familienversicherung-parents'));
}

function canJoinKSK(output){
	it('can join the Künstlersozialkasse', () => {
		hasFlag(output, 'ksk')();
		equal(output.other.options.find(o => o.id === 'ksk').id, 'ksk');
	});
}
function cannotJoinKSK(output){
	it('cannot join the Künstlersozialkasse', () => {
		notHasFlag(output, 'ksk')();
		equal(output.other.options.find(o => o.id === 'ksk'), undefined);
	});
}

function canGetFreeInsuranceThroughSocialBenefits(output){
	it('can get free health insurance through social benefits', () => {
		hasFlag(output, 'social-benefits')();
		equal(output.other.options.find(o => o.id === 'social-benefits').id, 'social-benefits');
	});
}
function cannotGetFreeInsuranceThroughSocialBenefits(output){
	it('cannot get free health insurance through social benefits', () => {
		notHasFlag(output, 'social-benefits')();
		equal(output.other.options.find(o => o.id === 'social-benefits'), undefined);
	});
}

function canUseEHIC(output){
	it('can use their EHIC card', hasFlag(output, 'ehic'));
}

function cannotUseEHIC(output){
	it('cannot use their EHIC card', notHasFlag(output, 'ehic'));
}

function earnsEnoughForPrivate(output){
	it('earns enough for private health insurance', notHasFlag(output, 'private-income-too-low'));
}

function doesNotEarnEnoughForPrivate(output){
	it('might not earn enough for private health insurance', hasFlag(output, 'private-income-too-low'));
}
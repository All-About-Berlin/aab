{% include '_js/constants.js' %}
{% js %}

function getBoundedMonthlyIncome(monthlyIncome){
	// The income limited by the min and max health insurance contributions
	return Math.min(healthInsurance.maxMonthlyIncome, Math.max(monthlyIncome, healthInsurance.minMonthlyIncome));
}

function getInsurerOptions(customZusatzbeitrag){
	const allInsurers = Object.entries(healthInsurance.companies);
	if(customZusatzbeitrag !== undefined) {
		// Add an extra option with the user-specified Zusatzbeitrag
		allInsurers.push([
			'custom',
			{
				name: 'Other health insurer',
				zusatzbeitrag: customZusatzbeitrag,
			}
		]);
	}
	return allInsurers;
}

function calculatePflegeversicherungRate(age, childrenCount){
	if (age > pflegeversicherung.defaultTarifMaxAge && childrenCount === 0) {
		return pflegeversicherung.surchargeTarif;
	}
	else if(childrenCount < pflegeversicherung.minimumChildCountForDiscount){
		return pflegeversicherung.defaultTarif;
	}
	else{
		return pflegeversicherung.defaultTarif - (
			pflegeversicherung.discountPerChild
			* (
				Math.min(childrenCount, pflegeversicherung.maximumChildCountForDiscount)
				- pflegeversicherung.minimumChildCountForDiscount
				+ 1
			)
		);
	}
}

function calculateHealthInsuranceForAzubi(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(),
		tarif: 'azubi',
	};

	if(monthlyIncome <= healthInsurance.azubiFreibetrag) {
		out.flags.add('azubi-free');
	}

	const adjustedIncome = Math.min(healthInsurance.maxMonthlyIncome, monthlyIncome);

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};
	out.baseContribution.totalRate = healthInsurance.defaultTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * adjustedIncome);

	if(adjustedIncome <= healthInsurance.azubiFreibetrag) { // Below this, the employer pays everything
		out.baseContribution.employerRate = out.baseContribution.totalRate;
		out.baseContribution.employerContribution = out.baseContribution.totalContribution;
		out.baseContribution.personalRate = 0;
		out.baseContribution.personalContribution = 0;
	}
	else {
		out.baseContribution.employerRate = out.baseContribution.totalRate / 2;
		out.baseContribution.employerContribution = roundCurrency(adjustedIncome * out.baseContribution.employerRate);
		out.baseContribution.personalRate = out.baseContribution.totalRate - out.baseContribution.employerRate;
		out.baseContribution.personalContribution = roundCurrency(out.baseContribution.totalContribution - out.baseContribution.employerContribution);
	}


	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.totalRate);

	// Personal + employer contributions
	if(adjustedIncome <= healthInsurance.azubiFreibetrag) { // Below this, the employer pays everything
		out.pflegeversicherung.employerRate = out.pflegeversicherung.totalRate;
		out.pflegeversicherung.employerContribution = out.pflegeversicherung.totalContribution;
		out.pflegeversicherung.personalRate = 0;
		out.pflegeversicherung.personalContribution = 0;
	}
	else{
		out.pflegeversicherung.employerRate = pflegeversicherung.employerTarif;
		out.pflegeversicherung.employerContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.employerRate);
		out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate - out.pflegeversicherung.employerRate;
		out.pflegeversicherung.personalContribution = roundCurrency(out.pflegeversicherung.totalContribution - out.pflegeversicherung.employerContribution);
	}


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};

		options[krankenkasseKey].zusatzbeitrag.totalRate = krankenkasse.zusatzbeitrag;
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(adjustedIncome * options[krankenkasseKey].zusatzbeitrag.totalRate);

		if(monthlyIncome <= healthInsurance.azubiFreibetrag) {  // Below this amount, the employer pays everything
			options[krankenkasseKey].zusatzbeitrag.employerRate = options[krankenkasseKey].zusatzbeitrag.totalRate;
			options[krankenkasseKey].zusatzbeitrag.employerContribution = options[krankenkasseKey].zusatzbeitrag.totalContribution;
		}
		else {
			options[krankenkasseKey].zusatzbeitrag.employerRate = options[krankenkasseKey].zusatzbeitrag.totalRate / 2;
			options[krankenkasseKey].zusatzbeitrag.employerContribution = roundCurrency(adjustedIncome * options[krankenkasseKey].zusatzbeitrag.employerRate);
		}

		options[krankenkasseKey].zusatzbeitrag.personalRate = options[krankenkasseKey].zusatzbeitrag.totalRate - options[krankenkasseKey].zusatzbeitrag.employerRate;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = options[krankenkasseKey].zusatzbeitrag.totalContribution - options[krankenkasseKey].zusatzbeitrag.employerContribution;

		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceForEmployee(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(),
		tarif: 'employee',
	};

	if(monthlyIncome > healthInsurance.minFreiwilligMonthlyIncome){
		out.flags.add('private');
	}

	const adjustedIncome = getBoundedMonthlyIncome(monthlyIncome);

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};
	out.baseContribution.totalRate = healthInsurance.defaultTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * adjustedIncome);
	out.baseContribution.employerRate = out.baseContribution.totalRate / 2;
	out.baseContribution.employerContribution = roundCurrency(adjustedIncome * out.baseContribution.employerRate);
	out.baseContribution.personalRate = out.baseContribution.totalRate - out.baseContribution.employerRate;
	out.baseContribution.personalContribution = roundCurrency(out.baseContribution.totalContribution - out.baseContribution.employerContribution);


	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.totalRate);
	out.pflegeversicherung.employerRate = pflegeversicherung.employerTarif;
	out.pflegeversicherung.employerContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.employerRate);
	out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate - out.pflegeversicherung.employerRate;
	out.pflegeversicherung.personalContribution = roundCurrency(out.pflegeversicherung.totalContribution - out.pflegeversicherung.employerContribution);


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};

		options[krankenkasseKey].zusatzbeitrag.totalRate = krankenkasse.zusatzbeitrag;
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(adjustedIncome * options[krankenkasseKey].zusatzbeitrag.totalRate);

		options[krankenkasseKey].zusatzbeitrag.employerRate = krankenkasse.zusatzbeitrag / 2;
		options[krankenkasseKey].zusatzbeitrag.employerContribution = adjustedIncome * options[krankenkasseKey].zusatzbeitrag.employerRate;
		options[krankenkasseKey].zusatzbeitrag.personalRate = options[krankenkasseKey].zusatzbeitrag.totalRate - options[krankenkasseKey].zusatzbeitrag.employerRate;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = options[krankenkasseKey].zusatzbeitrag.totalContribution - options[krankenkasseKey].zusatzbeitrag.employerContribution;

		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceForMidijob(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(['midijob']),
		tarif: 'midijob',
	};

	/***************************************************
	* Monthly income
	* According to Gleitzone formula: §20 Abs. 2a SGB VI
	***************************************************/

	const adjustedIncomeEmployer = (
		healthInsurance.factorF * taxes.maxMinijobIncome
		+ (
			(healthInsurance.midijobMaxIncome / (healthInsurance.midijobMaxIncome-taxes.maxMinijobIncome))
			- (
				(
					taxes.maxMinijobIncome
					/ (healthInsurance.midijobMaxIncome - taxes.maxMinijobIncome)
				)
				* healthInsurance.factorF
			)
		) * (monthlyIncome - taxes.maxMinijobIncome)
	);

	const adjustedIncomeEmployee = (
		(healthInsurance.midijobMaxIncome / (healthInsurance.midijobMaxIncome-taxes.maxMinijobIncome))
		* (monthlyIncome - taxes.maxMinijobIncome)
	);

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};
	out.baseContribution.totalRate = healthInsurance.defaultTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * adjustedIncomeEmployer);

	out.baseContribution.employerRate = healthInsurance.defaultTarif / 2;
	out.baseContribution.personalRate = out.baseContribution.totalRate - out.baseContribution.employerRate;
	out.baseContribution.personalContribution = roundCurrency(adjustedIncomeEmployee * out.baseContribution.personalRate);
	out.baseContribution.employerContribution = roundCurrency(out.baseContribution.totalContribution - out.baseContribution.personalContribution);


	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(adjustedIncomeEmployer * out.pflegeversicherung.totalRate);

	out.pflegeversicherung.employerRate = pflegeversicherung.employerTarif;
	out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate - out.pflegeversicherung.employerRate;
	out.pflegeversicherung.personalContribution = roundCurrency(
		(out.pflegeversicherung.totalRate - pflegeversicherung.defaultTarif) * adjustedIncomeEmployer
		+ out.pflegeversicherung.personalRate * adjustedIncomeEmployee // The childless surcharge is not covered by the employer
	);
	out.pflegeversicherung.employerContribution = roundCurrency(out.pflegeversicherung.totalContribution - out.pflegeversicherung.personalContribution);


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(krankenkasse.zusatzbeitrag * adjustedIncomeEmployer);
		options[krankenkasseKey].zusatzbeitrag.employerRate = krankenkasse.zusatzbeitrag / 2;
		options[krankenkasseKey].zusatzbeitrag.personalRate = krankenkasse.zusatzbeitrag / 2;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = roundCurrency(adjustedIncomeEmployee * options[krankenkasseKey].zusatzbeitrag.personalRate);
		options[krankenkasseKey].zusatzbeitrag.employerContribution = roundCurrency(options[krankenkasseKey].zusatzbeitrag.totalContribution - options[krankenkasseKey].zusatzbeitrag.personalContribution);


		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceForSelfEmployment(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(['private']),
		tarif: 'selfEmployed',
	};

	const adjustedIncome = getBoundedMonthlyIncome(monthlyIncome);

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};
	out.baseContribution.totalRate = healthInsurance.selfEmployedTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * adjustedIncome);
	out.baseContribution.employerRate = 0;
	out.baseContribution.employerContribution = 0;
	out.baseContribution.personalRate = out.baseContribution.totalRate;
	out.baseContribution.personalContribution = out.baseContribution.totalContribution;


	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.totalRate);
	out.pflegeversicherung.employerRate = 0;
	out.pflegeversicherung.employerContribution = 0;
	out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate;
	out.pflegeversicherung.personalContribution = out.pflegeversicherung.totalContribution;


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};

		options[krankenkasseKey].zusatzbeitrag.totalRate = krankenkasse.zusatzbeitrag;
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(adjustedIncome * options[krankenkasseKey].zusatzbeitrag.totalRate);
		options[krankenkasseKey].zusatzbeitrag.employerRate = 0;
		options[krankenkasseKey].zusatzbeitrag.employerContribution = 0;
		options[krankenkasseKey].zusatzbeitrag.personalRate = options[krankenkasseKey].zusatzbeitrag.totalRate;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = options[krankenkasseKey].zusatzbeitrag.totalContribution;

		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceForSelfPay(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(['private']),
		tarif: 'selfPay',
	};

	const adjustedIncome = getBoundedMonthlyIncome(monthlyIncome);

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};
	out.baseContribution.totalRate = healthInsurance.defaultTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * adjustedIncome);
	out.baseContribution.employerRate = 0;
	out.baseContribution.employerContribution = 0;
	out.baseContribution.personalRate = out.baseContribution.totalRate;
	out.baseContribution.personalContribution = out.baseContribution.totalContribution;

	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(adjustedIncome * out.pflegeversicherung.totalRate);
	out.pflegeversicherung.employerRate = 0;
	out.pflegeversicherung.employerContribution = 0;
	out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate;
	out.pflegeversicherung.personalContribution = out.pflegeversicherung.totalContribution;


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};

		options[krankenkasseKey].zusatzbeitrag.totalRate = krankenkasse.zusatzbeitrag;
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(adjustedIncome * options[krankenkasseKey].zusatzbeitrag.totalRate);
		options[krankenkasseKey].zusatzbeitrag.employerRate = 0;
		options[krankenkasseKey].zusatzbeitrag.employerContribution = 0;
		options[krankenkasseKey].zusatzbeitrag.personalRate = options[krankenkasseKey].zusatzbeitrag.totalRate;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = options[krankenkasseKey].zusatzbeitrag.totalContribution;

		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceForStudent(monthlyIncome, age, childrenCount, customZusatzbeitrag){
	const out = {
		flags: new Set(['student', 'private']),
		tarif: 'student',
	};

	/***************************************************
	* Base contribution
	***************************************************/

	out.baseContribution = {};

	// Students pay a fixed amount: 70% of the normal rate * the bafogBedarfssatz
	out.baseContribution.totalRate = healthInsurance.studentTarif;
	out.baseContribution.totalContribution = roundCurrency(out.baseContribution.totalRate * bafogBedarfssatz);

	// TODO: How do employers contribute to student health insurance?
	out.baseContribution.employerRate = 0;
	out.baseContribution.personalRate = undefined;
	out.baseContribution.personalContribution = out.baseContribution.totalContribution;
	out.baseContribution.employerContribution = roundCurrency(out.baseContribution.totalContribution - out.baseContribution.personalContribution);


	/***************************************************
	* Pflegeversicherung
	***************************************************/

	out.pflegeversicherung = {};

	// TODO: How does an employer contribute to a student's Pflegeversicherung?
	out.pflegeversicherung.totalRate = calculatePflegeversicherungRate(age, childrenCount);
	out.pflegeversicherung.totalContribution = roundCurrency(out.pflegeversicherung.totalRate * bafogBedarfssatz);
	out.pflegeversicherung.employerRate = 0;
	out.pflegeversicherung.employerContribution = 0;
	out.pflegeversicherung.personalRate = out.pflegeversicherung.totalRate - out.pflegeversicherung.employerRate;
	out.pflegeversicherung.personalContribution = roundCurrency(out.pflegeversicherung.totalContribution - out.pflegeversicherung.employerContribution);


	/***************************************************
	* Zusatzbeitrag
	***************************************************/

	out.options = getInsurerOptions(customZusatzbeitrag).reduce((options, [krankenkasseKey, krankenkasse]) => {
		options[krankenkasseKey] = {
			zusatzbeitrag: {}
		};

		options[krankenkasseKey].zusatzbeitrag.totalRate = krankenkasse.zusatzbeitrag;
		options[krankenkasseKey].zusatzbeitrag.totalContribution = roundCurrency(bafogBedarfssatz * options[krankenkasseKey].zusatzbeitrag.totalRate);
		options[krankenkasseKey].zusatzbeitrag.employerRate = 0;
		options[krankenkasseKey].zusatzbeitrag.employerContribution = 0;
		options[krankenkasseKey].zusatzbeitrag.personalRate = options[krankenkasseKey].zusatzbeitrag.totalRate - options[krankenkasseKey].zusatzbeitrag.employerRate;
		options[krankenkasseKey].zusatzbeitrag.personalContribution = roundCurrency(options[krankenkasseKey].zusatzbeitrag.totalContribution - options[krankenkasseKey].zusatzbeitrag.employerContribution);

		const finalTotal = field => out.baseContribution[field] + out.pflegeversicherung[field] + options[krankenkasseKey].zusatzbeitrag[field];
		options[krankenkasseKey].total = {
			totalRate: finalTotal('totalRate'),
			employerRate: finalTotal('employerRate'),
			personalRate: finalTotal('personalRate'),
			totalContribution: roundCurrency(finalTotal('totalContribution')),
			employerContribution: roundCurrency(finalTotal('employerContribution')),
			personalContribution: roundCurrency(finalTotal('personalContribution')),
		}

		return options;
	}, {});

	return out;
}

function calculateHealthInsuranceContributions({age, monthlyIncome, occupation, isMarried, childrenCount, customZusatzbeitrag}) {
	const isSelfEmployed = occupation == 'selfEmployed';
	const isWorkingStudent = occupation == 'studentEmployee';
	const isSelfEmployedStudent = occupation == 'studentSelfEmployed';
	const isStudent = isWorkingStudent || isSelfEmployedStudent || occupation == 'student';
	const isUnemployed = occupations.isUnemployed(occupation);
	const isAzubi = occupation == 'azubi';

	/***************************************************
	* Tarif selection
	***************************************************/
	let tarif = null;
	const flags = new Set();

	if(isStudent) {
		if(age >= 30) {
			flags.add('student-30plus');
			if(isWorkingStudent) {
				tarif = 'employee';
			}
			else if(isSelfEmployedStudent) {
				tarif = 'selfEmployed';
			}
			else {
				tarif = 'selfPay';
			}
		}
		else{
			tarif = 'student';
		}

		// You're earning too much to be considered a student
		// https://www.haufe.de/personal/haufe-personal-office-platin/student-versicherungsrechtliche-bewertung-einer-selbsts-5-student-oder-selbststaendiger_idesk_PI42323_HI9693887.html
		const hoursWorked = 20; // TODO: Accept different values
		if(hoursWorked <= 20 && monthlyIncome > 0.75*healthInsurance.nebenjobMaxIncome) {
			tarif = isSelfEmployedStudent ? 'selfEmployed' : 'employee';
			flags.add('not-nebenjob');
		}
		else if(hoursWorked > 20 && hoursWorked <= 30 && monthlyIncome > 0.5*healthInsurance.nebenjobMaxIncome) {
			tarif = isSelfEmployedStudent ? 'selfEmployed' : 'employee';
			flags.add('not-nebenjob');
		}
		else if(hoursWorked > 30 && monthlyIncome > 0.25*healthInsurance.nebenjobMaxIncome) {
			tarif = isSelfEmployedStudent ? 'selfEmployed' : 'employee';
			flags.add('not-nebenjob');
		}
	}
	else if(isSelfEmployed) {
		tarif = 'selfEmployed';
	}
	else if(isUnemployed) {
		tarif = 'selfPay';
	}
	else if(occupation === 'employee') {
		tarif = 'employee';
	}
	else if(isAzubi) {
		tarif = 'azubi';
	}

	if(tarif == 'employee' && !isAzubi) {
		// Azubis don't get the midijob tarif
		// https://www.haufe.de/sozialwesen/versicherungen-beitraege/auszubildende-besonderheiten-bei-den-neuen/besonderheiten-bei-der-beitragsberechnung_240_94670.html
		if(monthlyIncome <= taxes.maxMinijobIncome) {
			tarif = 'selfPay';
			flags.add('minijob');
		}
		else if(monthlyIncome <= healthInsurance.midijobMaxIncome) {
			tarif = 'midijob';
		}
	}


	/***************************************************
	* Flags
	***************************************************/

	if (isUnemployed){
		flags.add('alg-i-buergergeld');
	}

	if (monthlyIncome <= taxes.maxMinijobIncome && !isSelfEmployed && !isAzubi) {
		flags.add('ehic');
	}

	// Azubis can't use Familienversicherung - krankenkasse-vergleich-direkt.de/ratgeber/krankenversicherung-fuer-auszubildende.html
	// If the minijob income > familienversicherung income, minijobbers keep their familienversicherung. - §8 SGB V
	if(monthlyIncome <= Math.max(taxes.maxMinijobIncome, healthInsurance.maxFamilienvericherungIncome) && !isAzubi) {
		if(isMarried){
			flags.add('familienversicherung-spouse'); // No age limit
		}
		if(age < 23 || (isStudent && age < 25)) {
			flags.add('familienversicherung-parents');
		}
	}

	if (isSelfEmployed && (monthlyIncome * 12) >= healthInsurance.kskMinimumIncome) {
		flags.add('ksk');
	}

	if (monthlyIncome >= healthInsurance.maxMonthlyIncome) {
		flags.add('max-contribution');
	}

	if (monthlyIncome <= healthInsurance.minMonthlyIncome && (tarif === 'selfPay' || tarif === 'selfEmployed')) {
		flags.add('min-contribution');
	}

	if(tarif == 'employee' && !isAzubi && monthlyIncome <= taxes.maxMinijobIncome) {
		flags.add('minijob');
	}

	if (age > pflegeversicherung.defaultTarifMaxAge && childrenCount === 0) {
		flags.add('pflegeversicherung-surcharge');
	}

	if (monthlyIncome >= healthInsurance.minFreiwilligMonthlyIncome || isUnemployed || tarif === 'selfPay' || tarif === 'selfEmployed' || tarif === 'minijob' || tarif === 'student') {
		flags.add('private');
	}


	/***************************************************
	* Contributions calculation
	***************************************************/

	const calcFunction = {
		'azubi': calculateHealthInsuranceForAzubi,
		'employee': calculateHealthInsuranceForEmployee,
		'midijob': calculateHealthInsuranceForMidijob,
		'selfEmployed': calculateHealthInsuranceForSelfEmployment,
		'selfPay': calculateHealthInsuranceForSelfPay,
		'student': calculateHealthInsuranceForStudent,
	}[tarif];
	const output = calcFunction(monthlyIncome, age, childrenCount, customZusatzbeitrag);

	const insurerOptionsSortedByPrice = Object.values(output.options).sort((a, b) => a.total.personalContribution - b.total.personalContribution);
	output.options.cheapest = insurerOptionsSortedByPrice[0];
	output.options.mostExpensive = insurerOptionsSortedByPrice[insurerOptionsSortedByPrice.length - 1];

	flags.forEach(f => output.flags.add(f));

	return output;
}
{% endjs %}
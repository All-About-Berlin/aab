export const citizenshipDepartments = {
	S1: 'S1 — Syria',
	S2: 'S2 — Afghanistan, Irak, Russia',
	S3: 'S3 — Asia',
	S4: 'S4 — Africa, America, Australia, Oceania',
	S5: 'S5 — Georgia, Poland, Turkey, Ukraine',
	S6: 'S6 — Europe',
};

// Before restructuration in October 2025
export const oldResidencePermitDepartments = {
	E1: 'E1 — Middle East',
	E2: 'E2 — Africa, America, Israel',
	E3: 'E3 — India, Turkey, etc.',
	E4: 'E4 — Asia, Australia, New Zealand, Russia',
	E5: 'E5 — Balkans, Belarus, Georgia, Ukraine',
	E6: 'E6 — Europe',
}

export const residencePermitTypes = {
	BLUE_CARD: {
		capitalized: "Blue Card",
		normal: "Blue Card",
		glossaryTerm: "Blue Card",
		guideUrl: '/guides/blue-card',
	},
	FAMILY_REUNION_VISA: {
		capitalized: "Family reunion visa",
		normal: "family reunion visa",
		glossaryTerm: "Family reunion visa",
		askAboutHealthInsurance: true,
	},
	FREELANCE_VISA: {
		capitalized: "Freelance visa",
		normal: "freelance visa",
		glossaryTerm: "Freelance visa",
		askAboutHealthInsurance: true,
		guideUrl: '/guides/freelance-visa',
	},
	JOB_SEEKER_VISA: {
		capitalized: "Job seeker visa",
		normal: "job seeker visa",
		glossaryTerm: "Job seeker visa",
		askAboutHealthInsurance: true,
	},
	PERMANENT_RESIDENCE: {
		capitalized: "Permanent residence",
		normal: "permanent residence",
		glossaryTerm: "Niederlassungserlaubnis",
		askAboutHealthInsurance: true,
		guideUrl: '/guides/permanent-residence',
	},
	STUDENT_VISA: {
		capitalized: "Student visa",
		normal: "student visa",
		glossaryTerm: "Student visa",
		askAboutHealthInsurance: true,
	},
	WORK_VISA: {
		capitalized: "Work visa",
		normal: "work visa",
		glossaryTerm: "Work Visa",
		guideUrl: '/guides/work-visa',
	},
};

export function residencePermitDepartments(residencePermitType){
	return {
		BLUE_CARD: {
			B1_B2_B3_B4: 'B1, B2, B3, B4 — Online application',
			B6: 'BIS — Business Immigration Service',
		},
		FAMILY_REUNION_VISA: {
			A1_A5: 'A1, A5 — Syria',
			A2_A3_A4: 'A2, A3, A4 — Asylum seekers',
			B1_B2_B3_B4: 'B1, B2, B3, B4 — Family of skilled workers',
			B6: 'BIS — Business Immigration Service',
			F1_F2: 'F1, F2 — Privileged countries',
			M1: 'M1 — Afghanistan, Iraq, Iran',
			M2: 'M2 — Africa, Middle East',
			M3: 'M3 — Belarus, Libya, Russia, Turkey, Ukraine',
			M4: 'M4 — Americas, everyone else',
		},
		FREELANCE_VISA: {
			A1_A5: 'A1, A5 — Syria',
			A2_A3_A4: 'A2, A3, A4 — Asylum seekers',
			F1_F2: 'F1, F2 — Privileged countries',
			M1: 'M1 — Afghanistan, Iraq, Iran',
			M2: 'M2 — Africa, Middle East',
			M3: 'M3 — Belarus, Libya, Russia, Turkey, Ukraine',
			M4: 'M4 — Americas, everyone else',
		},
		PERMANENT_RESIDENCE: {
			A1_A5: 'A1, A5 — Syria',
			A2_A3_A4: 'A2, A3, A4 — Asylum seekers',
			F1_F2: 'F1, F2 — Privileged countries',
			M1: 'M1 — Afghanistan, Iraq, Iran',
			M2: 'M2 — Africa, Middle East',
			M3: 'M3 — Belarus, Libya, Russia, Turkey, Ukraine',
			M4: 'M4 — Americas, everyone else',
		},
		STUDENT_VISA: {
			B1_B2_B3_B4: 'B1, B2, B3, B4 — Students',
		},
		WORK_VISA: {
			B1_B2_B3_B4: 'B1, B2, B3, B4 — Skilled workers',
			B6: 'B6 — Business Immigration Service',
		},
	}[residencePermitType] || {
		A1_A5: 'A1, A5 — Syria',
		A2_A3_A4: 'A2, A3, A4 — Asylum seekers',
		B1_B2_B3_B4: 'B1, B2, B3, B4 — Students, workers, researchers',
		B6: 'B6 — Business Immigration Service',
		F1_F2: 'F1, F2 — Privileged countries',
		M1: 'M1 — Afghanistan, Iraq, Iran',
		M2: 'M2 — Africa, Middle East',
		M3: 'M3 — Belarus, Libya, Russia, Turkey, Ukraine',
		M4: 'M4 — Americas, everyone else',
	};
}
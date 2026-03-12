export function formatName(gender, firstName, lastName, language='en', alwaysIncludeFirstName=true){
	let displayGender = {
		man: { en: 'Mr', de: 'Herr' },
		woman: { en: 'Mrs', de: 'Frau' },
		other: { en: '', de: '' },
	}[gender][language];

	if(!lastName){ // No "Dear Mr Firstname"
		displayGender = '';
	}

	if(displayGender && lastName && !alwaysIncludeFirstName){
		return [displayGender, lastName].join(' ');
	}

	return [displayGender, firstName, lastName].filter(Boolean).join(' ');
}

export function formatSalutations(gender, firstName, lastName, language='en', comma=true){
	if(!lastName || (gender === 'other' && !firstName)) {
		return {
			en: 'Dear Sir or Madam',
			de: 'Sehr geehrte Damen und Herren'
		}[language] + (comma ? ',' : '');
	}
	return {
		'man': {
			en: `Dear Mr ${lastName}`,
			de: `Sehr geehrter Herr ${lastName}`,
		},
		'woman': {
			en: `Dear Mrs ${lastName}`,
			de: `Sehr geehrte Frau ${lastName}`,
		},
		'other': {
			en: `Dear ${firstName} ${lastName}`,
			de: `Sehr geehrte*r ${firstName} ${lastName}`,
		},
	}[gender][language] + (comma ? ',' : '');
}

export function mergeFields(fields){
	return fields.filter(Boolean).join(', ')
}
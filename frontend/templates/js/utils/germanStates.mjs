export const germanStateNames = {
	bb: {en: 'Brandenburg', de: 'Brandenburg'},
	bw: {en: 'Baden-Württemberg', de: 'Baden-Württemberg'},
	by: {en: 'Bavaria', de: 'Bayern'},
	hb: {en: 'Bremen', de: 'Bremen'},
	hh: {en: 'Hamburg', de: 'Hamburg'},
	hr: {en: 'Hesse', de: 'Hessen'},
	mv: {en: 'Mecklenburg-Western Pomerania', de: 'Mecklenburg-Vorpommern'},
	ni: {en: 'Lower Saxony', de: 'Niedersachsen'},
	nw: {en: 'North Rhine-Westphalia', de: 'Nordrhein-Westfalen'},
	rp: {en: 'Rhineland-Palatinate', de: 'Rheinland-Pfalz'},
	sh: {en: 'Schleswig-Holstein', de: 'Schleswig-Holstein'},
	sl: {en: 'Saarland', de: 'Saarland'},
	sn: {en: 'Saxony', de: 'Sachsen'},
	st: {en: 'Saxony-Anhalt', de: 'Sachsen-Anhalt'},
	th: {en: 'Thuringia', de: 'Thüringen'},

	be: {en: 'Berlin', de: 'Berlin'},
	'be-east': {en: 'Berlin (East)', de: 'Berlin (Ost)'},
	'be-west': {en: 'Berlin (West)', de: 'Berlin (West)'},
};

export function isEastGerman(state){
	return ['bb', 'be-east', 'mv', 'sn', 'st', 'th'].includes(state)
}
export function dateFromString(str) {
	if(str.match(/\d\d\d\d-\d\d-\d\d/)){
		const [year, month, day] = str.split('-').map(n => parseInt(n, 10));
		return new Date(year, month - 1, day);
	}
	return null;
}

export function formatDate(date, locale){  // "01/23/2025" or "23.01.2025"
	if(date) {
		const dateObj = (date instanceof Date) ? date : dateFromString(date);
		return dateObj.toLocaleDateString(locale, {
			year: 'numeric',
			month: 'numeric',
			day: 'numeric',
		});
	}
	return '';
}

export function formatLongDate(date, locale="en-US", includeSameYear=false){  // "January 23, 2025"
	if(date) {
		const dateObj = (date instanceof Date) ? date : dateFromString(date);
		const yearParam = {};
		if(includeSameYear || dateObj.getFullYear() !== new Date().getFullYear()){
			yearParam.year = 'numeric';
		}
		return dateObj.toLocaleDateString(locale, {
			...yearParam,
			month: 'long',
			day: 'numeric',
		});
	}
	return '';
}

export function formatTimeDelta(date1, date2){
	const millisecondsPerDay = 1000 * 60 * 60 * 24;
	const days = Math.ceil((date2.getTime() - date1.getTime()) / millisecondsPerDay);
	let qty, unit = null;
	if(days <= 7 * 2){
		qty = days
		unit = (qty === 1 ? 'day' : 'days');
	}
	else if(days <= 7 * 8){
		qty = Math.round(days / 7);
		unit = (qty === 1 ? 'week' : 'weeks');
	}
	else{
		qty = Math.round(days / 30)
		unit = (qty === 1 ? 'month' : 'months');
	}

	return `${qty} ${unit}`;
}

export function isoDay(date){
	const yyyy = date.getFullYear();
	const mm = String(date.getMonth() + 1).padStart(2, '0');
	const dd = String(date.getDate()).padStart(2, '0');

	return `${yyyy}-${mm}-${dd}`;
}

export function isoMonth(date){
	return isoDay(date).slice(0, 7);
}
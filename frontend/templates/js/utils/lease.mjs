import { publicHolidaysByDate } from '/js/utils/publicHolidays.mjs';
import { dateFromString } from '/js/utils/date.mjs';

export function isPublicHoliday(date) {
	return publicHolidaysByDate.map(dateFromString).some(holiday =>
		holiday.getFullYear() === date.getFullYear() &&
		holiday.getMonth() === date.getMonth() &&
		holiday.getDate() === date.getDate()
	);
}

export function getNthWorkingDay(year, zeroBasedMonth, n){
	const date = new Date(year, zeroBasedMonth, 1);
	let workingDaysFound = 0;
	while(workingDaysFound < n){
		date.setDate(date.getDate() + 1);

		// Working days (Werktage) include Saturdays in this context
		if(date.getDay() !== 0 && !isPublicHoliday(date)){
			workingDaysFound++;
		}
	}
	return date;
}

export function getMoveOutDate(noticeDate) {
	// Termination notice is due on 3rd working day, so it must arrive before the 4th working day
	const fourthWorkingDay = getNthWorkingDay(noticeDate.getFullYear(), noticeDate.getMonth(), 4);
	const monthsToAdd = noticeDate <= fourthWorkingDay ? 3 : 4;
	const moveOutDate = new Date(noticeDate); // Leave original object untouched
	moveOutDate.setHours(0, 0, 0, 0);  // Start of the day
	moveOutDate.setMonth(moveOutDate.getMonth() + monthsToAdd);
	moveOutDate.setDate(0); // Last day of previous month. Jan 0 -> Dec 31
	return moveOutDate;
}

export function getLatestNoticeDate(moveOutDate) {
	const noticeDate = new Date(moveOutDate);
	noticeDate.setHours(0, 0, 0, 0);  // Start of the day
	noticeDate.setDate(1); // First day of the month.
	noticeDate.setMonth(noticeDate.getMonth() - 2); // Go back 2 months, not 3

	// Termination notice is due on 3rd working day
	return getNthWorkingDay(noticeDate.getFullYear(), noticeDate.getMonth(), 3);
}
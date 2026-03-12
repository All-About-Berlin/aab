import Collapsible from '/js/vue/components/collapsible.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import { dateFromString, formatLongDate, isoDay } from '/js/utils/date.mjs';
import { getMoveOutDate, getLatestNoticeDate } from '/js/utils/lease.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';

export default {
	components: {
		Collapsible,
		DatePicker,
		Glossary,
	},
	mixins: [uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			inputNoticeDate: '',  // YYYY-MM-DD string
		};
	},
	mounted(){
		this.inputNoticeDate = isoDay(new Date())
	},
	computed: {
		inputMoveOutDate: {
			get(){
				const noticeDate = dateFromString(this.inputNoticeDate);
				return noticeDate ? isoDay(getMoveOutDate(noticeDate)) : '';
			},
			set(dateString){
				const moveOutDate = dateFromString(dateString);
				this.inputNoticeDate = moveOutDate ? isoDay(getLatestNoticeDate(moveOutDate)) : '';
			}
		},
		isNoticePeriodDelayed(){
			return getLatestNoticeDate(getMoveOutDate(dateFromString(this.inputNoticeDate))) > dateFromString(this.inputNoticeDate);
		},
		noticeDateMonth(){
			return dateFromString(this.inputNoticeDate).toLocaleString('en-US', { month: 'long' });
		},
		noticePeriodStart(){
			const latestNoticeDate = getLatestNoticeDate(dateFromString(this.inputMoveOutDate));
			latestNoticeDate.setDate(1);
			return latestNoticeDate.toLocaleString('en-US', { day: 'numeric', month: 'long' });
		},
		noticePeriodEnd(){
			return formatLongDate(dateFromString(this.inputMoveOutDate));
		},
	},
	template: `
		<collapsible
			aria-label="Lease notice period calculator"
			aria-description="Calculate the notice period of your apartment lease"
			class="lease-notice-period-calculator"
			:static="static">

			<template v-slot:header>Lease notice period calculator</template>
			<div class="form-group show-errors">
				<label :for="uid('noticeDate')">Notice date</label>
				<date-picker v-model="inputNoticeDate" :id="uid('noticeDate')"></date-picker>
				<span class="input-instructions">When your landlord receives your <glossary term="Kündigungsschreiben">termination letter</glossary>.</span>
			</div>
			<div class="form-group show-errors">
				<label :for="uid('moveOutDate')">Move-out date</label>
				<date-picker v-model="inputMoveOutDate" :id="uid('moveOutDate')"></date-picker>
				<span class="input-instructions">When your <glossary term="Kündigungsfrist">notice period</glossary> ends, on the last day of the month.</span>
			</div>
			<template v-if="inputMoveOutDate && inputNoticeDate">
				<hr>
				Your notice date is {{ isNoticePeriodDelayed ? 'after the 3rd' : 'before the 4th' }} <glossary term="Werktag">working day</glossary> of {{ noticeDateMonth }}, so your <glossary term="Kündigungsfrist">notice period</glossary> starts on {{ noticePeriodStart }}. Your lease can end 3 months later, on {{ noticePeriodEnd }}.
			</template>
		</collapsible>
	`,
}
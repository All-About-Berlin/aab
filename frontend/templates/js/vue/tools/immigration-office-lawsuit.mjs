import CityInput from '/js/vue/components/city-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { dateFromString, isoDay, formatTimeDelta } from '/js/utils/date.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';

import metadata from '/js/vue/tools/immigration-office-lawsuit.metadata.json' with { type: 'json' };

export default {
	components: {
		CityInput,
		Collapsible,
		DatePicker,
		EmailInput,
		FullNameInput,
		Checkbox,
	},
	mixins: [multiStageMixin, uniqueIdsMixin, trackedStagesMixin],
	props: {
		static: Boolean,
	},
	data() {
		return {
			metadata,
			trackAs: 'Untätigkeitsklage',
			isLoading: false,
			stages: ['intro', 'questions', 'contact', 'thank-you', 'error'],
			applicationType: null,
			city: '',
			applicationDate: null,
			applicationDateError: '',
			immigrationOfficeHasReplied: false,
			meetsRequirements: false,
			hasSubmittedDocuments: false,
			fullName: '',
			email: '',
			message: '',
			recipientEmail: 'contact@legalweg.com',
		};
	},
	computed: {
		monthsAgo(){
			if(!this.applicationDate) return;

			const applicationDate = dateFromString(this.applicationDate);
			const today = new Date();

			let months = (
				(today.getFullYear() - applicationDate.getFullYear()) * 12
				+ (today.getMonth() - applicationDate.getMonth())
			);

			if (today.getDate() < applicationDate.getDate()){
				months--;
			}

			return months;
		},
		minWaitMonths() {
			if (this.applicationType === 'CITIZENSHIP') return 12;
			if (this.applicationType === 'PERMANENT_RESIDENCE') return 9;
			return 6;
		},
		isTooEarlyToSue() {
			if (!this.applicationDate || !this.applicationType) return false;
			return this.monthsAgo < this.minWaitMonths;
		},
	},
	watch: {
		applicationDate(newVal) {
			if(!this.applicationDate){
				this.applicationDateError = "";
			}

			this.applicationDateError = this.monthsAgo < 3 ? "Wait at least 3 months before suing the immigration office." : "";
			this.$refs.applicationDateInput.$el.setCustomValidity(this.applicationDateError);
		},
	},
	methods: {
		async submitForm(event) {
			if (validateForm(this.$el)) {
				this.isLoading = true;
				const response = await fetch(
					'/api/forms/immigration-office-lawsuit',
					{
						method: 'POST',
						keepalive: true,
						headers: { 'Content-Type': 'application/json; charset=utf-8' },
						body: JSON.stringify({
							name: this.fullName,
							email: this.email,
							application_type: this.applicationType,
							city: this.city,
							application_date: this.applicationDate,
							immigration_office_has_replied: this.immigrationOfficeHasReplied,
							meets_requirements: this.meetsRequirements,
							has_submitted_documents: this.hasSubmittedDocuments,
							message: this.message,
							referrer: getReferrer() || '',
						}),
					},
				);
				this.isLoading = false;
				if (response.ok) {
					this.goToStage('thank-you');
				} else {
					this.goToStage('error');
				}
			} else {
				event.preventDefault();
			}
		},
	},
	template: `
		<collapsible
			class="immigration-office-lawsuit"
			:aria-label="metadata.label"
			:aria-description="metadata.description"
			:static="static">
			<template v-slot:header>
				Sue the immigration office
			</template>

			<progress v-if="stage !== 'intro' && stage !== 'thank-you' && stage !== 'error'" aria-label="Form progress" :max="stages.length - 1" :value="stageIndex"></progress>

			<template v-if="stage === 'intro'">
				<div class="form-recipient">
					<div>
						<h2 v-if="static">Sue the immigration office</h2>
						<p>Artjom Spirin is an immigration lawyer. He will assess if a lawsuit makes sense. He usually replies on the same day.</p>
						<p>This assessment is <strong>100% free</strong>. You only pay if you choose to sue. If you win, the immigration office usually refunds your legal costs.</p>
					</div>
					<img
						srcset="/experts/photos/bioLarge1x/artjom-spirin.jpg, /experts/photos/bioLarge2x/artjom-spirin.jpg 2x"
						alt="Artjom Spirin" width="125" height="125"
						sizes="125px">
				</div>
				<hr>
				<div class="buttons bar">
					<button class="button primary next" @click="nextStage">
						Continue
					</button>
				</div>
			</template>

			<template v-if="stage === 'questions'">
				<h2>Tell us about your situation&hellip;</h2>
				<p>This helps Artjom decide if you should sue the immigration office.</p>
				<hr>
				<div class="form-group" :class="{'show-errors': !!applicationDateError}">
					<label :for="uid('applicationDate')">Application date</label>
					<date-picker
						ref="applicationDateInput"
						:id="uid('applicationDate')"
						v-model="applicationDate"
						required></date-picker>
					<span v-if="applicationDateError" class="input-instructions error" v-text="applicationDateError"></span>
					<span v-else class="input-instructions">When did you submit your application?</span>
				</div>
				<div class="form-group">
					<label :for="uid('applicationType')">Application type</label>
					<select :id="uid('applicationType')" v-model="applicationType" :class="{placeholder: !applicationType}" required>
						<option disabled hidden :value="null">What did you apply for?</option>
						<option value="BLUE_CARD">Blue Card</option>
						<option value="CITIZENSHIP">Citizenship</option>
						<option value="FAMILY_REUNION_VISA">Family reunion visa</option>
						<option value="FREELANCE_VISA">Freelance visa</option>
						<option value="JOB_SEEKER_VISA">Job seeker visa</option>
						<option value="PERMANENT_RESIDENCE">Permanent residence</option>
						<option value="STUDENT_VISA">Student visa</option>
						<option value="WORK_VISA">Work visa</option>
					</select>
				</div>
				<div class="form-group">
					<label :for="uid('city')">Application city</label>
					<city-input
						:id="uid('city')"
						v-model="city"
						placeholder="In which city did you apply?"
						required></city-input>
				</div>
				<hr>
				<div class="form-group">
					<span class="label">Extra information</span>
					<checkbox v-model="meetsRequirements">
						I meet all the application requirements
					</checkbox>
					<checkbox v-model="hasSubmittedDocuments">
						I have sent all required application documents
					</checkbox>
					<checkbox v-model="immigrationOfficeHasReplied">
						The immigration office has replied <template v-if="monthsAgo > 6">in the last 6 months</template>
					</checkbox>
				</div>
				<div class="form-group">
					<label :for="uid('message')">Comments</label>
					<textarea :id="uid('message')" v-model="message" placeholder="What else should Artjom know?"></textarea>
				</div>
				<template v-if="isTooEarlyToSue">
					<hr>
					<p>You should wait at least {{ minWaitMonths }} months to sue the immigration office. Suing too early will not help.</p>
				</template>
				<hr>
				<div class="buttons bar">
					<button class="button previous" @click="previousStage">
						Back
					</button>
					<button class="button primary next" @click="nextStage">
						Continue
					</button>
				</div>
			</template>

			<template v-if="stage === 'contact'">
				<h2>How can we contact you?</h2>
				<hr>
				<div class="form-group">
					<label :for="uid('fullName')">Full name</label>
					<full-name-input
						:id="uid('fullName')"
						v-model="fullName"
						required></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('email')">Email address</label>
					<email-input
						v-model="email"
						:id="uid('email')"
						required></email-input>
				</div>
				<hr>
				<div class="buttons bar">
					<button class="button previous" @click="previousStage">
						Back
					</button>
					<button class="button primary next" @click="submitForm" :disabled="isLoading" :class="{loading: isLoading}">
						Send
					</button>
				</div>
			</template>

			<template v-if="stage === 'thank-you'">
				<p><strong>Message sent!</strong> Artjom will review your case and contact you soon. You will get an email from <a :href="'mailto:' + recipientEmail">{{ recipientEmail }}</a> within 1 business day. If you don't get a response, check your spam folder.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button previous" @click="goToStart()">
						Go back
					</button>
				</div>
			</template>

			<template v-if="stage === 'error'">
				<p><strong>An error occurred</strong> while sending your request. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button previous" @click="goToStart()">
						Go back
					</button>
				</div>
			</template>
		</collapsible>
	`,
}

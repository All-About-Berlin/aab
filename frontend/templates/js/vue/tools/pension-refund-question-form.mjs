import Collapsible from '/js/vue/components/collapsible.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconExit from '/js/vue/components/icons/exit.mjs';

import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { calculatePensionRefund } from '/js/utils/pensionRefund.mjs';
import { getNearestHeadingId } from '/js/utils/tracking.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { validateForm } from '/js/utils/form.mjs';

export default {
	components: {
		Collapsible,
		CountryInput,
		IconDonate,
		IconExit,
		EmailInput,
		FullNameInput,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data: function() {
		return {
			isLoading: false,
			email: userDefaults.empty,
			fullName: userDefaults.empty,
			question: '',
			nationality: userDefaults.empty,
			countryOfResidence: userDefaults.empty,
			stage: 'contactInfo',
		};
	},
	methods: {
		async submitForm() {
			if(validateForm(this.$refs.collapsible.$el)) {
				this.isLoading = true;
				const response = await fetch(
					'/api/forms/pension-refund-question',
					{
						method: 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8'},
						body: JSON.stringify({
							name: this.fullName,
							email: this.email,
							question: this.question,
							nationality: this.nationality,
							country_of_residence: this.countryOfResidence,
						}),
					}
				);
				this.isLoading = false;
				this.stage = response.ok ? 'thank-you' : 'error';
				this.$nextTick(() => {
					this.$refs.collapsible.$el.scrollIntoView({ block: 'start', behavior: 'auto' });
					plausible('Pension refund question', { props: {
						stage: this.stage,
						pageSection: getNearestHeadingId(this.$el),
						referrer: getReferrer(),
					}});
				});
			}
		},
	},
	computed: {
		isEligible() {
			const threeYearsAgo = new Date();
			threeYearsAgo.setYear(threeYearsAgo.getFullYear() - 3);
			const fourYearsAgo = new Date();
			fourYearsAgo.setYear(fourYearsAgo.getFullYear() - 4);

			return calculatePensionRefund(
				this.nationality,
				this.countryOfResidence,
				threeYearsAgo,
				fourYearsAgo,
				40000,
				false,
			).flags.has('eligible');
		}
	},
	template: `
	<collapsible
		aria-description="Ask an expert about German pension payments refunds"
		aria-label="Pension refund question form"
		class="pension-refund-question"
		ref="collapsible"
		:static="static">
		<template v-slot:header>Ask a pension refund expert</template>
		<template v-if="stage === 'contactInfo'">
			<p><a target="_blank" href="/out/pension-refund-germany">Pension Refund Germany</a> helps people get their pension refund. They answer in 1 to 3 business days. This is a free service.</p>
			<hr>
			<div class="form-group">
				<label :for="uid('question')">Your question</label>
				<textarea v-model="question" :id="uid('question')" required placeholder=" "></textarea>
			</div>
			<div class="form-group">
				<label :for="uid('fullName')">
					Name
				</label>
				<full-name-input :id="uid('fullName')" v-model="fullName" required></full-name-input>
			</div>
			<div class="form-group">
				<label :for="uid('email')">
					Email address
				</label>
				<email-input v-model="email" :id="uid('email')" required></email-input>
			</div>
			<hr>
			<div class="form-group">
				<label :for="uid('nationality')">Nationality</label>
				<country-input
					country-code
					v-model="nationality"
					:id="uid('nationality')"
					required></country-input>
			</div>
			<div class="form-group">
				<label :for="uid('countryOfResidence')">Where do you live?</label>
				<country-input
					country-code
					v-model="countryOfResidence"
					:id="uid('countryOfResidence')"
					required></country-input>
				<span class="input-instructions error" v-if="!isEligible">You do not qualify for a pension refund.</span>
			</div>
			<input type="text" name="username" value="" autocomplete="off" hidden role="presentation" required/>
			<hr>
			<div class="buttons bar">
				<button class="button primary no-print" @click="submitForm" :disabled="isLoading" :class="{loading: isLoading}">Send question <i class="icon right" aria-hidden="true"></i></button>
			</div>
		</template>
		<template v-if="stage === 'thank-you'">
			<p><strong>Message sent!</strong> Pension Refund Germany will contact you soon.</p>
			<ul class="buttons list">
				<li>
					<a href="/guides/leaving-germany" target="_blank">
						<icon-exit/>
						<div>
							<h3>Learn how to leave Germany</h3>
							<p>Use my checklist for moving to another country.</p>
						</div>
					</a>
				</li>
				<li>
					<a href="/donate" target="_blank">
						<icon-donate/>
						<div>
							<h3>Support this website</h3>
							<p>Donate €10 to help me build more free tools.</p>
						</div>
					</a>
				</li>
			</ul>
		</template>
		<template v-if="stage === 'error'">
			<p><strong>An error occurred</strong> while sending your question. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
		</template>
	</collapsible>
	`
}
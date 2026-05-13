import Checkbox from '/js/vue/components/checkbox.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import Price from '/js/vue/components/price.mjs';

import IconDental from '/js/vue/components/icons/insurance/dental.mjs';
import IconHousehold from '/js/vue/components/icons/insurance/household.mjs';
import IconHealth from '/js/vue/components/icons/insurance/health.mjs';
import IconInsurance from '/js/vue/components/icons/insurance/insurance.mjs';
import IconLegal from '/js/vue/components/icons/insurance/legal.mjs';
import IconTravel from '/js/vue/components/icons/insurance/travel.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { insuranceCosts } from '/js/utils/constants.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { validateForm } from '/js/utils/form.mjs';

import metadata from '/js/vue/tools/insurance-checklist.metadata.json' with { type: 'json' };

export default {
	components: {
		Checkbox,
		Collapsible,
		EmailInput,
		FullNameInput,
		Price,
		IconDental,
		IconHousehold,
		IconHealth,
		IconInsurance,
		IconLegal,
		IconTravel,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, multiStageMixin, trackedStagesMixin],
	props: {
		static: Boolean,
	},
	data: function() {
		return {
			metadata,
			selectedInsurances: {
				health: false,
				liability: false,
				legal: false,
				disability: false,
				life: false,
				dental: false,
			},
			stages: [
				'checklist',
				'contactInfo',
				'thank-you',
				'error',
			],
			email: userDefaults.empty,
			fullName: userDefaults.empty,
			phone: '',
			isLoading: false,
			trackAs: 'Insurance checklist',
		};
	},
	computed: {
		insuranceTypes() {
			return [
				{
					key: 'health',
					label: 'Health',
					description: 'For getting healthcare. Required if you live in Germany or apply for a German visa.',
					minCost: insuranceCosts.health.min,
					maxCost: insuranceCosts.health.max,
					icon: 'health',
				},
				{
					key: 'liability',
					label: 'Liability',
					description: 'For accidents that cause expensive damage. Very good to have.',
					minCost: insuranceCosts.liability.min,
					maxCost: insuranceCosts.liability.max,
					icon: 'insurance',
				},
				{
					key: 'legal',
					label: 'Legal',
					description: 'For getting legal advice or suing someone.',
					minCost: insuranceCosts.legal.min,
					maxCost: insuranceCosts.legal.max,
					icon: 'legal',
				},
				{
					key: 'disability',
					label: 'Disability',
					description: "Gives you an income if you can't work because of a disability.",
					minCost: insuranceCosts.disability.min,
					maxCost: insuranceCosts.disability.max,
				},
				{
					key: 'life',
					label: 'Life',
					description: "Supports your family after your death.",
					minCost: insuranceCosts.life.min,
					maxCost: insuranceCosts.life.max,
				},
				{
					key: 'dental',
					label: 'Dental',
					description: 'For getting dental care in Germany.',
					minCost: insuranceCosts.dental.min,
					maxCost: insuranceCosts.dental.max,
					icon: 'dental',
				},
			];
		},
		hasSelectedOptions() {
			return Object.values(this.selectedInsurances).some(v => v);
		},
		totalMinCost() {
			return this.insuranceTypes
				.filter(t => this.selectedInsurances[t.key])
				.reduce((sum, t) => sum + t.minCost, 0);
		},
		totalMaxCost() {
			return this.insuranceTypes
				.filter(t => this.selectedInsurances[t.key])
				.reduce((sum, t) => sum + t.maxCost, 0);
		},
	},
	methods: {
		goToContactInfo() {
			if (this.hasSelectedOptions) {
				this.nextStage();
			}
		},
		async submitForm() {
			if (!validateForm(this.$el)) return;
			this.isLoading = true;
			const response = await fetch(
				'/api/insurance/multi-insurance-case',
				{
					method: 'POST',
					keepalive: true,
					headers: {'Content-Type': 'application/json; charset=utf-8'},
					body: JSON.stringify({
						name: this.fullName,
						email: this.email,
						phone: this.phone,
						health_insurance: this.selectedInsurances.health,
						liability_insurance: this.selectedInsurances.liability,
						legal_insurance: this.selectedInsurances.legal,
						disability_insurance: this.selectedInsurances.disability,
						life_insurance: this.selectedInsurances.life,
						dental_insurance: this.selectedInsurances.dental,
						referrer: getReferrer() || '',
					}),
				}
			);
			this.isLoading = false;
			this.goToStage(response.ok ? 'thank-you' : 'error');
		},
	},
	template: `
	<collapsible
		:aria-description="metadata.description"
		:aria-label="metadata.label"
		class="insurance-checklist"
		ref="collapsible"
		:static="static">
		<template v-slot:header>Insurance checklist</template>

		<template v-if="stage === 'checklist'">
			<p><strong>Let's get you covered.</strong> Choose the insurances you need.</p>
			<checkbox v-for="t in insuranceTypes" :key="t.key" v-model="selectedInsurances[t.key]">
				<component :is="'icon-' + (t.icon || 'insurance')"></component>
				<div>
					<h4>{{ t.label }}</h4>
					<p>{{ t.description }}</p>
				</div>
			</checkbox>
			<div class="buttons bar" v-if="hasSelectedOptions">
				<button class="button primary no-print" @click="goToContactInfo">Continue <i class="icon right" aria-hidden="true"></i></button>
			</div>
		</template>
		<template v-if="stage === 'contactInfo'">
			<p>Where can we send your insurance contract and documents?</p>
			<hr>
			<div class="form-group required">
				<label :for="uid('fullName')">Name</label>
				<full-name-input :id="uid('fullName')" v-model="fullName" required></full-name-input>
			</div>
			<div class="form-group required">
				<label :for="uid('email')">Email address</label>
				<email-input v-model="email" :id="uid('email')" required></email-input>
			</div>
			<input type="text" name="username" value="" autocomplete="off" hidden role="presentation" required/>
			<hr>
			<div class="buttons bar">
				<button class="button primary no-print" @click="submitForm" :disabled="isLoading" :class="{loading: isLoading}">Send request <i class="icon right" aria-hidden="true"></i></button>
			</div>
		</template>
		<template v-if="stage === 'thank-you'">
			<p><strong>Request sent!</strong> A broker will contact you soon to help you find the right insurances.</p>
		</template>
		<template v-if="stage === 'error'">
			<p><strong>An error occurred</strong> while sending your request. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
		</template>
	</collapsible>
	`
}
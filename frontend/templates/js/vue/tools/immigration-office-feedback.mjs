import CitizenshipFeedbackForm from '/js/vue/tools/citizenship-feedback-form.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import ResidencePermitFeedbackForm from '/js/vue/tools/residence-permit-feedback-form.mjs';
import Pagination from '/js/vue/components/pagination.mjs';
import Tabs from '/js/vue/components/tabs.mjs';
import { citizenshipDepartments } from '/js/utils/immigrationOffice.mjs'
import { formatLongDate, formatTimeDelta } from '/js/utils/date.mjs';
import { residencePermitTypes, residencePermitDepartments, oldResidencePermitDepartments } from '/js/utils/immigrationOffice.mjs';

export default {
	components: {
		CitizenshipFeedbackForm,
		Glossary,
		ResidencePermitFeedbackForm,
		Pagination,
		Tabs,
	},
	data() {
		return {
			isCitizenship: false,
			department: null,
			citizenshipDepartments,
			oldResidencePermitDepartments,

			apiEndpointForCurrentResults: null,
			page: 1,
			resultCount: 0,
			itemsPerPage: 10,
			resultsPage: [],
			stats: {},

			residencePermitType: null,
			residencePermitTypes,
			healthInsuranceTypes: {
				PUBLIC: {
					name: "public health insurance",
					glossaryTerm: "gesetzliche Krankenversicherung",
				},
				PRIVATE: {
					name: "private health insurance",
					glossaryTerm: "private Krankenversicherung",
				},
				EXPAT: {
					name: "expat health insurance",
					glossaryTerm: "Expat health insurance",
				},
				FAMILY: {
					name: "family health insurance",
					glossaryTerm: "Familienversicherung",
				},
				EHIC: {
					name: "health insurance from another EU country",
					glossaryTerm: "EHIC",
				},
				OTHER: {
					name: "another health insurance",
					glossaryTerm: null,
				},
			},

			isLoading: true,
		};
	},
	async mounted(){
		this.loadPage();
	},
	computed: {
		pageCount(){
			return this.isLoading ? 0 : Math.ceil(this.resultCount / this.itemsPerPage);
		},
		feedbackCount(){
			return this.stats?.first_response_date?.count || 0;
		},
		totalWaitAverage(){
			return this.stats?.total?.readable_average ?? 'unknown';
		},
		totalWaitRange(){
			return this.stats?.total?.readable_range ?? 'a few months';
		},
		residencePermitDepartments(){
			return residencePermitDepartments(this.residencePermitType);
		},
		guideUrl(){
			return residencePermitTypes?.[this.residencePermitType]?.guideUrl;
		},

		apiEndpoint(){
			let apiEndpoint = '/api/forms/citizenship-feedback.json';
			const querystring = new URLSearchParams({ page: this.page });
			if(this.department){
				querystring.append('department', this.department);
			}
			if(!this.isCitizenship){
				if(this.residencePermitType){
					querystring.append('residence_permit_type', this.residencePermitType);
				}
				apiEndpoint = '/api/forms/residence-permit-feedback.json';
			}
			return `${apiEndpoint}?${querystring.toString()}`;
		}
	},
	methods: {
		formatLongDate,
		formatTimeDelta,

		healthInsuranceType(result){
			return result.health_insurance_type && this.healthInsuranceTypes[result.health_insurance_type];
		},
		residencePermitName(residencePermitType){
			return {
				CITIZENSHIP: {
					normal: "citizenship",
					capitalized: "Citizenship",
					glossaryTerm: null,
				},
				...this.residencePermitTypes,
			}[residencePermitType] || {
				normal: "residence permit",
				capitalized: "Residence permit",
				glossaryTerm: "Aufenthaltstitel",
			};
		},
		departmentName(result){
			const longName = {
				...this.citizenshipDepartments,
				...this.oldResidencePermitDepartments,
				...residencePermitDepartments(),
			}[result.department];
			return longName?.split(' — ')[0];
		},
		stepWaitRange(stepKey){
			if(this.isLoading){
				return 'Loading…';
			}
			const range = this.stats[stepKey]?.readable_range;
			const average = this.stats[stepKey]?.readable_average;
			return range && average ?
				`Wait ${range} — ${average} on average`
				: 'Wait for an unknown duration';
		},
		waitTime(date1, date2, stillWaiting=false) {
			if(stillWaiting){
				const timeDelta = this.formatTimeDelta(date1, date2);
				return timeDelta.startsWith('1 ') ? `${timeDelta} has passed` : `${timeDelta} have passed`;
			}
			else if(date2 >= date1 && !this.isInTheFuture(date2)){
				return `Waited ${this.formatTimeDelta(date1, date2)}`
			}
			return `Waiting ${this.formatTimeDelta(date1, date2)}`;
		},
		isInTheFuture(date){
			return date > (new Date());
		},

		async loadPage(){
			if(this.apiEndpoint !== this.apiEndpointForCurrentResults){
				this.resultsPage = [];
				this.apiEndpointForCurrentResults = this.apiEndpoint;
				this.isLoading = true;

				const response = await (await fetch(this.apiEndpoint)).json();
				this.resultCount = response.count;
				this.resultsPage = response.results.map(r => {
					r.modification_date = new Date(r.modification_date);
					r.application_date = new Date(r.application_date);
					r.first_response_date = r.first_response_date ? new Date(r.first_response_date) : null;
					r.appointment_date = r.appointment_date ? new Date(r.appointment_date) : null;
					r.pick_up_date = r.pick_up_date ? new Date(r.pick_up_date) : null;
					return r;
				});
				this.stats = response.stats;

				this.isLoading = false;
			}
		},
		scrollToTopOfResults(){
			this.$nextTick(() => {
				this.$el.querySelector('#feedback-from-other-people').scrollIntoView({
					behavior: "instant",
					block: "start",
					inline: "nearest"
				});
			});
		},
		async deleteResult(modificationKey){
			if(confirm('Delete this item?')){
				const queryType = this.isCitizenship ? 'citizenship' : 'residence-permit';
				const apiEndpoint = `/api/forms/${queryType}-feedback/${modificationKey}`;
				await fetch(
					apiEndpoint, {
						method: 'DELETE',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8'}
					}
				);
				this.resultsPage = [];
				this.loadPage();
			}
		},
	},
	watch: {
		apiEndpoint(){
			this.$nextTick(() => this.loadPage());
		},
		isCitizenship(){
			this.department = null;
			this.residencePermitType = null;
			this.page = 1;
		},
		department(){
			this.page = 1;
		},
		residencePermitType(){
			// Avoiding invalid department + type combinations
			if(!(this.department in this.residencePermitDepartments)){
				this.department = null;
			}
			this.page = 1;
		},
	},
	template: `
		<div class="component-group">
			<div class="filters">
				<tabs
					id="is-citizenship-top"
					aria-label="Feedback type"
					v-model="isCitizenship"
					:options="[{label: 'Residence permit', value: false}, {label: 'Citizenship', value: true}]"
					required>
				</tabs>
				<select v-model="residencePermitType" v-if="!isCitizenship">
					<option :value="null">All types</option>
					<option disabled="disabled">──────────</option>
					<option v-for="(name, key) in residencePermitTypes" :key="key" :value="key" v-text="name.capitalized"></option>
				</select>
				<select v-model="department">
					<option :value="null">All departments</option>
					<option disabled="disabled">──────────</option>
					<option v-if="isCitizenship" v-for="(name, key) in citizenshipDepartments" :key="key" :value="key" v-text="name"></option>
					<option v-if="!isCitizenship" v-for="(name, key) in residencePermitDepartments" :key="key" :value="key" v-text="name"></option>
					<optgroup v-if="!isCitizenship && !residencePermitType" label="Old departments">
						<option v-for="(name, key) in oldResidencePermitDepartments" :key="key" :value="key" v-text="name"></option>
					</optgroup>
				</select>
			</div>

			<p>
				In Berlin, it takes <strong v-text="totalWaitRange">a few months</strong> to
				<template v-if="isCitizenship">become a German citizen.</template>
				<template v-else>get a <glossary :term="residencePermitName(residencePermitType).glossaryTerm">{{ residencePermitName(residencePermitType).normal }}</glossary>.</template>

				The average wait time is <span v-text="totalWaitAverage">unknown</span>.

				Wait times vary by <a href="/guides/immigration-office#departments">department</a><span v-if="!residencePermitType">&nbsp;and residence permit type</span>.

				Based on <a href="#feedback-from-other-people">feedback from <span v-text="feedbackCount">many</span> people</a>.
			</p>

			<div class="feedback-summary">
				<div class="steps">
					<div class="step completed">
						<input type="checkbox" checked disabled>
						<span class="description">Send your documents</span>
						<small class="duration" v-text="stepWaitRange('first_response_date')">Loading…</small>
					</div>
					<div class="step completed">
						<input type="checkbox" checked disabled>
						<span class="description">Get a response</span>
						<small class="duration" v-text="stepWaitRange('appointment_date')">Loading…</small>
					</div>
					<div class="step completed" v-if="isCitizenship">
						<input type="checkbox" checked disabled>
						<span class="description">Become a German citizen</span>
					</div>
					<template v-else>
						<div class="step completed">
							<input type="checkbox" checked disabled>
							<span class="description">Go to your Ausländerbehörde appointment</span>
							<small class="duration" v-text="stepWaitRange('pick_up_date')">Loading…</small>
						</div>
						<div class="step completed">
							<input type="checkbox" checked disabled>
							<span class="description">Pick up your residence card</span>
						</div>
					</template>
				</div>
			</div>

			<p v-if="guideUrl">
				<strong><a :href="guideUrl" class="internal-link">How to apply for the {{ residencePermitTypes[residencePermitType].normal }}</a></strong>
			</p>

			<citizenship-feedback-form v-if="isCitizenship" static></citizenship-feedback-form>
			<residence-permit-feedback-form v-else static></residence-permit-feedback-form>

			<h2 id="feedback-from-other-people">Feedback from other people</h2>

			<div class="filters">
				<tabs
					id="is-citizenship-bottom"
					aria-label="Feedback type"
					v-model="isCitizenship"
					:options="[{label: 'Residence permit', value: false}, {label: 'Citizenship', value: true}]"
					required>
				</tabs>
				<select v-model="residencePermitType" v-if="!isCitizenship">
					<option :value="null">All types</option>
					<option disabled="disabled">──────────</option>
					<option v-for="(name, key) in residencePermitTypes" :key="key" :value="key" v-text="name.capitalized"></option>
				</select>
				<select v-model="department">
					<option :value="null">All departments</option>
					<option v-if="isCitizenship" v-for="(name, key) in citizenshipDepartments" :key="key" :value="key" v-text="name"></option>
					<option v-if="!isCitizenship" v-for="(name, key) in residencePermitDepartments" :key="key" :value="key" v-text="name"></option>
					<optgroup v-if="!isCitizenship" label="Old departments">
						<option v-for="(name, key) in oldResidencePermitDepartments" :key="key" :value="key" v-text="name"></option>
					</optgroup>
				</select>
			</div>

			<div class="loading" v-if="isLoading">Loading feedback...</div>
			<ul class="feedback-list" v-show="!isLoading">
				<li v-for="result in resultsPage" v-if="!isLoading" :key="result.modification_date.toString()">
					<button class="button" v-if="result.modification_key" @click="deleteResult(result.modification_key)">Delete</button>
					<h3>
						{{ residencePermitName(result.residence_permit_type || 'CITIZENSHIP').capitalized }}
						<template v-if="isCitizenship && result.appointment_date">in {{ formatTimeDelta(result.application_date, result.appointment_date) }}</template>
						<template v-if="!isCitizenship && result.pick_up_date">in {{ formatTimeDelta(result.application_date, result.pick_up_date) }}</template>
						<span class="department" v-if="departmentName(result)">Department <span v-text="departmentName(result)"></span></span>
						<span class="validity" v-if="result.validity_in_months">
							Valid for
							<template v-if="result.validity_in_months % 12">{{ result.validity_in_months }} month{{ result.validity_in_months === 1 ? '' : 's'}}</template>
							<template v-if="!(result.validity_in_months % 12)">{{ result.validity_in_months/12 }} year{{ result.validity_in_months/12 === 1 ? '' : 's'}}</template>
						</span>
					</h3>
					<p v-if="result.notes.length" class="notes">“{{ result.notes.trim() }}”</p>
					<div class="steps">
						<div class="step completed">
							<input type="checkbox" checked disabled>
							<span class="description">
								Applied <span class="no-mobile">on {{ formatLongDate(result.application_date) }}</span>
								<small class="extra" v-if="healthInsuranceType(result)">
									Using
									<glossary v-if="healthInsuranceType(result).glossaryTerm" :term="healthInsuranceType(result).glossaryTerm">{{ healthInsuranceType(result).name }}</glossary>
									<template v-else>{{ healthInsuranceType(result).name }}</template>
									<template v-if="result.health_insurance_name">(“{{ result.health_insurance_name }}”)</template>
								</small>
							</span>
							<time v-text="formatLongDate(result.application_date)"></time>
						</div>

						<div class="step" :class="{completed: !!result.first_response_date}">
							<input type="checkbox" :checked="result.first_response_date" disabled>
							<span class="description">
								<template v-if="result.first_response_date">
									Got a response {{ formatTimeDelta(result.application_date, result.first_response_date) }} later
								</template>
								<template v-else>
									No response as of {{ formatLongDate(result.modification_date) }}
								</template>
							</span>
							<time v-if="result.first_response_date" v-text="formatLongDate(result.first_response_date)"></time>
						</div>

						<div class="step" v-if="!!result.first_response_date" :class="{completed: !!result.appointment_date}">
							<input type="checkbox" :checked="result.appointment_date" disabled>
							<span class="description">
								<template v-if="result.appointment_date">
									Went to appointment {{ formatTimeDelta(result.first_response_date, result.appointment_date) }} later
								</template>
								<template v-else>
									No appointment as of {{ formatLongDate(result.modification_date) }}
								</template>
							</span>
							<time v-if="result.appointment_date" v-text="formatLongDate(result.appointment_date)"></time>
						</div>

						<div v-if="!isCitizenship && !!result.appointment_date" class="step" :class="{completed: !!result.pick_up_date}">
							<input type="checkbox" :checked="result.pick_up_date" disabled>
							<span class="description">
								<template v-if="result.pick_up_date && isInTheFuture(result.pick_up_date)">
									Will pick up residence card after {{ formatTimeDelta(result.appointment_date, result.pick_up_date) }}
								</template>
								<template v-if="result.pick_up_date && !isInTheFuture(result.pick_up_date)">
									Picked up residence card {{ formatTimeDelta(result.appointment_date, result.pick_up_date) }} later
								</template>
								<template v-else>
									No pick-up date as of {{ formatLongDate(result.modification_date) }}
								</template>
							</span>
							<time v-if="result.pick_up_date" v-text="formatLongDate(result.pick_up_date)"></time>
						</div>
					</div>
				</li>
			</ul>

			<pagination :value="page" @input="page = $event; scrollToTopOfResults()" :page-count="pageCount"></pagination>
		</div>
	`,
}
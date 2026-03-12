import AgeInput from '/js/vue/components/age-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconSupport from '/js/vue/components/icons/support.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { residencePermitTypes, residencePermitDepartments, oldResidencePermitDepartments } from '/js/utils/immigrationOffice.mjs';

export default {
	components: {
		AgeInput,
		Collapsible,
		DatePicker,
		EmailInput,
		IconDonate,
		IconSupport,
	},
	props: {
		static: Boolean,
		type: {
			type: String,
			default: null,
		}
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, multiStageMixin, trackedStagesMixin],
	data() {
		return {
			department: null,
			oldDepartments: oldResidencePermitDepartments,
			residencePermitTypes,
			residencePermitType: null,

			showResidencePermitField: true,
			isLoading: false,

			// The primary key of the Feedback item, plus a two-letter prefix denoting the residencePermitType
			modificationKey: userDefaults.empty,

			notes: '',
			email: userDefaults.empty,

			healthInsurance: null,
			healthInsuranceName: null,

			validityUnit: 'months',
			validity: null,

			steps: {
				application: {
					dateFieldTitle: "Application date",
					completed: null,
					date: null,
				},
				response: {
					dateFieldTitle: "First response date",
					completed: null,
					date: null,
				},
				appointment: {
					dateFieldTitle: "Appointment date",
					completed: null,
					date: null,
				},
				pickup: {
					dateFieldTitle: "Pick-up date",
					completed: null,
					date: null,
				},
			},

			stages: [
				'start',
				'email',
				'finish',
				'error',
			],
			inputsToFocus: {
				email: () => this.$refs.emailInput.$el,
			},
		};
	},
	async mounted(){
		// The residence permit type can be pre-selected with the data-type attribute
		if(this.type){
			this.showResidencePermitField = false;
			this.residencePermitType = this.type;
		}

		// Load the key from the URL hash
		const keyFromHash = (new URLSearchParams(window.location.hash.substring(1))).get('feedbackKey');
		if(keyFromHash){
			this.modificationKey = keyFromHash;
			history.replaceState(null, null, ' '); // Remove the hash
		}

		// Set the residencePermitType from the modificationKey, but don't override a hard-coded type
		if(this.modificationKey && !this.residencePermitType){
			this.residencePermitType = this.modificationKey.split('~')[1];
		}

		if(this.modificationKey && this.modificationKeyMatchesResidencePermitType){
			const response = await fetch(this.apiEndpoint);
			if(!response.ok){
				this.modificationKey = null;
				return;
			}

			const responseJson = await response.json();

			this.steps.application.date = responseJson.application_date;
			this.steps.application.completed = !!responseJson.application_date;

			this.steps.response.date = responseJson.first_response_date;
			this.steps.response.completed = !!responseJson.first_response_date;

			this.steps.appointment.date = responseJson.appointment_date;
			this.steps.appointment.completed = !!responseJson.appointment_date;

			this.steps.pickup.date = responseJson.pick_up_date;
			this.steps.pickup.completed = !!responseJson.pick_up_date;

			this.healthInsurance = responseJson.health_insurance_type;
			this.healthInsuranceName = responseJson.health_insurance_name;

			this.email = responseJson.email || this.email;
			this.department = responseJson.department;
			this.notes = responseJson.notes;
			this.validity = responseJson.validity;
			this.validityUnit = (this.validity % 12 || !this.validity) ? 'months' : 'years';
		}
	},
	computed: {
		modificationKeyMatchesResidencePermitType(){
			return (
				this.residencePermitType
				&& this.modificationKey
				&& this.modificationKey.endsWith(this.residencePermitType)
			);
		},
		apiEndpoint(){
			if(this.modificationKeyMatchesResidencePermitType){
				return `/api/forms/residence-permit-feedback/${this.modificationKey.split('~')[0]}`
			}
			return '/api/forms/residence-permit-feedback';
		},
		trackAs(){
			return `Feedback (${this.residencePermitType})`;
		},
		ariaLabel(){
			return `Feedback form: ${this.residencePermitName} processing time`;
		},
		residencePermitName(){
			return this.residencePermitTypes[this.residencePermitType]?.normal || "residence permit";
		},
		showFeedbackLink(){
			return !window.location.pathname.startsWith('/guides/immigration-office/wait-times');
		},
		showRestOfForm(){
			return this.steps.application.completed;
		},
		departments(){
			return residencePermitDepartments(this.residencePermitType);
		},
		askAboutHealthInsurance(){
			return this.residencePermitType && this.residencePermitTypes[this.residencePermitType].askAboutHealthInsurance;
		},
		showHealthInsuranceNameField(){
			return ["PRIVATE", "EXPAT", "OTHER"].includes(this.healthInsurance);
		},
		validityInMonths(){
			if(!this.validity){
				return null;
			}
			return this.validity * (this.validityUnit === 'years' ? 12 : 1);
		},
		feedbackComplete(){
			return Object.values(this.steps).every(s => s.completed);
		},
	},
	methods: {
		async nextStage(){
			if(validateForm(this.$el)){
				if(this.stage === 'start'){
					this.goToStage((this.email || this.feedbackComplete) ? 'finish' : 'email');
				}
				else{
					this.goToStage('finish');
				}
			}
		},
		onStepCompletionChange(key){
			const changedStepIndex = Object.keys(this.steps).indexOf(key);
			Object.values(this.steps).forEach((step, index) => {
				// Tick all previous steps
				if(index < changedStepIndex && this.steps[key].completed){
					step.completed = true;
				}

				// Untick all following steps
				if(index > changedStepIndex && !this.steps[key].completed){
					step.completed = false;
				}
			})
		},
		async submitFeedback(){
			if(validateForm(this.$el)){
				this.isLoading = true;

				// Don't set the email before the email stage, even if it's not empty. The email might be prefilled by
				// userDefaultsMixin, but that does not mean the user consented to email notifications.
				const emailAddress = (
					(this.stage === 'email' && this.email)
					|| (this.stage === 'start' && this.modificationKey && this.email)
				) ? this.email : null;

				const response = await fetch(
					this.apiEndpoint,
					{
						method: this.modificationKeyMatchesResidencePermitType ? 'PUT' : 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8',},
						body: JSON.stringify({
							health_insurance_type: this.healthInsurance || '',
							health_insurance_name: this.healthInsuranceName || '',
							application_date: this.steps.application.date,
							appointment_date: (this.steps.appointment.completed ? this.steps.appointment.date : null),
							email: emailAddress,
							first_response_date: (this.steps.response.completed ? this.steps.response.date : null),
							department: this.department,
							notes: this.notes,
							pick_up_date: (this.steps.pickup.completed ? this.steps.pickup.date : null),
							residence_permit_type: this.residencePermitType,
							validity_in_months: this.validityInMonths,
						}),
					}
				);
				this.isLoading = false;
				if(response.ok){
					this.nextStage();
					const responseJson = await response.json();

					// No need to modify complete feedback, so the key gets cleared
					this.modificationKey = this.feedbackComplete ? null : `${responseJson.modification_key}~${this.residencePermitType}`;
				}
				else{
					this.goToStage('error');
				}
			}
		},
		stepName(key){
			return {
				application: "I have applied in Berlin",
				response: "The immigration office has replied",
				appointment: "I have an appointment",
				pickup: "I have a pick-up date for the residence card",
			}[key];
		},
		minimumStepDate(step){
			const stepList = Object.values(this.steps);
			const previousStep = stepList[stepList.indexOf(step) - 1];
			return previousStep?.date ? previousStep.date : null;
		},
	},
	watch: {
		residencePermitType: {
			handler(newType){
				// Auto select department if it's the only available option
				if(Object.keys(this.departments).length === 1){
					this.department = Object.keys(this.departments)[0];
				}
				// Deselect department if it's not a valid option
				else if(this.department && !(this.department in this.departments)){
					this.department = null;
				}
			},
			immediate: true, // So it runs before mounted()
		},
	},
	template: `
		<collapsible
			:aria-label="ariaLabel"
			aria-description="Share your experience applying for a residence permit in Berlin."
			class="feedback-form"
			:static="static">
			<template v-slot:header>
				How is your <span class="no-mobile">{{ residencePermitName }}</span> application going?
			</template>
			<template v-if="stage === 'start'">
				<h3 v-if="static">How is your {{ residencePermitName }} application going?</h3>
				<div class="steps">
					<div class="step" v-for="(step, key, index) in steps" :key="key">
						<input :id="uid('checkbox' + key)" type="checkbox" v-model="step.completed" @change="onStepCompletionChange(key)">
						<label :for="uid('checkbox' + key)" class="description" v-text="stepName(key)"></label>
						<div class="duration form-group" v-if="step.completed">
							<label :for="uid(key) + '-date'" v-text="step.dateFieldTitle"></label>
							<date-picker :min="minimumStepDate(step)" v-model="step.date" :id="uid(key) + '-date'" required></date-picker>
						</div>
					</div>
				</div>
				<template v-if="showFeedbackLink && !showRestOfForm">
					<hr>
					<div class="icon-paragraph">
						<icon-support/>
						<div>
							<p>
								Your feedback helps others plan their {{ residencePermitName }} application.
							</p>
							<p>
								<strong><a class="internal-link" target="_blank" href="/guides/immigration-office/wait-times">Read other people's feedback</a></strong>
							</p>
						</div>
					</div>
				</template>
				<template v-if="showRestOfForm">
					<hr>
					<div class="form-group" v-if="showResidencePermitField">
						<label :for="uid('residencePermitType')">Residence permit</label>
						<select :id="uid('residencePermitType')" v-model="residencePermitType" :class="{placeholder: !residencePermitType}" required>
							<option disabled hidden default :value="null">Choose a residence permit</option>
							<option v-for="(name, key) in residencePermitTypes" :key="key" :value="key" v-text="name.capitalized"></option>
						</select>
						<span class="input-instructions">
							Which residence permit did you apply for?
						</span>
					</div>
					<div class="form-group">
						<label :for="uid('department')">Department</label>
						<select :id="uid('department')" v-model="department" :class="{placeholder: !department}" required>
							<option disabled hidden default :value="null">Choose a department</option>
							<option v-for="(name, key) in departments" :value="key" :key="key" v-text="name"></option>
						</select>
						<span class="input-instructions">
							<a target="_blank" href="/guides/immigration-office#departments">Find your Ausländerbehörde department.</a> Don't choose a random department.
						</span>
					</div>
					<hr>
					<template v-if="askAboutHealthInsurance">
						<div class="form-group">
							<label :for="uid('healthInsurance')">Health insurance</label>
							<select :id="uid('healthInsurance')" v-model="healthInsurance" :class="{placeholder: healthInsurance == null}">
								<option disabled hidden default :value="null">Type of health insurance</option>
								<option value="PUBLIC">Public health insurance</option>
								<option value="PRIVATE">Private health insurance</option>
								<option value="EXPAT">Expat health insurance</option>
								<option value="FAMILY">Insured by family</option>
								<option value="EHIC">Insured by another EU country</option>
								<option value="OTHER">Other</option>
								<option value="">I don't know</option>
							</select>
							<input v-if="showHealthInsuranceNameField" placeholder="Name of health insurance" type="text" v-model="healthInsuranceName"/>
							<span class="input-instructions">Which health insurance did you use when you applied?</span>
						</div>
						<hr>
					</template>

					<template v-if="steps.appointment.completed && residencePermitType !== 'PERMANENT_RESIDENCE'">
						<div class="form-group">
							<label :for="uid('validity')">Permit validity</label>
							<div class="input-group">
								<input :id="uid('validity')" type="text" placeholder="0" inputmode="numeric" pattern="[0-9]*" v-model.number="validity" maxlength="2">
								<select v-model="validityUnit">
									<option value="months">month{{ validity === 1 ? '' : 's' }}</option>
									<option value="years">year{{ validity === 1 ? '' : 's' }}</option>
								</select>
							</div>
							<span class="input-instructions">The expiration date is <a href="/images/residence-permit-expiration-date.jpg" target="_blank">on the back of your {{ residencePermitName }}</a>.</span>
						</div>
						<hr>
					</template>
					<div class="form-group">
						<label :for="uid('notes')">Notes and advice</label>
						<textarea placeholder=" " v-model="notes" :id="uid('notes')"></textarea>
						<span class="input-instructions">Add information about your situation and give advice to other people. Do not ask questions here.</span>
					</div>
				</template>
			</template>
			<template v-if="stage === 'email'">
				<p><strong>Thank you for your feedback!</strong> It will help a lot of people.</p>
				<p>Can you complete your feedback when you get your {{ residencePermitName }}? I can remind you by email.</p>
				<div class="form-group">
					<label :for="uid('email')">Email address</label>
					<email-input ref="emailInput" v-model="email" :id="uid('email')" required></email-input>
					<span class="input-instructions">You will get a reminder in 2 months and in 6 months. Nothing else.</span>
				</div>
			</template>
			<template v-if="stage === 'finish'">
				<p><strong>Thank you for your feedback!</strong> This information will help a lot of people.</p>
				<ul class="buttons list">
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
				<p><strong>An error occurred.</strong> If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
			</template>
			<template v-if="showRestOfForm && stage !== 'finish'">
				<hr>
				<div class="buttons bar" v-if="showRestOfForm && stage !== 'finish'">
					<button v-if="stage === 'email' || stage === 'error'" class="button" @click="goToStage('start')"><i class="icon left" aria-hidden="true"></i> Go back</button>
					<button
						class="button primary"
						v-if="stage === 'start'"
						:disabled="isLoading"
						:class="{loading: isLoading}"
						@click="submitFeedback">{{ modificationKeyMatchesResidencePermitType ? 'Update' : 'Send' }} feedback</button>
					<button class="button primary" v-if="stage === 'email'" @click="submitFeedback">Remind me</button>
				</div>
			</template>
		</collapsible>
	`
}
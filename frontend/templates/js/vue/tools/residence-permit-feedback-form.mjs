import AgeInput from '/js/vue/components/age-input.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
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
import { citizenshipDepartments, residencePermitTypes, residencePermitDepartments, oldResidencePermitDepartments } from '/js/utils/immigrationOffice.mjs';

import citizenshipMetadata from '/js/vue/tools/citizenship-feedback-form.metadata.json' with { type: 'json' };
import residencePermitMetadata from '/js/vue/tools/residence-permit-feedback-form.metadata.json' with { type: 'json' };

export default {
	components: {
		AgeInput,
		Checkbox,
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
			// Common fields
			modificationKey: userDefaults.empty,  // Format: [unique hash]~[permit type]
			documentType: null,
			department: null,
			notes: '',
			emailAddress: null, // Not named 'email' so userDefaultsMixin doesn't load it from localStorage

			// Citizenship only
			citizenshipSteps: {
				application: {
					name: "I have applied in Berlin",
					dateFieldTitle: "Application date",
					completed: null,
					date: null
				},
				response: {
					name: "I got a reply",
					dateFieldTitle: "First response date",
					completed: null,
					date: null
				},
				appointment: {
					name: "I got an appointment",
					dateFieldTitle: "Appointment date",
					completed: null,
					date: null
				},
			},

			// Residence permits only
			showResidencePermitField: true,
			healthInsurance: null,
			healthInsuranceName: null,
			validityUnit: 'months',
			validity: null,
			residencePermitTypes,
			residencePermitSteps: {
				application: {
					name: "I have applied in Berlin",
					dateFieldTitle: "Application date",
					completed: null,
					date: null
				},
				response: {
					name: "The immigration office has replied",
					dateFieldTitle: "First response date",
					completed: null,
					date: null
				},
				appointment: {
					name: "I have an appointment",
					dateFieldTitle: "Appointment date",
					completed: null,
					date: null
				},
				pickup: {
					name: "I have a pick-up date for the residence card",
					dateFieldTitle: "Pick-up date",
					completed: null,
					date: null
				},
			},

			isLoading: false,
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
		// The residence permit type can be pre-selected with the "data-type" attribute
		if(this.type){
			this.showResidencePermitField = false;
			this.documentType = this.type;
		}

		// Note: the modificationKey might be loaded from localStorage by userDefaultsMixin

		// Load the modification key from the URL hash, if it's there
		const keyFromHash = (new URLSearchParams(window.location.hash.substring(1))).get('feedbackKey');
		if(keyFromHash){
			this.modificationKey = keyFromHash;
			history.replaceState(null, null, ' '); // Remove the hash from the URL
		}

		// Set the residence permit type from the modificationKey
		if(this.modificationKey && !this.documentType){
			this.documentType = this.modificationKey.split('~')[1];
		}

		if(this.isUpdatingExistingFeedback){
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

			if(!this.isCitizenship){
				this.steps.pickup.date = responseJson.pick_up_date;
				this.steps.pickup.completed = !!responseJson.pick_up_date;

				this.healthInsurance = responseJson.health_insurance_type;
				this.healthInsuranceName = responseJson.health_insurance_name;
				this.validity = responseJson.validity;
				this.validityUnit = (this.validity % 12 || !this.validity) ? 'months' : 'years';
			}

			this.emailAddress = responseJson.email || this.emailAddress;
			this.department = responseJson.department;
			this.notes = responseJson.notes;
		}
	},
	computed: {
		metadata(){
			return this.isCitizenship ? citizenshipMetadata : residencePermitMetadata;
		},
		trackAs(){
			return `Feedback (${this.documentType})`;
		},

		steps(){
			return this.isCitizenship ? this.citizenshipSteps : this.residencePermitSteps;
		},
		departments(){
			return this.isCitizenship ? citizenshipDepartments : residencePermitDepartments(this.documentType);
		},

		documentName(){
			if(this.isCitizenship) return 'citizenship';
			return this.residencePermitTypes[this.documentType]?.normal || "residence permit";
		},
		isCitizenship(){
			return this.documentType === 'CITIZENSHIP';
		},
		isUpdatingExistingFeedback(){
			// The user might have a modification key for a different kind of residence permit.
			// For example, a form that's pre-set to Blue Card feedback should be in "new feedback" mode, even if
			// the user has a modification key for a freelance visa.
			return (
				this.modificationKey
				&& this.documentType
				&& this.modificationKey.endsWith(this.documentType)
			);
		},

		showFeedbackLink(){
			return !window.location.pathname.startsWith('/guides/immigration-office/wait-times');
		},
		submittedOnDate(){
			return this.steps.application.date
				? new Date(this.steps.application.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })
				: null;
		},
		showRestOfForm(){
			return this.steps.application.completed;
		},
		askAboutValidity(){
			return this.allStepsAreCompleted && this.documentType && !['PERMANENT_RESIDENCE', 'CITIZENSHIP'].includes(this.documentType);
		},
		validityInMonths(){
			if(this.validity){
				return this.validity * (this.validityUnit === 'years' ? 12 : 1);
			}
			return null;
		},
		askAboutHealthInsurance(){
			return this.documentType && [
				'FAMILY_REUNION_VISA',
				'FREELANCE_VISA',
				'JOB_SEEKER_VISA',
				'PERMANENT_RESIDENCE',
				'STUDENT_VISA'
			].includes(this.documentType);
		},
		askAboutHealthInsuranceName(){
			return ["PRIVATE", "EXPAT", "OTHER"].includes(this.healthInsurance);
		},
		allStepsAreCompleted(){
			return Object.values(this.steps).every(s => s.completed);
		},

		apiEndpoint(){
			const type = this.isCitizenship ? 'citizenship' : 'residence-permit';
			const url = `/api/forms/${type}-feedback`;
			if(this.isUpdatingExistingFeedback){
				return url + '/' + this.modificationKey.split('~')[0];
			}
			return url;
		},
	},
	methods: {
		async nextStage(){
			if(validateForm(this.$el)){
				if(this.stage === 'start'){
					this.goToStage((this.emailAddress || this.allStepsAreCompleted) ? 'finish' : 'email');
				}
				else{
					this.goToStage('finish');
				}
			}
		},
		onStepCompletionChange(key){
			// Check steps before this one. Uncheck steps after this one.
			const changedStepIndex = Object.keys(this.steps).indexOf(key);
			Object.values(this.steps).forEach((step, index) => {
				if(index < changedStepIndex && this.steps[key].completed){
					step.completed = true;
				}
				if(index > changedStepIndex && !this.steps[key].completed){
					step.completed = false;
				}
			});
		},
		minimumStepDate(step){
			// Date should be greater than or equal to the previous step's date
			const stepList = Object.values(this.steps);
			const previousStep = stepList[stepList.indexOf(step) - 1];
			return previousStep?.date ?? null;
		},
		async submitFeedback(){
			if(validateForm(this.$el)){
				this.isLoading = true;

				const body = {
					application_date: this.steps.application.date,
					first_response_date: (this.steps.response.completed ? this.steps.response.date : null),
					appointment_date: (this.steps.appointment.completed ? this.steps.appointment.date : null),
					email: this.emailAddress,
					notes: this.notes,
					department: this.department,
					subscribe_to_newsletter: false,
				};

				if(!this.isCitizenship){
					body.residence_permit_type = this.documentType;
					body.pick_up_date = this.steps.pickup.completed ? this.steps.pickup.date : null;
					if(this.askAboutHealthInsurance){
						body.health_insurance_type = this.healthInsurance || '';
					}
					if(this.askAboutHealthInsuranceName){
						body.health_insurance_name = this.healthInsuranceName || '';
					}
					if(this.askAboutValidity){
						body.validity_in_months = this.validityInMonths;
					}
				}

				const response = await fetch(
					this.apiEndpoint,
					{
						method: this.isUpdatingExistingFeedback ? 'PUT' : 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8',},
						body: JSON.stringify(body),
					}
				);
				this.isLoading = false;
				if(response.ok){
					this.nextStage();
					if(this.allStepsAreCompleted){
						// No need to modify feedback that is complete
						this.modificationKey = null;
					}
					else{
						const responseJson = await response.json();
						this.modificationKey = `${responseJson.modification_key}~${this.documentType}`;
					}
				}
				else{
					this.goToStage('error');
				}
			}
		},
		clearForm(){
			this.modificationKey = null;
			Object.values(this.steps).forEach(step => {
				step.completed = null;
				step.date = null;
			});
			this.notes = '';
			this.department = null;
			this.healthInsurance = null;
			this.healthInsuranceName = null;
			this.validity = null;
			this.validityUnit = 'months';
		},
	},
	watch: {
		documentType: {
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
			:aria-label="metadata.label"
			:aria-description="metadata.description"
			class="feedback-form"
			:static="static">
			<template v-slot:header>
				How is your <span class="no-mobile">{{ documentName }}</span> application going?
			</template>
			<template v-if="stage === 'start'">
				<h3 v-if="static">How is your {{ documentName }} application going?</h3>
				<template v-if="isUpdatingExistingFeedback && submittedOnDate">
					<p>You are updating the feedback you submitted on {{ submittedOnDate }}. To give feedback about a different application, <button class="button link" @click="clearForm">clear the form</button>.</p>
					<hr>
				</template>
				<div class="steps">
					<div class="step" v-for="(step, key, index) in steps" :key="key">
						<input :id="uid('checkbox' + key)" type="checkbox" v-model="step.completed" @change="onStepCompletionChange(key)">
						<label :for="uid('checkbox' + key)" class="description" v-text="step.name"></label>
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
								Your feedback helps others plan their {{ documentName }} application.
							</p>
							<p>
								<strong><a class="internal-link" target="_blank" href="/guides/immigration-office/wait-times">Read other people's feedback</a></strong>
							</p>
						</div>
					</div>
				</template>
				<template v-if="showRestOfForm">
					<hr>
					<div class="form-group" v-if="!isCitizenship && showResidencePermitField">
						<label :for="uid('documentType')">Residence permit</label>
						<select :id="uid('documentType')" v-model="documentType" :class="{placeholder: !documentType}" required>
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
							<a target="_blank" href="/guides/immigration-office#departments">Find the correct department.</a> Don't choose a random department.
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
							<input v-if="askAboutHealthInsuranceName" placeholder="Name of health insurance" type="text" v-model="healthInsuranceName"/>
							<span class="input-instructions">Which health insurance did you use for your application?</span>
						</div>
						<hr>
					</template>
					<template v-if="askAboutValidity">
						<div class="form-group">
							<label :for="uid('validity')">Permit validity</label>
							<div class="input-group">
								<input :id="uid('validity')" type="text" placeholder="0" inputmode="numeric" pattern="[0-9]*" v-model.number="validity" maxlength="2">
								<select v-model="validityUnit">
									<option value="months">month{{ validity === 1 ? '' : 's' }}</option>
									<option value="years">year{{ validity === 1 ? '' : 's' }}</option>
								</select>
							</div>
							<span class="input-instructions">The expiration date is <a href="/images/residence-permit-expiration-date.jpg" target="_blank">on the back of your {{ documentName }}</a>.</span>
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
				<h3>One last thing&hellip;</h3>
				<p>
					Your feedback is incomplete. If you enter your email, I will send you a link. You can use this link to complete your feedback later.
				</p>
				<div class="form-group">
					<label :for="uid('email')">Email address</label>
					<email-input ref="emailInput" v-model="emailAddress" :id="uid('email')" required></email-input>
					<span class="input-instructions">
						You will get 2 reminder emails, no spam.
					</span>
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
						@click="submitFeedback">{{ isUpdatingExistingFeedback ? 'Update' : 'Send' }} feedback</button>
					<button class="button primary" v-if="stage === 'email'" @click="submitFeedback">Finish</button>
				</div>
			</template>
		</collapsible>
	`
}

import Checkbox from '/js/vue/components/checkbox.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconSupport from '/js/vue/components/icons/support.mjs';

import feedbackFormMixin from '/js/vue/mixins/feedbackForm.mjs';
import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { citizenshipDepartments } from '/js/utils/immigrationOffice.mjs';

import metadata from '/js/vue/tools/citizenship-feedback-form.metadata.json' with { type: 'json' };

export default {
	components: {
		Checkbox,
		Collapsible,
		DatePicker,
		EmailInput,
		IconDonate,
		IconSupport,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, multiStageMixin, trackedStagesMixin, feedbackFormMixin],
	props: {
		static: Boolean,
	},
	data() {
		return {
			metadata,

			citizenshipModificationKey: userDefaults.empty,

			department: null,
			departments: citizenshipDepartments,

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
			},

			trackAs: 'Feedback (citizenship)',
		};
	},
	async mounted(){
		// Load the key from the URL hash
		const keyFromHash = (new URLSearchParams(window.location.hash.substring(1))).get('feedbackKey');
		if(keyFromHash){
			this.citizenshipModificationKey = keyFromHash;
			history.replaceState(null, null, ' '); // Remove the hash
		}

		if(this.citizenshipModificationKey){
			const response = await fetch(this.apiEndpoint);
			if(!response.ok){
				this.citizenshipModificationKey = null;
				return;
			}

			const responseJson = await response.json();

			this.steps.application.date = responseJson.application_date;
			this.steps.application.completed = !!responseJson.application_date;

			this.steps.response.date = responseJson.first_response_date;
			this.steps.response.completed = !!responseJson.first_response_date;

			this.steps.appointment.date = responseJson.appointment_date;
			this.steps.appointment.completed = !!responseJson.appointment_date;

			this.emailAddress = responseJson.email || this.emailAddress;
			this.notes = responseJson.notes;

			this.department = responseJson.department;
		}
	},
	computed: {
		apiEndpoint(){
			if(this.citizenshipModificationKey){
				return `/api/forms/citizenship-feedback/${this.citizenshipModificationKey}`
			}
			return '/api/forms/citizenship-feedback';
		},
	},
	methods: {
		async submitFeedback(){
			if(validateForm(this.$el)){
				this.isLoading = true;

				const response = await fetch(
					this.apiEndpoint,
					{
						method: this.citizenshipModificationKey ? 'PUT' : 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8',},
						body: JSON.stringify({
							application_date: this.steps.application.date,
							appointment_date: (this.steps.appointment.completed ? this.steps.appointment.date : null),
							email: this.emailAddress,
							first_response_date: (this.steps.response.completed ? this.steps.response.date : null),
							notes: this.notes,
							department: this.department,
							subscribe_to_newsletter: this.subscribeToNewsletter,
						}),
					}
				);
				this.isLoading = false;
				if(response.ok){
					this.nextStage();
					const responseJson = await response.json();

					// No need to modify complete feedback, so the key gets cleared
					this.citizenshipModificationKey = this.feedbackComplete ? null : responseJson.modification_key;
				}
				else{
					this.goToStage('error');
				}
			}
		},
		clearForm(){
			this.citizenshipModificationKey = null;
			Object.values(this.steps).forEach(step => {
				step.completed = null;
				step.date = null;
			});
			this.notes = '';
			this.department = null;
		},
		stepName(key){
			return {
				application: "I have applied in Berlin",
				response: "I got a reply",
				appointment: "I got an appointment",
			}[key];
		},
	},
	template: `
		<collapsible
			:aria-label="metadata.label"
			:aria-description="metadata.description"
			class="feedback-form"
			:static="static">
			<template v-slot:header>
				How is your <span class="no-mobile">citizenship</span> application going?
			</template>
			<template v-if="stage === 'start'">
				<h3 v-if="static">How is your citizenship application going?</h3>
				<template v-if="citizenshipModificationKey && submittedOnDate">
					<p>You are updating the feedback you submitted on {{ submittedOnDate }}. To give new feedback about a different application, <button class="button link" @click="clearForm">clear the form</button>.</p>
					<hr>
				</template>
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
								Your feedback helps others plan their citizenship application.
							</p>
							<p>
								<strong><a class="internal-link" target="_blank" href="/guides/immigration-office/wait-times">Read other people's feedback</a></strong>
							</p>
						</div>
					</div>
				</template>
				<template v-if="showRestOfForm">
					<hr>
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
					<div class="form-group optional">
						<label :for="uid('notes')">Notes and advice</label>
						<textarea placeholder=" " v-model="notes" :id="uid('notes')"></textarea>
						<span class="input-instructions">Add information about your situation and give advice to other people. Do not ask questions here.</span>
					</div>
				</template>
			</template>
			<template v-if="stage === 'email'">
				<h2 v-if="isEmailRequired">One last thing&hellip;</h2>
				<p>
					<template v-if="isEmailRequired">
						Your email is required because your feedback is incomplete. I will send you a link. You can use that link to complete your feedback later.
					</template>
					<template v-else>
						<strong>Thank you for your feedback!</strong> If you enter your email, I will send you a link. You can use this link to complete your feedback later.
					</template>
				</p>
				<div class="form-group">
					<label :for="uid('email')">Email address</label>
					<email-input ref="emailInput" v-model="emailAddress" :id="uid('email')" required></email-input>
					<checkbox class="newsletter-checkbox" v-model="subscribeToNewsletter"><span>Subscribe to the <a href="/newsletter" target="_blank">monthly newsletter</a></span></checkbox>
					<span class="input-instructions">
						You will get 2 reminders,
						<template v-if="subscribeToNewsletter">and the monthly newsletter.</template>
						<template v-else>no spam.</template>
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
						@click="submitFeedback">{{ citizenshipModificationKey ? 'Update' : 'Send' }} feedback</button>
					<button class="button primary" v-if="stage === 'email'" @click="submitFeedback">{{ isEmailRequired ? 'Finish' : 'Remind me' }}</button>
				</div>
			</template>
		</collapsible>
	`
}
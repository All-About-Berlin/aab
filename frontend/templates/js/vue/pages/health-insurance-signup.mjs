import Checkbox from '/js/vue/components/checkbox.mjs';
import ChildrenInput from '/js/vue/components/children-input.mjs';
import CityInput from '/js/vue/components/city-input.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconEmployee from '/js/vue/components/icons/employee.mjs';
import IconFamily from '/js/vue/components/icons/family.mjs';
import IconFreelancer from '/js/vue/components/icons/freelancer.mjs';
import IconStudent from '/js/vue/components/icons/student.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import PostalcodeInput from '/js/vue/components/postalcode-input.mjs';
import Radio from '/js/vue/components/radio.mjs';
import store from '/js/vue/pages/health-insurance-signup-store.mjs';
import Tabs from '/js/vue/components/tabs.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import YesNoInput from '/js/vue/components/yes-no-input.mjs';
import { salaryOrIncome } from '/js/utils/occupations.mjs';

export default {
	components: {
		Checkbox,
		ChildrenInput,
		CityInput,
		CountryInput,
		DatePicker,
		EmailInput,
		FirstNameInput,
		Glossary,
		IconEmployee,
		IconFamily,
		IconFreelancer,
		IconStudent,
		IncomeInput,
		LastNameInput,
		PostalcodeInput,
		Radio,
		Tabs,
		YesNoInput,
	},
	mixins: [uniqueIdsMixin, multiStageMixin, trackedStagesMixin],
	data() {
		return {
			trackAs: 'Health insurance signup',

			// Stages are turned on/off based on form content
			allStages: {
				start: {
					label: 'Start',
					enabled: true
				},
				family: {
					label: 'People to insure',
					enabled: true
				},
				you: {
					label: 'You',
					enabled: true
				},
				spouse: {
					label: 'Your spouse',
					enabled: false
				},
				children: {
					label: 'Your children',
					enabled: false
				},
				occupation: {
					label: 'Occupation',
					enabled: true
				},
				contactInfo: {
					label: 'Contact',
					enabled: true
				},
				'thank-you': {
					enabled: true
				},
				error: {
					enabled: true
				},
			},

			insureSpouse: false,
			insureChildren: false,

			// Occupation
			isEmployed: null,
			isStudent: null,
			isSelfEmployed: null,

			insuranceStartDate: '',
			hasCurrentGermanInsurance: null,
			hasCurrentInsuranceAbroad: null,
			currentInsuranceCountry: '',
			currentInsuranceType: '',
			currentInsurerName: '',
			isCurrentlyPolicyHolder: null,
			inputIncome: null,
			useMonthlyIncome: false,
			isFirstJobInGermany: null,
			hasStartedWorking: null,
			employmentStartDate: '',
			employmentHoursPerWeek: null,
			hasLivedAbroad: null,
			countryOfLastInsurance: '',
			selfEmploymentHoursPerWeek: null,
			selfEmploymentIncomePerMonth: null,
			isManagingDirector: null,
			isStartupFounder: null,
			hasEmployees: null,
			hasMultipleMinijobEmployees: null,
			childrenCount: null,
			insureFamilyMembers: null,

			email: '',
			phone: '',

			gender: '',
			title: '',
			firstName: '',
			lastName: '',
			birthName: '',
			showExtraNameFields: false,
			nationality: '',
			dateOfBirth: '',
			birthPlace: '',
			birthCountry: '',
			street: '',
			houseNumber: '',
			buildingDetails: '',
			postCode: '',
			city: '',
			country: '',
		};
	},
	computed: {
		occupation(){
			if(this.isStudent){
				if(this.isSelfEmployed){
					return 'studentSelfEmployed';
				}
				else if(this.isEmployed){
					return 'studentEmployee';
				}
				return 'student';
			}
			else if(this.isEmployed){
				return 'employee';
			}
			else if(this.isSelfEmployed){
				return 'selfEmployed';
			}
			return null;
		},
		monthOrYear(){
			return this.useMonthlyIncome ? 'month' : 'year';
		},
		monthlyIncome(){
			return this.useMonthlyIncome ? this.inputIncome : this.inputIncome / 12;
		},
		showContinueButton(){
			if(this.stage === 'you'){
				return this.occupation;
			}
			return !['thank-you', 'error'].includes(this.stage);
		},
		showBackButton(){
			return !['start', 'error'].includes(this.stage);
		},
	},
	methods: {
		selectOccupation(occupation){
			this.occupation = occupation;
		},
		toggleUseMonthlyIncome(){
			this.useMonthlyIncome = !this.useMonthlyIncome;
			if(this.useMonthlyIncome){
				this.inputIncome = Math.round(this.inputIncome / 12);
			}
			else{
				this.inputIncome *= 12;
			}
		},
		finish(){
			this.goToStage('thank-you');
		},
		updateStages(){
			this.allStages.spouse.enabled = this.insureSpouse;
			this.allStages.children.enabled = this.insureChildren && this.childrenCount > 0;
			this.stages = Object.entries(this.allStages)
				.filter(([stageKey, stage]) => stage.enabled)
				.map(([stageKey]) => stageKey);
		},
	},
	created(){
		this.updateStages();
	},
	watch: {
		insureSpouse(){ this.updateStages(); },
		insureChildren(){ this.updateStages(); },
		childrenCount(){ this.updateStages(); },
		allStages: {
			immediate: true,
			handler(value){ store.sidebarStages = value; },
		},
		stage: {
			immediate: true,
			handler(value){ store.currentSidebarStage = value; },
		},
	},
	template: `
		<section class="section">
			<template v-if="stage === 'start'">
				<h1>Sign up for German health insurance</h1>
				<p>Sign up online for public health insurance with TK. It only takes a few minutes.</p>
			</template>

			<template v-if="stage === 'you'">
				<h2>What is your occupation?</h2>
				<p>Your occupation affects your insurance options, and the cost of your insurance.</p>
				<ul class="buttons grid" aria-label="Occupations">
					<li>
						<label>
							<input type="checkbox" v-model="isEmployed">
							<icon-employee/>
							Employee
						</label>
					</li>
					<li>
						<label>
							<input type="checkbox" v-model="isStudent">
							<icon-student/>
							Student
						</label>
					</li>
					<li>
						<label>
							<input type="checkbox" v-model="isSelfEmployed">
							<icon-freelancer/>
							Self-employed
						</label>
					</li>
				</ul>

				<template v-if="isEmployed">
					<hr>
					<h3>Information about your job</h3>

					<div class="form-group">
						<label :for="uid('income')">
							Salary
						</label>
						<div class="input-group">
							<income-input :id="uid('income')" v-model="inputIncome" required></income-input>&nbsp;€
							<button class="toggle" @click="toggleUseMonthlyIncome">per {{ monthOrYear }}</button>
						</div>
					</div>

					<div class="form-group">
						<span class="label">Work history</span>
						<yes-no-input :id="uid('isFirstJobInGermany')" v-model="isFirstJobInGermany" required>
							Is this your first job in Germany?
						</yes-no-input>
						<yes-no-input :id="uid('hasStartedWorking')" v-model="hasStartedWorking" required>
							Did you already start working?
						</yes-no-input>
					</div>

					<div class="form-group" v-if="hasStartedWorking === false">
						<span class="label">Start date</span>
						<div class="question-input">
							When do you start working?
							<date-picker
								:id="uid('job')"
								v-model="employmentStartDate"
								required></date-picker>
						</div>
					</div>
				</template>

				<hr>

				<h3>Current insurance</h3>

				<div class="form-group no-label">
					<yes-no-input
						:id="uid('hasCurrentGermanInsurance')"
						v-model="hasCurrentGermanInsurance"
						required>
						Are you already insured in Germany?
					</yes-no-input>
					<yes-no-input
						:id="uid('hasCurrentInsuranceAbroad')"
						v-if="hasCurrentGermanInsurance === false"
						v-model="hasCurrentInsuranceAbroad"
						required>
						Are you already insured in another country?
					</yes-no-input>
				</div>

				<div class="form-group" v-if="hasCurrentInsuranceAbroad === true">
					<label :for="uid('currentInsuranceCountry')">Country</label>
					<country-input
						country-code
						v-model="currentInsuranceCountry"
						:id="uid('currentInsuranceCountry')"
						required></country-input>
				</div>

				<div class="form-group" v-if="hasCurrentGermanInsurance === true">
					<span class="label">Insurance type</span>
					<div class="no-label" aria-label="Insurance type">
						<radio v-model="currentInsuranceType" value="public" required>
							<glossary term="gesetzliche Krankenversicherung">Public health insurance</glossary>
						</radio>
						<radio v-model="currentInsuranceType" value="private" required>
							<glossary term="private Krankenversicherung">Private health insurance</glossary>
						</radio>
						<radio v-model="currentInsuranceType" value="travelExpat" required>
							<span>Travel or <glossary term="Expat health insurance">expat health insurance</glossary></span>
						</radio>
					</div>
				</div>

				<div class="form-group" v-if="hasCurrentGermanInsurance === true || hasCurrentInsuranceAbroad === true">
					<label :for="uid('currentInsurerName')">Insurer name</label>
					<input
						type="text"
						:id="uid('currentInsurerName')"
						v-model="currentInsurerName"
						maxlength="25"
						placeholder="e.g. TK, AOK, DAK"
						required>
				</div>
			</template>

			<template v-if="stage === 'family'">
				<h2>Who are you insuring?</h2>
				<p>It's cheaper to insure your family together. Public health insurance can cover your spouse and your children for free.</p>
				<ul class="buttons grid" aria-label="Who are you insuring">
					<li>
						<label>
							<input type="checkbox" checked disabled>
							<icon-employee/>
							Me
						</label>
					</li>
					<li>
						<label>
							<input type="checkbox" v-model="insureSpouse">
							<icon-family/>
							My spouse
						</label>
					</li>
					<li>
						<label>
							<input type="checkbox" v-model="insureChildren">
							<icon-family/>
							My children
						</label>
					</li>
				</ul>
				<hr v-if="insureChildren">
				<div class="form-group no-label" v-if="insureChildren">
					<div class="question-input">
						<label :for="uid('childrenCount')">How many children do you have?</label>
						<children-input
							v-model="childrenCount"
							:id="uid('childrenCount')"
							required></children-input>
					</div>
				</div>
			</template>

			<template v-if="stage === 'personalDetails'">
				<h2>Personal details</h2>

				<div class="form-group">
					<span class="label">Gender</span>
					<tabs
						aria-label="Gender"
						v-model="gender"
						:id="uid('gender')"
						:options="[{label: 'Male', value: 'male'}, {label: 'Female', value: 'female'}, {label: 'Non-binary', value: 'non_binary'}, {label: 'Unspecified', value: 'unspecified'}]"
						required></tabs>
				</div>

				<div class="form-group" v-if="showExtraNameFields">
					<label :for="uid('title')">Title</label>
					<input
						type="text"
						:id="uid('title')"
						v-model="title"
						autocomplete="honorific-prefix"
						placeholder="Dr."
						class="anrede-input">
				</div>

				<div class="form-group">
					<label :for="uid('firstName')">First and last name</label>
					<div class="input-group">
						<first-name-input :id="uid('firstName')" v-model="firstName" required></first-name-input>
						<last-name-input v-model="lastName" required></last-name-input>
						<a
							class="input-instructions"
							href="#"
							v-if="!showExtraNameFields"
							@click.prevent="showExtraNameFields = true">Add a title or birth name</a>
					</div>
				</div>

				<div class="form-group" v-if="showExtraNameFields">
					<label :for="uid('birthName')">Name at birth</label>
					<input
						type="text"
						:id="uid('birthName')"
						v-model="birthName"
						placeholder="Alex Brown">
					<span class="input-instructions">If you changed your name, enter your full name at birth.</span>
				</div>

				<div class="form-group">
					<label :for="uid('nationality')">Nationality</label>
					<country-input
						country-code
						v-model="nationality"
						:id="uid('nationality')"
						required></country-input>
				</div>

				<hr>

				<div class="form-group">
					<label :for="uid('dateOfBirth')">Date of birth</label>
					<date-picker
						:id="uid('dateOfBirth')"
						v-model="dateOfBirth"
						autocomplete="bday"
						required></date-picker>
				</div>

				<div class="form-group">
					<label :for="uid('birthPlace')">Place of birth</label>
					<input
						type="text"
						:id="uid('birthPlace')"
						v-model="birthPlace"
						placeholder="Montreal"
						required>
				</div>

				<div class="form-group">
					<label :for="uid('birthCountry')">Country of birth</label>
					<country-input
						country-code
						v-model="birthCountry"
						:id="uid('birthCountry')"
						required></country-input>
				</div>

				<hr>

				<div class="form-group">
					<label :for="uid('street')">Street address</label>
					<div class="input-group">
						<input
							type="text"
							:id="uid('street')"
							v-model="street"
							placeholder="Neue Straße"
							autocomplete="address-line1"
							required>
						<input
							type="text"
							v-model="houseNumber"
							placeholder="123"
							required>
					</div>
				</div>

				<div class="form-group">
					<label :for="uid('buildingDetails')">Building details</label>
					<input
						type="text"
						:id="uid('buildingDetails')"
						v-model="buildingDetails"
						placeholder="Haus B, 2. Etage rechts"
						autocomplete="address-line2">
					<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#extra-information" target="_blank">How to write your building details</a>
				</div>

				<div class="form-group">
					<label :for="uid('postCode')">Post code and city</label>
					<div class="input-group">
						<postalcode-input :id="uid('postCode')" v-model="postCode" required></postalcode-input>
						<city-input v-model="city" required></city-input>
					</div>
				</div>

				<div class="form-group">
					<label :for="uid('country')">Country</label>
					<country-input
						country-code
						v-model="country"
						:id="uid('country')"
						required></country-input>
				</div>
			</template>

			<template v-if="stage === 'contactInfo'">
				<h2>Contact information</h2>

				<div class="form-group">
					<label :for="uid('email')">Email</label>
					<email-input :id="uid('email')" v-model="email" required></email-input>
				</div>

				<div class="form-group">
					<label :for="uid('phone')">Phone number</label>
					<input
						type="tel"
						:id="uid('phone')"
						v-model="phone"
						autocomplete="tel"
						placeholder="+49 30 12345678">
				</div>
			</template>

			<template v-if="stage === 'thank-you'">
				<h2>Thank you</h2>
				<p>We received your signup.</p>
			</template>

			<template v-if="stage === 'error'">
				<p><strong>An error occurred</strong> while sending your request. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
			</template>

			<template v-if="showContinueButton || showBackButton">
				<hr>
				<div class="buttons bar">
					<button v-if="showBackButton" class="button previous" @click="previousStage">Go back</button>
					<button v-if="showContinueButton" class="button primary next" @click="nextStage">Continue</button>
				</div>
			</template>
		</section>
	`,
};
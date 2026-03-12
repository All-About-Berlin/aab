import AgeInput from '/js/vue/components/age-input.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
import ChildrenInput from '/js/vue/components/children-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import ExpatHealthInsuranceOptions from '/js/vue/components/expat-health-insurance-options.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconEmployee from '/js/vue/components/icons/employee.mjs';
import IconFamily from '/js/vue/components/icons/family.mjs';
import IconFreelancer from '/js/vue/components/icons/freelancer.mjs';
import IconLeasure from '/js/vue/components/icons/leasure.mjs';
import IconMoving from '/js/vue/components/icons/moving.mjs';
import IconProtection from '/js/vue/components/icons/protection.mjs';
import IconStudent from '/js/vue/components/icons/student.mjs';
import IconSupport from '/js/vue/components/icons/support.mjs';
import IconWhatsapp from '/js/vue/components/icons/whatsapp.mjs';
import HealthInsuranceOptions from '/js/vue/components/health-insurance-options.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import PublicHealthInsuranceOptions from '/js/vue/components/public-health-insurance-options.mjs';
import PrivateHealthInsuranceOptions from '/js/vue/components/private-health-insurance-options.mjs';
import Radio from '/js/vue/components/radio.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

import brokerMixin from '/js/vue/mixins/broker.mjs';
import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import QRCode from '/js/libs/qrcode.mjs';
import { healthInsurance, occupations, pflegeversicherung } from '/js/utils/constants.mjs';
import { formatCurrency } from '/js/utils/currency.mjs';
import { getHealthInsuranceOptions } from '/js/utils/healthInsurance.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';

export default {
	components: {
		AgeInput,
		Checkbox,
		ChildrenInput,
		Collapsible,
		ExpatHealthInsuranceOptions,
		EmailInput,
		FullNameInput,
		Glossary,
		IconEmployee,
		IconFamily,
		IconFreelancer,
		IconLeasure,
		IconMoving,
		IconStudent,
		IconSupport,
		IconProtection,
		IconWhatsapp,
		HealthInsuranceOptions,
		IncomeInput,
		PublicHealthInsuranceOptions,
		PrivateHealthInsuranceOptions,
		Radio,
		Tabs,
	},
	mixins: [brokerMixin, multiStageMixin, uniqueIdsMixin, trackedStagesMixin],
	props: {
		static: Boolean,
		mode: {
			type: String,
			default: 'calculator',
		},
		initialOccupation: {
			type: String,
			default: null,
		},
	},
	data() {
		return {
			// Insurance questions
			age: null,
			childrenCount: null,
			inputIncome: null,
			occupation: null,
			isMarried: null,
			useMonthlyIncome: null,
			yearlyIncome: null,
			worksOver20HoursPerWeek: null,
			isApplyingForFirstVisa: null,
			hasGermanPublicHealthInsurance: null,
			hasEUPublicHealthInsurance: null,

			// Contact form
			contactMethod: null,
			fullName: '',
			email: '',
			question: '',
			isLoading: false,
			intent: 'other',

			// Component settings
			trackAs: `Health insurance ${this.mode}`,
			stages: this.mode === 'question' ? [
					'askABroker',
					'occupation',
					'questions',
					'thank-you',
					'error',
				] : [
					'occupation',
					'questions',
					'options',
					'publicOptions',
					'privateOptions',
					'expatOptions',
					'askABroker',
					'thank-you',
					'error',
				],

			pflegeversicherung,
			healthInsurance,
		};
	},
	mounted(){
		this.inputIncome = this.useMonthlyIncome ? this.monthlyIncome : this.yearlyIncome;
	},
	computed: {
		isStudent(){ return occupations.isStudent(this.occupation) },
		isSelfEmployed(){ return occupations.isSelfEmployed(this.occupation) },
		isUnemployed(){ return occupations.isUnemployed(this.occupation) },
		monthlyIncome(){ return this.yearlyIncome / 12 },
		progressBarLength(){ return this.stages.filter(s => !['publicOptions', 'privateOptions', 'expatOptions', 'thank-you', 'error'].includes(s)).length - 1 },
		progressBarValue(){ return Math.min(this.stageIndex, this.progressBarLength) },
		showProgressBar(){ return this.progressBarLength && this.progressBarValue < this.progressBarLength && this.stageIndex !== 0 && this.occupation !== 'other' },

		requireCompleteForm(){
			// When asking a question, the fields are only a suggestion
			return this.mode === 'calculator';
		},

		askForCurrentInsurance(){
			// Check if having EU/German public health insurance would change the recommendations
			const flagsWithoutPublicInsurance = getHealthInsuranceOptions({
				...this.calculatorParams,
				hasEUPublicHealthInsurance: false,
				hasGermanPublicHealthInsurance: false,
			}).flags;
			const flagsWithPublicInsurance = getHealthInsuranceOptions({
				...this.calculatorParams,
				hasEUPublicHealthInsurance: true,
				hasGermanPublicHealthInsurance: true,
			}).flags;

			return !(
				flagsWithoutPublicInsurance.size === flagsWithPublicInsurance.size
				&& [...flagsWithoutPublicInsurance].every(value => flagsWithPublicInsurance.has(value))
			)
		},

		// Insurance options
		calculatorParams(){
			return {
				age: this.age,
				childrenCount: this.childrenCount,
				hasGermanPublicHealthInsurance: !!this.hasGermanPublicHealthInsurance,
				hasEUPublicHealthInsurance: !!this.hasEUPublicHealthInsurance,
				hoursWorkedPerWeek: this.worksOver20HoursPerWeek ? 40 : 20,
				isApplyingForFirstVisa: !!this.isApplyingForFirstVisa,
				isMarried: this.isMarried,
				monthlyIncome: this.isUnemployed ? 0 : this.monthlyIncome,
				occupation: this.occupation,
				customZusatzbeitrag: null,
			};
		},
		showGuideLink(){
			// If you're on this page, you're already reading about health insurance
			return window.location.pathname !== '/guides/german-health-insurance';
		},

		// Contact form
		personSummary(){
			if(!this.occupation){
				// User has clicked "skip the questions"
				return '';
			}

			const facts = [];

			if(this.age){
				facts.push(`I am ${this.age} years old`);
			}

			const cleanOccupation = {
				azubi: 'an apprentice',
				employee: 'employed',
				selfEmployed: 'self-employed',
				studentEmployee: 'a student',
				studentSelfEmployed: 'a self-employed student',
				studentUnemployed: 'an unemployed student',
				unemployed: 'unemployed',
			}[this.occupation];
			if(cleanOccupation){
				facts.push(`I am ${cleanOccupation}`);
			}
			if(this.isStudent){
				facts.push(`I work ${this.worksOver20HoursPerWeek ? 'more' : 'less'} than 20 hours per week`);
			}
			if(this.yearlyIncome != null && !this.isUnemployed && this.occupation !== 'other'){
				facts.push(`I earn ${formatCurrency(this.yearlyIncome)} per year`);
			}
			if(this.isApplyingForFirstVisa != null){
				facts.push('I am applying for my first visa');
			}
			if(this.isMarried != null){
				facts.push(`I am ${this.isMarried ? '' : 'not '}married`);
			}

			if(this.childrenCount != null){
				if(+this.childrenCount === 0){
					facts.push(`I don't have children`);
				}
				else{
					facts.push(`I have ${this.childrenCount} ${this.childOrChildren}`);
				}
			}

			if(this.hasGermanPublicHealthInsurance != null){
				facts.push(`I have German public health insurance`);
			}
			else if(this.hasEUPublicHealthInsurance != null){
				facts.push(`I have public health insurance in another EU country`);
			}

			return (new Intl.ListFormat('en-US', {style: 'long', type: 'conjunction'}).format(facts)) + '.';
		},
		intentString(){
			return {
				private: 'choose private health insurance',
				expat: 'choose expat health insurance',
			}[this.intent] || 'choose the best health insurance'
		},
		whatsappMessage(){
			return `Hi ${this.broker.name}, I am ${this.fullName}. Can you help me ${this.intentString}? ${this.personSummary}`;
		},
		whatsappUrl(){
			return `https://wa.me/${this.broker.phoneNumber}?text=${encodeURIComponent(this.whatsappMessage)}`;
		},
		qrCode(){
			var qrcode = new QRCode({
				content: `https://wa.me/${this.broker.phoneNumber}`,
				width: 150,
				height: 150,
				padding: 0,
				color: 'currentColor',
				background: 'transparent',
				ecl: "L",
				join: true,
				pretty: false,
				container: 'none',
			});
			return qrcode.svg();
		},

		// Printed values
		salaryOrIncome(){ return occupations.salaryOrIncome(this.occupation) === 'salary' ? 'Salary' : 'Income' },
		childOrChildren(){ return this.childrenCount === 1 ? 'child' : 'children' },

		trackedStagesExtraData() {
			const data = {
				partner: this.broker.id,
			};
			if(this.contactMethod){
				data.contactMethod = this.contactMethod;
			}
			return data;
		},
	},
	methods: {
		goBackFromAskABroker(){
			if(this.occupation === 'other'){
				this.goToStage('occupation');
			}
			else{
				this.goToStage('options');
			}
		},

		// Insurance questions
		selectOccupation(occupation){
			this.occupation = occupation;

			if(this.mode === 'question'){
				this.stages = [
					'askABroker',
					'occupation',
					'questions',
					'thank-you',
					'error',
				];
			}
			else if (occupation === 'other'){
				this.stages = [
					'occupation',
					'askABroker',
					'thank-you',
					'error',
				]
			}
			else{
				this.stages = [
					'occupation',
					'questions',
					'options',
					'publicOptions',
					'privateOptions',
					'expatOptions',
					'askABroker',
					'thank-you',
					'error',
				];
			}
			this.nextStage();
		},

		// Insurance options
		selectOption(option){
			if(option === 'askABroker'){
				this.intent = {
					expatOptions: 'expat',
					privateOptions: 'private',
				}[this.stage] || 'other';

				this.goToStage('askABroker');
			}
			else if(option.endsWith('Options')){
				this.goToStage(option);
			}
		},

		// Contact form
		async createCase(event){
			if(validateForm(this.$el)){
				this.isLoading = true;
				const response = await fetch(
					'/api/insurance/case',
					{
						method: 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8'},
						body: JSON.stringify({
							email: this.email || '',
							question: this.question || '',
							name: this.fullName,
							income: this.isUnemployed ? 0 : this.yearlyIncome,
							occupation: this.occupation || 'other',
							age: this.age,
							children_count: this.childrenCount == null ? null : +this.childrenCount,

							// null if the questions can be skipped, false if they were deliberately set to false
							is_married: this.requireCompleteForm ? !!this.isMarried : this.isMarried,
							is_applying_for_first_visa: this.requireCompleteForm ? !!this.isApplyingForFirstVisa : this.isApplyingForFirstVisa,
							has_eu_public_insurance: this.requireCompleteForm ? !!this.hasEUPublicHealthInsurance: this.hasEUPublicHealthInsurance,
							has_german_public_insurance: this.requireCompleteForm ? !!this.hasGermanPublicHealthInsurance: this.hasGermanPublicHealthInsurance,

							referrer: getReferrer() || '',
							contact_method: this.contactMethod || 'EMAIL',
							broker: this.broker.id,
						}),
					},
				);
				this.isLoading = false;

				if(response.ok){
					this.goToStage('thank-you');
				}
				else{
					this.goToStage('error');
				}
			}
			else{
				// Don't open Whatsapp
				event.preventDefault();
				return;
			}
		},
	},
	watch: {
		inputIncome(newIncome){
			this.yearlyIncome = this.useMonthlyIncome ? newIncome * 12 : newIncome;
		},
		useMonthlyIncome(monthly){
			this.yearlyIncome = monthly ? this.inputIncome * 12 : this.inputIncome;
		},
	},
	template: `
		<collapsible
			class="health-insurance-calculator"
			:aria-label="trackAs"
			:data-stage="stage"
			:static="static">
			<template v-slot:header>
				<template v-if="mode === 'question'">Ask our<span class="no-mobile"> health</span> insurance expert</template>
				<template v-else>Health insurance calculator</template>
			</template>

			<progress v-if="showProgressBar" aria-label="Form progress" :value="progressBarValue" :max="progressBarLength"></progress>

			<template v-if="stage === 'occupation' && initialOccupation">
				<p v-if="initialOccupation === 'studentUnemployed'">This tool helps you <strong>find student health insurance</strong> in a few seconds.</p>
				<p v-else-if="initialOccupation === 'selfEmployed'">This tool helps you <strong>find the best health insurance</strong> for freelancers in a few seconds.</p>
				<p v-else>This tool helps you <strong>find the best health insurance</strong> in a few seconds.</p>
				<hr>
				<ul class="benefits">
					<li v-if="initialOccupation !== 'employee'">
						<icon-protection/>
						<div>
							<strong>Low price, great coverage</strong>
							<br>Find affordable health insurance that works when you need it.
						</div>
					</li>
					<li v-if="initialOccupation === 'employee'">
						<icon-family/>
						<div>
							<strong>For you and your family</strong>
							<br>Find health insurance that covers your spouse and your children.
						</div>
					</li>
					<li v-if="initialOccupation === 'employee'">
						<icon-employee/>
						<div>
							<strong>Perfect for your visa <span class="no-mobile">application</span></strong>
							<br>Get the right insurance for your work visa, Blue Card or Chancenkarte.
						</div>
					</li>
					<li v-if="initialOccupation === 'studentUnemployed'">
						<icon-moving/>
						<div>
							<strong>Perfect for a student visa</strong>
							<br>Get the right insurance for your National Visa application.
						</div>
					</li>
					<li v-if="initialOccupation === 'selfEmployed'">
						<icon-moving/>
						<div>
							<strong>Perfect for your <span class="no-mobile">freelance</span> visa</strong>
							<br>Get insurance that's accepted by the immigration office.
						</div>
					</li>
					<li>
						<icon-support/>
						<div>
							<strong>Free expert advice</strong>
							<br>Ask our insurance expert anything on WhatsApp.
						</div>
					</li>
				</ul>
				<hr>
				<div class="buttons bar">
					<button :data-occupation="initialOccupation" class="button primary" @click="selectOccupation(initialOccupation)">Find health insurance <i class="icon right"></i></button>
				</div>
			</template>

			<template v-if="stage === 'occupation' && !initialOccupation">
				<p v-if="mode === 'calculator'"><strong>Let's find the right health insurance.</strong> What is your occupation?</p>
				<template v-if="mode === 'question'">
					<h3>What is your occupation?</h3>
					<p>Your health insurance options depend on what you do.</p>
				</template>
				<ul class="buttons grid" aria-label="Occupations">
					<li>
						<button data-occupation="employee" @click="selectOccupation('employee')">
							<icon-employee/>
							Employee
						</button>
					</li>
					<li>
						<button data-occupation="studentUnemployed" @click="selectOccupation('studentUnemployed')">
							<icon-student/>
							Student
						</button>
					</li>
					<li>
						<button data-occupation="selfEmployed" @click="selectOccupation('selfEmployed')">
							<icon-freelancer/>
							Self-employed
						</button>
					</li>
					<li>
						<button data-occupation="azubi" @click="selectOccupation('azubi')">
							<icon-support/>
							Apprentice
						</button>
					</li>
					<li>
						<button data-occupation="unemployed" @click="selectOccupation('unemployed')">
							<icon-leasure/>
							Unemployed
						</button>
					</li>
					<li>
						<button data-occupation="other" @click="selectOccupation('other')">
							<icon-family/>
							It's complicated
						</button>
					</li>
				</ul>
				<template v-if="mode === 'question'">
					<hr>
					<div class="buttons bar">
						<button aria-label="Go back" class="button" @click="previousStage()">
							<i class="icon left" aria-hidden="true"></i> <span class="no-mobile">Go back</span>
						</button>
						<button class="button" @click="occupation = null; createCase()">
							Skip the questions <i class="icon right" aria-hidden="true"></i>
						</button>
					</div>
				</template>
			</template>

			<template v-if="stage === 'questions'">
				<h2>Tell us a bit more about you&hellip;</h2>
				<p v-if="mode === 'question'">You can skip this step, but this information helps {{ broker.name }} recommend the right health insurance.</p>
				<p v-else>It helps us calculate prices and recommend the right health insurance.</p>
				<hr>
				<div class="form-group">
					<label :for="uid('age')">
						Age
					</label>
					<div class="input-group">
						<age-input
							ref="ageInput"
							:id="uid('age')"
							v-model="age"
							:required="requireCompleteForm"></age-input>
						years old
					</div>
				</div>
				<div class="form-group">
					<span class="label">
						Spouse
					</span>
					<tabs
						aria-label="Are you married?"
						v-model="isMarried"
						:id="uid('isMarried')"
						:options="[{label: 'Married', value: true}, {label: 'Not married', value: false}]"
						:required="requireCompleteForm"></tabs>
				</div>
				<div class="form-group">
					<label :for="uid('childrenCount')">
						Children
					</label>
					<children-input
						v-model="childrenCount"
						:id="uid('childrenCount')"
						:required="requireCompleteForm"></children-input>
				</div>
				<div class="form-group" v-if="isStudent">
					<span class="label">
						Other occupation
					</span>
					<radio
						v-model="occupation"
						value="studentUnemployed"
						:required="requireCompleteForm">
						I am unemployed
					</radio>
					<radio
						v-model="occupation"
						value="studentEmployee"
						:required="requireCompleteForm">
						I have a job
					</radio>
					<radio
						v-model="occupation"
						value="studentSelfEmployed"
						:required="requireCompleteForm">
						I am self-employed
					</radio>
				</div>
				<div class="form-group" v-if="!isUnemployed">
					<label :for="uid('income')" v-text="salaryOrIncome"></label>
					<div class="input-group">
						<income-input
							:id="uid('income')"
							v-model="inputIncome"
							:required="requireCompleteForm"></income-input>&nbsp;€
						<button class="toggle" @click="useMonthlyIncome = !useMonthlyIncome">per {{ useMonthlyIncome ? 'month' : 'year' }}</button>
						<span class="no-mobile">before taxes</span>
					</div>
					<checkbox v-model="worksOver20HoursPerWeek" v-if="occupation === 'studentEmployee'">
						I work more than 20 hours per week
					</checkbox>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('isApplyingForFirstVisa')">
						Immigration
					</label>
					<checkbox :id="uid('isApplyingForFirstVisa')" v-model="isApplyingForFirstVisa">
						<div>
							I am applying for a <glossary>National Visa</glossary> to move to Germany
						</div>
					</checkbox>
				</div>
				<hr v-if="askForCurrentInsurance">
				<div class="form-group" v-if="askForCurrentInsurance">
					<span class="label">
						Current insurance
					</span>
					<checkbox v-model="hasGermanPublicHealthInsurance">
						<div>I have <glossary term="gesetzliche Krankenversicherung">public health insurance</glossary> in Germany</div>
					</checkbox>
					<checkbox v-model="hasEUPublicHealthInsurance">
						<div>I have public health insurance in another <glossary term="European Union">EU</glossary> country</div>
					</checkbox>
				</div>
				<hr>
				<div class="buttons bar">
					<template v-if="mode === 'calculator'">
						<button aria-label="Go back" class="button" @click="goToStart()">
							<i class="icon left" aria-hidden="true"></i> <span class="no-mobile">Go back</span>
						</button>
						<button class="button primary" @click="nextStage()">
							See options <i class="icon right" aria-hidden="true"></i>
						</button>
					</template>

					<template v-if="mode === 'question'">
						<button aria-label="Go back" class="button" @click="goToStart()">
							<i class="icon left" aria-hidden="true"></i> <span :class="{'no-mobile': !!contactMethod}">Go back</span>
						</button>
						<button v-if="contactMethod === 'EMAIL'" class="button primary" @click="createCase" :disabled="isLoading" :class="{loading: isLoading}">
							Ask {{ broker.name }}
						</button>
						<a v-if="contactMethod === 'WHATSAPP'" :href="whatsappUrl" @click="createCase" class="button whatsapp" :disabled="isLoading" target="_blank">
							<icon-whatsapp/>
							<span class="only-mobile">Start chat</span>
							<span class="no-mobile">Chat with {{ broker.name }}</span>
						</a>
					</template>
				</div>
			</template>

			<health-insurance-options v-if="stage === 'options'" v-bind="calculatorParams" @select="selectOption"></health-insurance-options>
			<public-health-insurance-options v-if="stage === 'publicOptions'" @select="selectOption" v-bind="calculatorParams"></public-health-insurance-options>
			<private-health-insurance-options v-if="stage === 'privateOptions'" @select="selectOption" v-bind="calculatorParams"></private-health-insurance-options>
			<expat-health-insurance-options v-if="stage === 'expatOptions'" @select="selectOption" v-bind="calculatorParams"></expat-health-insurance-options>

			<template v-if="stage === 'options' || stage === 'publicOptions' || stage === 'expatOptions'">
				<hr>
				<h3>Need help choosing?</h3>
				<ul class="buttons list">
					<li>
						<button class="recommended" @click="selectOption('askABroker')" :aria-labelledby="uid('h-askOurExpert')">
							<icon-support/>
							<div>
								<h3 :id="uid('h-askOurExpert')">Ask our expert</h3>
								<p>Let {{ broker.name }} find the best health insurance for you. It's 100% free.</p>
							</div>
						</button>
					</li>
					<li v-if="showGuideLink" :aria-labelledby="uid('h-readGuide')">
						<a href="/guides/german-health-insurance" @click="selectOption('guide')" target="_blank">
							<icon-student/>
							<div>
								<h3 :id="uid('h-readGuide')">Learn how to choose</h3>
								<p>Read my health insurance guide and make an informed decision.</p>
							</div>
						</a>
					</li>
				</ul>
			</template>

			<div class="buttons bar" v-if="stage === 'options' || stage.endsWith('Options')">
				<button aria-label="Go back" class="button" @click="stage === 'options' ? previousStage() : goToStage('options')">
					<i class="icon left" aria-hidden="true"></i> <span :class="{'no-mobile': stage === 'privateOptions'}">Go back</span>
				</button>
				<button v-if="stage === 'privateOptions'" class="button primary" @click="selectOption('askABroker')">
					Get insured <i class="icon right" aria-hidden="true"></i>
				</button>
			</div>

			<template v-if="stage === 'askABroker'">
				<div class="form-recipient">
					<div>
						<p v-if="occupation === 'other'">If your situation is complicated, let our expert help you.</p>
						<p>{{ broker.name }} will help you <strong v-text="intentString">choose the best health insurance</strong>. I work with {{ broker.him }} because {{ broker.he }} is honest and knowledgeable.</p>
						<p>{{ capitalize(broker.he) }} replies on the same day. {{ capitalize(broker.his) }} help is <strong>100% free</strong>.</p>
					</div>
					<img
						:srcset="'/experts/photos/bioLarge1x/' + broker.id + '.jpg, /experts/photos/bioLarge2x/' + broker.id + '.jpg 2x'"
						:alt="broker.fullName" width="125" height="125"
						sizes="125px">
				</div>
				<hr>
				<div class="contact-method">
					<h3>How should we talk?</h3>
					<tabs
						aria-label="Preferred contact method"
						v-model="contactMethod"
						:id="uid('contactMethod')"
						:options="[{label: 'WhatsApp', value: 'WHATSAPP'}, {label: 'Email', value: 'EMAIL'}]"></tabs>
				</div>
				<template v-if="contactMethod">
					<hr>
					<div class="form-group">
						<label :for="uid('fullName')">
							Your name
						</label>
						<full-name-input
							:id="uid('fullName')"
							v-model="fullName"
							required></full-name-input>
					</div>
					<div class="form-group" v-if="contactMethod === 'EMAIL'">
						<label :for="uid('email')">
							Email address
						</label>
						<email-input
							v-model="email"
							:id="uid('email')"
							required></email-input>
					</div>
					<template v-if="contactMethod !== 'WHATSAPP'">
						<hr>
						<div class="form-group">
							<label :for="uid('question')">
								Your question
							</label>
							<textarea :id="uid('question')" v-model="question" :placeholder="'How can ' + broker.name + ' help you?'" :required="occupation === 'other'"></textarea>
						</div>
					</template>
				</template>
				<template v-if="contactMethod || mode === 'calculator'">
					<hr>
					<div class="buttons bar">
						<button v-if="stageIndex > 0" aria-label="Go back" class="button" @click="goBackFromAskABroker()">
							<i class="icon left" aria-hidden="true"></i> <span class="no-mobile">Go back</span>
						</button>
						<button v-if="mode === 'question'" class="button primary" @click="nextStage()">
							Continue <i class="icon right" aria-hidden="true"></i>
						</button>
						<button v-if="mode === 'calculator' && contactMethod === 'EMAIL'" class="button primary" @click="createCase" :disabled="isLoading" :class="{loading: isLoading}">
							Ask {{ broker.name }}
						</button>
						<a v-if="mode === 'calculator' && contactMethod === 'WHATSAPP'" :href="whatsappUrl" @click="createCase" class="button whatsapp" :disabled="isLoading" target="_blank">
							<icon-whatsapp/>
							<span class="only-mobile">Start chat</span>
							<span class="no-mobile">Chat with {{ broker.name }}</span>
						</a>
					</div>
				</template>
			</template>

			<template v-if="stage === 'thank-you' && contactMethod === 'WHATSAPP'">
				<div class="form-recipient">
					<div>
						<p>
							To chat with {{ broker.name }}, <a :href="whatsappUrl" target="_blank">open WhatsApp</a> <span class="no-mobile">or scan this QR code</span>.
						</p>
						<p>
							{{ capitalize(broker.his) }} number is <strong class="selectable">{{ broker.phoneNumberPretty }}</strong>.
						</p>
					</div>
					<svg class="no-mobile" v-html="qrCode" xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 150 150"></svg>
				</div>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button" @click="goToStart()">
						<i class="icon left" aria-hidden="true"></i> <span class="no-mobile">Go back</span>
					</button>
					<a :href="whatsappUrl" class="button whatsapp" target="_blank">
						<icon-whatsapp/>
						Open WhatsApp
					</a>
				</div>
			</template>

			<template v-if="stage === 'thank-you' && contactMethod === 'EMAIL'">
				<p><strong>Thank you!</strong> {{ broker.name }} got your message. {{ capitalize(broker.he) }} will answer your question in the next 24 hours.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button" @click="goToStart()">
						<i class="icon left" aria-hidden="true"></i> Go back
					</button>
				</div>
			</template>

			<template v-if="stage === 'error'">
				<p><strong>An error occurred</strong> while sending your question. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button" @click="goToStart()">
						<i class="icon left" aria-hidden="true"></i> Go back
					</button>
				</div>
			</template>
		</collapsible>
	`,
}
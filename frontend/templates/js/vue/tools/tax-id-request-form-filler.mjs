import Checkbox from '/js/vue/components/checkbox.mjs';
import CityInput from '/js/vue/components/city-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconMail from '/js/vue/components/icons/mail.mjs';
import IconPdf from '/js/vue/components/icons/pdf.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import PostalcodeInput from '/js/vue/components/postalcode-input.mjs';
import Radio from '/js/vue/components/radio.mjs';
import Recommended from '/js/vue/components/recommended.mjs';
import StateInput from '/js/vue/components/state-input.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import preloadPdfMixin from '/js/vue/mixins/preloadPdf.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { countriesInGerman } from '/js/utils/countries.mjs';
import { germanStateNames } from '/js/utils/germanStates.mjs';
import { mergeFields } from '/js/utils/letter.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { getNearestHeadingId } from '/js/utils/tracking.mjs';
import { fillAndSavePDF } from '/js/utils/pdf.mjs';

export default {
	components: {
		Checkbox,
		CityInput,
		Collapsible,
		CountryInput,
		DatePicker,
		EmailInput,
		FirstNameInput,
		Glossary,
		IconDonate,
		IconMail,
		IconPdf,
		LastNameInput,
		PostalcodeInput,
		Radio,
		Recommended,
		StateInput,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, multiStageMixin, trackedStagesMixin, preloadPdfMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			trackAs: 'Tax ID request form',

			purpose: null,
			address: '',
			foreignCityAndPostCode: '',
			germanCity: '',
			germanPostCode: '',
			germanState: userDefaults.empty,
			country: '',
			people: [],
			namesAreOnMailbox: true,
			nameOnMailbox: '',

			sendToEmployer: false,
			employerName: '',
			employerAddress: '',
			employerCity: '',
			employerPostCode: '',
			employerState: '',
			email: userDefaults.empty,

			stages: [
				'start',
				'purpose',
				'address',
				'addPeople',
				'beiAddress',
				'employer',
				'feedback',
				'options',
			],
			inputsToFocus: {
				start: () => this.$refs.startButton,
				address: () => this.country === 'DE' ? this.$refs.addressInput : this.$refs.countryInput.$el,
				addPeople: () => this.$refs.firstNameInput[0].$el,
				beiAddress: () => this.$refs.namesAreOnMailboxCheckbox.$el.querySelector('input'),
				employer: () => this.$refs.sendToEmployerCheckbox.$el.querySelector('input'),
				feedback: () => this.$refs.emailInput.$el,
			},
			downloadInProgress: false,
			feedbackReminderSent: false,
			pdfUrl: '/documents/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.pdf',
		};
	},
	methods: {
		nextStage(){
			if(validateForm(this.$el)){
				if(this.country !== 'DE' && this.stages[this.stageIndex + 1] === 'beiAddress'){
					this.stageIndex += 2; // Skip beiAddress for foreign addresses
				}
				else{
					this.stageIndex += 1;
				}
			}
		},
		addPerson(){
			this.people.push({
				id: Math.floor(Math.random() * 10000),
				firstName: '',
				lastName: '',
				birthName: '',
				dateOfBirth: '',
				birthPlace: '',
				showExtraFields: false,
			})
		},
		personName(person, index){
			if(person.firstName || person.lastName){
				return [person.firstName, person.lastName].filter(Boolean).join(' ');
			}
			return `person #${index}`;
		},
		async generatePDF(person){
			this.downloadInProgress = true;
			const beiAddress = (this.namesAreOnMailbox || this.country !== 'DE') ? '' : `(bei ${this.nameOnMailbox})`;

			const textFields = {
				lastName: [
					person.lastName,
					person.birthName ? `(geb. ${person.birthName})` : null,
				].join(' '),
				firstName: person.firstName,
				placeOfBirth: person.birthPlace,
				dateOfBirthDay: person.dateOfBirth.substring(8, 10).split('').join(' '), // A space between characters align them with the form field
				dateOfBirthMonth: person.dateOfBirth.substring(5, 7).split('').join(' '),
				dateOfBirthYear: person.dateOfBirth.substring(0, 4),
				reasonForIssuance: {
					noAnmeldung: 'Kürzlich nach Deutschland gezogen. Wohnsitzanmeldung derzeit nicht möglich.',
					abroad: 'Grenzarbeiter. Kein Wohnsitz in Deutschland.',
				}[this.purpose],
				placeAndDate: mergeFields([
					this.germanCity || this.employerCity || null,
					(new Date()).toLocaleDateString("de-DE"),
				]),
			};

			if(this.sendToEmployer){
				textFields.deliveryName = textFields.nameAndTaxNumberOfEmployer = this.employerName;
				textFields.deliveryAddress = textFields.employerAddress = mergeFields([
					this.employerAddress,
					[this.employerPostCode, this.employerCity].join(' '),
					this.employerState,
				]);

			}
			else if(this.country === 'DE'){
				textFields.deliveryName = [person.firstName, person.lastName, beiAddress].join(' ');
				textFields.deliveryAddress = mergeFields([
					this.address,
					[this.germanPostCode, this.germanCity].join(' '),
					countriesInGerman[this.country]
				]);
			}
			else{
				textFields.deliveryName = [person.firstName, person.lastName, beiAddress].join(' ');
				textFields.deliveryAddress = mergeFields([
					this.address,
					this.foreignCityAndPostCode,
					countriesInGerman[this.country]
				]);
			}

			if(this.country === 'DE'){
				textFields.germanAddress1 = [this.address, beiAddress].join(' ');
				textFields.germanAddress2 = mergeFields([
					[this.germanPostCode, this.germanCity].join(' '),
					germanStateNames[this.germanState].de
				]);
				textFields.foreignAddress1 = 'Nicht zutreffend';
				textFields.foreignAddress2 = 'Nicht zutreffend';
			}
			else {
				textFields.foreignAddress1 = [this.address, beiAddress].join(' ');
				textFields.foreignAddress2 = mergeFields([this.foreignCityAndPostCode, countriesInGerman[this.country]]);
				textFields.germanAddress1 = 'Nicht zutreffend';
				textFields.germanAddress2 = 'Nicht zutreffend';
			}

			const checkboxFields = {
				reasonIsEmployer: true,
				purposeIsLohnsteuerabzug: true,
			};
			const radioFields = {
				isInGermany: this.country === 'DE' ? 'Ja' : 'Nein',
			}

			await fillAndSavePDF(this.pdfUrl, textFields, checkboxFields, radioFields, 'tax-id-form-filled.pdf', this.trackAs, getNearestHeadingId(this.$el));
			this.downloadInProgress = false;

			if(this.email && !this.feedbackReminderSent){
				this.feedbackReminderSent = true;
				fetch(
					'/api/forms/tax-id-request-feedback-reminder',
					{
						method: 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8',},
						body: JSON.stringify({
							name: [person.firstName, person.lastName].join(' '),
							email: this.email,
						}),
					}
				);
			}
		}
	},
	watch: {
		purpose(newPurpose){
			if(newPurpose === 'noAnmeldung'){
				this.country = 'DE';
			}
			else if(newPurpose === 'abroad' && this.country === 'DE'){
				this.country = '';
			}
		}
	},
	created() {
		this.addPerson();
	},
	template: `
		<collapsible
			aria-description="Fill this form to request a German tax ID from the Finanzamt"
			aria-label="Tax ID request form"
			class="tax-id-form"
			:static="static">
			<template v-slot:header>
				<small>Fill the form online</small>
				Request a new tax ID
			</template>
			<progress v-if="stage !== 'start'" aria-label="Form progress" :max="stages.length - 1" :value="stageIndex"></progress>
			<template v-if="stage === 'start'">
				<picture>
					<source srcset="/documents/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.webp 1600w, /documents/previews/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.webp 300w, /documents/previews2x/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.webp 600w" type="image/webp">
					<source srcset="/documents/previews/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.png 300w, /documents/previews2x/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.png 600w" type="image/png">
					<img alt="German tax ID application form" loading="lazy" src="/documents/previews/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.png">
				</picture>
				<p>This tool helps you request a new <glossary term="Steueridentifikationsnummer">tax ID</glossary>.</p>
				<p>You normally get a tax ID when you <glossary term="Anmeldung">register your address</glossary> for the first time. <strong>Only use this form if you can't register your address.</strong></p>
			</template>
			<template v-if="stage === 'purpose'">
				<h2>What is your situation?</h2>
				<hr>
				<div class="form-group no-label" aria-label="What is your situation?">
					<radio v-model="purpose" value="noAnmeldung" required>
						I can't register my address, but I need a tax ID
					</radio>
					<radio v-model="purpose" value="abroad" required>
						I don't live in Germany, but I need a tax ID
					</radio>
					<radio v-model="purpose" value="business" required>
						I have a business, and I need a tax number or a VAT number
					</radio>
					<radio v-model="purpose" value="forgot" required>
						I forgot my tax ID
					</radio>
					<radio v-model="purpose" value="other" required>
						Something else
					</radio>
				</div>
				<template v-if="purpose === 'noAnmeldung'">
					<hr>
					<p>
						This tool helps you fill <a href="/documents/010250-Antrag-auf-Vergabe-einer-steuerlichen-Identifikationsnummer-für-nicht-meldepflichtige-Personen-durch-das-Finanzamt-Deutsch.pdf" target="_blank">form 010250</a>. That form is not designed for your situation, but it usually works anyway. It's the only way to get a tax ID without <glossary term="Anmeldung">registering your address</glossary>.
					</p>
				</template>
				<template v-if="purpose === 'business'">
					<hr>
					<p>
						This form is not for you. The <glossary term="Steueridentifikationsnummer">tax ID</glossary>, the <glossary term="Steuernummer">tax number</glossary> and the <glossary term="Umsatzsteuernummer">VAT number</glossary> are different things.
					</p>
					<p>
						<strong><a class="internal-link" href="/guides/german-tax-id-steuernummer#how-to-get-a-steuernummer" target="_blank">How to get a tax number</a></strong>
					</p>
					<p>
						<strong><a class="internal-link" href="/guides/german-tax-id-steuernummer#how-to-get-a-german-vat-number" target="_blank">How to get a VAT number</a></strong>
					</p>
				</template>
				<template v-if="purpose === 'forgot'">
					<hr>
					<p>
						If you already have a tax ID, this form is not for you.
					</p>
					<p>
						<strong><a class="internal-link" href="/guides/german-tax-id-steuernummer#where-to-find-your-tax-id" target="_blank">How to find your tax ID</a></strong>
					</p>
				</template>
				<template v-if="purpose === 'other'">
					<hr>
					<p>
						You probably don't need this form to get a tax ID. You normally get a tax ID when you <glossary term="Anmeldung">register your address</glossary> for the first time.
					</p>
					<p>
						<strong><a class="internal-link" href="/guides/german-tax-id-steuernummer#how-to-get-your-tax-id" target="_blank">How to get a tax ID</a></strong>
					</p>
				</template>
			</template>
			<template v-if="stage === 'address'">
				<h2>Your address in Germany</h2>
				<hr>
				<div class="form-group" v-if="purpose !== 'noAnmeldung'">
					<label :for="uid('country')">Country</label>
					<country-input ref="countryInput" country-code v-model="country" :id="uid('country')" exclude-germany required></country-input>
				</div>
				<div class="form-group">
					<label :for="uid('address')">Street address</label>
					<input
						:id="uid('address')"
						type="text"
						ref="addressInput"
						v-model="address"
						:placeholder="country === 'DE' ? 'Berliner Str. 123' : '123 Maple Street, Apt. 102'"
						autocomplete="address-line1"
						required>
				</div>
				<div v-if="country === 'DE'" class="form-group">
					<label :for="uid('postCode')"><glossary term="Postleitzahl">Post code</glossary> and city</label>
					<div class="input-group">
						<postalcode-input :id="uid('postCode')" v-model="germanPostCode" required></postalcode-input>
						<city-input v-model="germanCity" required></city-input>
					</div>
				</div>
				<div v-if="country !== 'DE'" class="form-group">
					<label :for="uid('foreignCityAndPostCode')">City and post code</label>
					<input
						:id="uid('foreignCityAndPostCode')"
						placeholder="Montreal, Quebec, H3E 1J4"
						type="text"
						v-model="foreignCityAndPostCode"
						autocomplete="address-level2"
						required>
				</div>
				<div class="form-group" v-if="country === 'DE'">
					<label :for="uid('germanState')">State</label>
					<state-input :id="uid('germanState')" v-model="germanState" required></state-input>
				</div>
			</template>
			<template v-if="stage === 'addPeople'">
				<h2>Who needs a tax ID?</h2>
				<template v-for="(person, index) in people">
					<hr>
					<div class="form-group">
						<label :for="uid('firstName-' + person.id)">First and last name</label>
						<div class="input-group">
							<first-name-input
								:id="uid('firstName-' + person.id)"
								v-model="person.firstName"
								ref="firstNameInput"
								required></first-name-input>
							<last-name-input
								v-model="person.lastName"
								required></last-name-input>
							<a class="input-instructions" href="#" v-if="!person.showExtraFields" @click.prevent="person.showExtraFields = true">Add a title or birth name</a>
						</div>
					</div>
					<div class="form-group" v-if="person.showExtraFields">
						<label :for="uid('birthName-' + person.id)">Name at birth</label>
						<input
							type="text"
							v-model="person.birthName"
							:id="uid('birthName-' + person.id)"
							:aria-describedby="uid('birthName-instructions-' + person.id)"
							placeholder="Alex Brown">
						<span class="input-instructions" :id="uid('birthName-instructions-' + person.id)">If you changed your name, enter your full name at birth.</span>
					</div>
					<div class="form-group">
						<label :for="uid('dateOfBirth-' + person.id)">Date of birth</label>
						<date-picker
							:key="person.id"
							:id="uid('dateOfBirth-' + person.id)"
							v-model="person.dateOfBirth"
							autocomplete="bday"
							required></date-picker>
					</div>
					<div class="form-group">
						<label :for="uid('birthPlace-' + person.id)">Place of birth</label>
						<input
							type="text"
							v-model="person.birthPlace"
							:id="uid('birthPlace-' + person.id)"
							:aria-describedby="uid('birthPlace-instructions-' + person.id)"
							placeholder="Montreal, Quebec, Canada"
							required>
						<span class="input-instructions" :id="uid('birthPlace-instructions-' + person.id)">The city, region and country where you were born.</span>
					</div>
				</template>
			</template>
			<template v-if="stage === 'beiAddress'">
				<h2>{{ people.length > 1 ? 'Are your names' : 'Is your name' }} on your mailbox?</h2>
				<p>German apartments don't have door numbers. If your name is not on your mailbox, you will not receive your mail.</p>
				<hr>
				<checkbox ref="namesAreOnMailboxCheckbox" v-model="namesAreOnMailbox">
					{{ people.length > 1 ? 'Our names are on our mailbox' : 'My name is on my mailbox' }}
				</checkbox>
				<p v-if="!namesAreOnMailbox">If your name is not on your mailbox, you must <a href="/guides/anmeldung-in-english-berlin#if-your-name-is-not-on-your-mailbox" target="_blank">add “c/o” or “bei” to your address</a>. This tells postal workers to put your mail in another person's mailbox.</p>
				<div class="form-group" v-if="!namesAreOnMailbox">
					<label :for="uid('nameOnMailbox')">Name on mailbox</label>
					<input :id="uid('nameOnMailbox')" type="text" v-model="nameOnMailbox" placeholder="Max Mustermann" required>
				</div>
			</template>
			<template v-if="stage === 'employer'">
				<h2>Send your tax ID to your employer</h2>
				<p>The <glossary>Finanzamt</glossary> can send your tax ID directly to your employer. It's more reliable than sending it to your {{ country === 'DE' ? 'home' : 'foreign'}} address.</p>
				<hr>
				<checkbox ref="sendToEmployerCheckbox" v-model="sendToEmployer">
					<div>Send the tax ID to my employer&nbsp;<recommended></recommended></div>
				</checkbox>
				<template v-if="sendToEmployer">
					<div class="form-group">
						<label :for="uid('employerName')">Employer name</label>
						<input
							:id="uid('employerName')"
							type="text"
							v-model="employerName"
							placeholder="Musterfirma GmbH"
							required>
					</div>
					<div class="form-group">
						<label :for="uid('employerAddress')">Address</label>
						<input
							:id="uid('employerAddress')"
							type="text"
							v-model="employerAddress"
							placeholder="Berliner Str. 123"
							autocomplete="address-line1"
							required>
					</div>
					<div class="form-group">
						<label :for="uid('employerPostCode')"><glossary term="Postleitzahl">Post code</glossary> and city</label>
						<div class="input-group">
							<postalcode-input :id="uid('employerPostCode')" v-model="employerPostCode" required></postalcode-input>
							<city-input v-model="employerCity" required></city-input>
						</div>
					</div>
					<div class="form-group">
						<label :for="uid('employerState')">State</label>
						<state-input :id="uid('employerState')" v-model="employerState" output="germanName" required></state-input>
					</div>
				</template>
			</template>
			<template v-if="stage === 'feedback'">
				<h2>Volunteer to give feedback</h2>
				<p>In 8 weeks, I want to ask you if you got your tax ID. Your feedback will help me improve this form.</p>
				<hr>
				<div class="form-group optional">
					<label :for="uid('email')">Email</label>
					<email-input ref="emailInput" v-model="email" :id="uid('email')"></email-input>
					<span class="input-instructions" v-if="!email">You will get a single email in 8 weeks. Nothing else.</span>
					<span class="input-instructions" v-if="email">Thank you! Your feedback will be really helpful.</span>
				</div>
			</template>
			<template v-if="stage === 'options'">
				<h2>You are almost done!</h2>
				<template v-if="people.length > 1">
					<p>Print these forms, sign them, and send them to your <em>Finanzamt</em>.</p>
					<ul class="buttons list">
						<li v-for="(person, index) in people">
							<button :aria-labelledby="uid('h-btnDownload') + index" @click="generatePDF(person)" :disabled="downloadInProgress">
								<icon-pdf/>
								<div>
									<h3 :id="uid('h-btnDownload') + index">Download the application form for {{ person.firstName }}</h3>
								</div>
							</button>
						</li>
					</ul>
				</template>
				<ul class="buttons list">
					<li v-if="people.length === 1">
						<button @click="generatePDF(people[0], people[1])" :disabled="downloadInProgress" :aria-labelledby="uid('h-btnDownload')">
							<icon-pdf/>
							<div>
								<h3 :id="uid('h-btnDownload')">Download your application form</h3>
								<p>Print and sign this form, and send it to your local <em>Finanzamt</em>.</p>
							</div>
						</button>
					</li>
				</ul>
				<h3>What to do next</h3>
				<ul class="buttons list">
					<li>
						<a href="/docs/010250-antrag-auf-vergabe-einer-steuerlichen-id#how-to-send-this-form" target="_blank">
							<icon-mail/>
							<div>
								<h3>Submit your {{ people.length > 1 ? 'forms' : 'form' }}</h3>
								<p>Learn how to send {{ people.length > 1 ? 'these forms' : 'this form' }} to the Finanzamt.</p>
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
			<hr>
			<div class="buttons bar">
				<button v-if="stageIndex === 0" class="button primary" @click="stageIndex += 1">Start <i class="icon right" aria-hidden="true"></i></button>
				<button v-if="stageIndex > 0" class="button" @click="previousStage"><i class="icon left" aria-hidden="true"></i> Go back</button>
				<button v-if="stage === 'addPeople'" class="button" @click="addPerson"><i class="icon person" aria-hidden="true"></i> Add another person</button>
				<button
					v-if="stageIndex > 0 && stageIndex < stages.length - 2"
					class="button primary"
					:disabled="['business', 'forgot', 'other'].includes(purpose)"
					@click="nextStage">Continue <i class="icon right" aria-hidden="true"></i></button>
				<button v-if="stageIndex === stages.length - 2" class="button primary" @click="nextStage">Finish</button>
			</div>
		</collapsible>
	`
}
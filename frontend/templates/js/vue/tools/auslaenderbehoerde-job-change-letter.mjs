import AddressInput from '/js/vue/components/address-input.mjs';
import Blank from '/js/vue/components/blank.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';
import Radio from '/js/vue/components/radio.mjs';
import Tabs from '/js/vue/components/tabs.mjs';
import { countriesInEnglish, countriesInGerman } from '/js/utils/countries.mjs';
import { dateFromString, formatDate } from '/js/utils/date.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default {
	components: {
		AddressInput,
		Blank,
		CountryInput,
		DatePicker,
		FullNameInput,
		LetterGenerator,
		Radio,
		Tabs,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			fullName: userDefaults.empty,
			address: '',
			dateOfBirth: userDefaults.empty,
			letterType: 'termination',
			placeOfBirth: '',
			nationality: userDefaults.empty,
			auslaenderbehoerde: 'berlin',
			customRecipientAddress: '',
			currentDate: new Date(),
			lastDayOfWork: '',

			countriesInEnglish,
			countriesInGerman,
		};
	},
	computed: {
		recipientAddress() {
			if(this.auslaenderbehoerde === 'berlin'){
				// Both locations use the same address for mail
				return 'Landesamt für Einwanderung\nFriedrich-Krause-Ufer 24\n13353 Berlin';
			}
			return this.customRecipientAddress;
		},
		showJobChangeWarning(){
			return this.letterType === 'jobChange' && this.auslaenderbehoerde === 'berlin'
		}
	},
	methods: {
		dateFromString,
		formatDate,
	},
	watch: {
		showJobChangeWarning() {
			[
				'letterTypeTermination',
				'letterTypeResignation',
				'letterTypeJobChange',
			].forEach(
				name => this.$refs[name].$el.querySelector('input').setCustomValidity(this.showJobChangeWarning ? 'Use the official form to report a job change.' : '')
			);
		},
	},
	template: `
		<letter-generator
			aria-description="Generate a letter to notify the Berlin immigration office of a job change"
			aria-label="Ausländerbehörde job change notice letter generator"
			track-as="Ausländerbehörde job change"
			:static="static">
			<template v-slot:header>Ausländerbehörde – Job change notice</template>

			<template v-slot:letter-recipient="{ language, stage }">
				<span class="letter-return-address" v-if="address">
					{{ fullName }}<template v-if="fullName && address">, </template>
					{{ address.replaceAll('\\n', ', ') }}
				</span>
				<span class="letter-return-address" v-else></span>
				<span v-if="recipientAddress" v-html="recipientAddress.replaceAll('\\n', '<br>')"></span>
			</template>

			<template v-slot:letter-details="{ language, stage }">
				<template v-if="language === 'en'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Date:</strong> {{ formatDate(currentDate, 'en-US') }}
				</template>
				<template v-if="language === 'de'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Datum:</strong> {{ formatDate(currentDate, 'de-DE') }}
				</template>
			</template>

			<template v-slot:letter-body="{ language, stage }">
				<template v-if="language === 'en'">
					<p>
						<strong v-if="letterType === 'jobChange'">Subject: Notification of job change</strong>
						<strong v-else>Subject: Notification of job termination</strong>
					</p>
					<p>
						Dear Sir or Madam,
					</p>
					<p>
						My name is <blank :key="uid('fullNameBlankEn')" placeholder="Name">{{ fullName }}</blank>. I am a citizen of <blank :key="uid('nationalityBlankEn')" placeholder="Country">{{ countriesInEnglish[nationality] }}</blank>. I was born on <blank :key="uid('dateOfBirthBlankEn')" placeholder="Date of birth">{{ formatDate(dateOfBirth, 'en-US') }}</blank> in <blank :key="uid('placeOfBirthBlankEn')" placeholder="Birthplace">{{ placeOfBirth }}</blank>.
					</p>
					<p v-if="letterType === 'resignation'">
						I am writing to inform the Ausländerbehörde that I have quit my job.
						My last day of work {{ dateFromString(lastDayOfWork) >= currentDate ? 'is' : 'was' }} on <blank :key="uid('lastDayOfWorkBlankEn')" placeholder="Last day of work">{{ formatDate(lastDayOfWork, 'en-US') }}</blank>.
						I have attached a copy of my resignation letter.
					</p>
					<p v-if="letterType === 'termination'">
						I am writing to inform the Ausländerbehörde that my employer has terminated my employment.
						My last day of work {{ dateFromString(lastDayOfWork) >= currentDate ? 'is' : 'was' }} on <blank :key="uid('lastDayOfWorkBlankEn')" placeholder="Last day of work">{{ formatDate(lastDayOfWork, 'en-US') }}</blank>.
						I have attached a copy of the termination notice.
					</p>
					<p v-if="letterType === 'jobChange'">
						I am writing to inform the Ausländerbehörde that I am changing jobs.
						I have attached a copy of my resignation letter and my new job contract.
					</p>
					<p>
						Please tell me what to do next, and inform me of any changes to my residence permit.
					</p>
					<p>
						Best regards<template v-if="fullName">,<br></template>
						{{ fullName }}
					</p>
				</template>

				<template v-if="language === 'de'">
					<p>
						<strong v-if="letterType === 'jobChange'">Betreff: Mitteilung über Jobwechsel</strong>
						<strong v-else>Betreff: Mitteilung über Arbeitsplatzkündigung</strong>
					</p>
					<p>
						Sehr geehrte Damen und Herren,
					</p>
					<p>
						Mein Name ist <blank :key="uid('fullNameBlankDe')" placeholder="Name">{{ fullName }}</blank>. Ich bin Staatsangehöriger von <blank :key="uid('nationalityBlankDe')" placeholder="Land">{{ countriesInGerman[nationality] }}</blank>. Ich wurde am <blank :key="uid('dateOfBirthBlankDe')" placeholder="Geburtsdatum">{{ formatDate(dateOfBirth, 'de-DE') }}</blank> in <blank :key="uid('placeOfBirthBlankDe')" placeholder="Geburtsort">{{ placeOfBirth }}</blank> geboren.
					</p>
					<p v-if="letterType === 'resignation'">
						Ich schreibe, um die Ausländerbehörde darüber zu informieren, dass ich meinen Job gekündigt habe.
						Mein letzter Arbeitstag {{ dateFromString(lastDayOfWork) >= currentDate ? 'ist' : 'war' }} am <blank :key="uid('lastDayOfWorkBlankDe')" placeholder="Letzte Arbeitstag">{{ formatDate(lastDayOfWork, 'de-DE') }}</blank>.
						Beigefügt ist eine Kopie meines Kündigungsschreibens.
					</p>
					<p v-if="letterType === 'termination'">
						Ich schreibe, um die Ausländerbehörde darüber zu informieren, dass mein Arbeitgeber mein Arbeitsverhältnis beendet hat.
						Mein letzter Arbeitstag {{ dateFromString(lastDayOfWork) >= currentDate ? 'ist' : 'war' }} am <blank :key="uid('lastDayOfWorkBlankDe')" placeholder="Letzte Arbeitstag">{{ formatDate(lastDayOfWork, 'de-DE') }}</blank>.
						Beigefügt ist eine Kopie der Kündigungserklärung.
					</p>
					<p v-if="letterType === 'jobChange'">
						Ich schreibe, um die Ausländerbehörde darüber zu informieren, dass ich meinen Job gewechselt habe.
						Ich habe eine Kopie meines Kündigungsschreibens und meines neuen Arbeitsvertrags angehängt.
					</p>
					<p>
						Bitte sagen Sie mir, was ich als Nächstes tun soll, und informieren Sie mich über eventuelle Änderungen meiner Aufenthaltserlaubnis.
					</p>
					<p>
						Mit freundlichen Grüßen<template v-if="fullName">,<br></template>
						{{ fullName }}
					</p>
				</template>

				<p class="signature"
					v-if="stage === 'printPreview'"
					v-text="language === 'en' ? 'Signature' : 'Unterschrift'"></p>
			</template>

			<template v-slot:form>
				<div class="form-group show-errors">
					<span class="label">What happened?</span>
					<radio ref="letterTypeTermination" v-model="letterType" value="termination">
						I was fired or laid off
					</radio>
					<radio ref="letterTypeResignation" v-model="letterType" value="resignation">
						I quit my job
					</radio>
					<radio ref="letterTypeJobChange" v-model="letterType" value="jobChange">
						I am changing jobs
					</radio>
					<span v-if="showJobChangeWarning" class="input-instructions">In Berlin, use the <a href="/out/auslanderbehorde-job-change" target="_blank">official form</a> to report a job change.</span>
				</div>
				<div class="form-group">
					<label :for="uid('last-workday')">Last day of work</label>
					<date-picker
						v-model="lastDayOfWork"
						:id="uid('last-workday')"
						required></date-picker>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('fullName')">Your full name</label>
					<full-name-input :id="uid('fullName')" v-model="fullName" required></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('address')">Your address</label>
					<address-input :id="uid('address')" v-model="address" home required></address-input>
					<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#how-to-write-german-addresses" target="_blank">How to write your address</a>
				</div>
				<div class="form-group">
					<label :for="uid('date-of-birth')">Date of birth</label>
					<date-picker
						v-model="dateOfBirth"
						:id="uid('date-of-birth')"
						autocomplete="bday"
						required></date-picker>
				</div>
				<div class="form-group">
					<label :for="uid('place-of-birth')">Place of birth</label>
					<input type="text"
						v-model="placeOfBirth"
						placeholder="Montreal"
						required
						:id="uid('place-of-birth')">
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
					<span class="label">Ausländerbehörde</span>
					<tabs
						aria-label="Ausländerbehörde"
						v-model="auslaenderbehoerde"
						:id="uid('auslaenderbehoerde')"
						:options="[{label: 'Berlin', value: 'berlin'}, {label: 'Other', value: 'other'}]"
						required></tabs>
					<address-input
						:id="uid('customRecipientAddress')"
						v-if="auslaenderbehoerde === 'other'"
						v-model="customRecipientAddress"
						:placeholder="'Ausländerbehörde\\nMusterstraße 123\\n12345 Munich'"
						required></address-input>
					<a class="input-instructions external-link" v-if="auslaenderbehoerde === 'other'" href="https://bamf-navi.bamf.de/en/Themen/Behoerden/" target="_blank">
						Find your Ausländerbehörde
					</a>
					<span v-if="showJobChangeWarning" class="input-instructions error">
						Use the <a href="/out/auslanderbehorde-job-change" target="_blank">official form</a> to report a job change.
					</span>
				</div>
			</template>
		</letter-generator>
	`,
}
import AddressInput from '/js/vue/components/address-input.mjs';
import Blank from '/js/vue/components/blank.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import GenderInput from '/js/vue/components/gender-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';
import Recommended from '/js/vue/components/recommended.mjs';

import { formatDate } from '/js/utils/date.mjs';
import { formatName, formatSalutations } from '/js/utils/letter.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default {
	components: {
		AddressInput,
		Blank,
		Checkbox,
		DatePicker,
		FirstNameInput,
		FullNameInput,
		GenderInput,
		Glossary,
		LastNameInput,
		LetterGenerator,
		Recommended,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			fullName: userDefaults.empty,
			address: '',
			recipientGender: 'man',
			recipientFirstName: '',
			recipientLastName: '',
			employerAddress: '',
			employerCompanyName: '',
			employeeNumber: '',
			currentDate: new Date(),
			lastDayOfWork: null,

			requestLetterOfReference: true,
			requestVacationCertificate: true,
			requestQualifiedLetterOfReference: false,
			requestProvisionalLetterOfReference: false,
		};
	},
	computed: {
		hasRequestedAnyDocuments() {
			return this.requestLetterOfReference || this.requestProvisionalLetterOfReference || this.requestQualifiedLetterOfReference || this.requestVacationCertificate;
		}
	},
	methods: {
		formatDate,
		formatName,
		formatSalutations,
	},
	template: `
		<letter-generator
			aria-label="Job resignation letter generator"
			aria-description="Generate a letter to officially quit your job"
			track-as="Job resignation letter"
			:static="static">
			<template v-slot:header>Job resignation letter</template>

			<template v-slot:letter-recipient="{ language, stage }">
				<span class="letter-return-address">
					<blank :key="uid('fullNameReturnBlank')" placeholder="Your full name">{{ fullName }}</blank>,
					<blank :key="uid('addressReturnBlank')" placeholder="your address">{{ address.replaceAll('\\n', ', ') }}</blank>
				</span>
				<blank :key="uid('employerNameBlank')" placeholder="Employer name">{{ employerCompanyName }}</blank><br>
				<template v-if="formatName(recipientGender, recipientFirstName, recipientLastName, language)">
					{{ formatName(recipientGender, recipientFirstName, recipientLastName, language) }}<br>
				</template>
				<blank :key="uid('employerAddressBlank')" v-if="!employerAddress.trim()" placeholder="Employer address"></blank>
				<span v-if="employerAddress.trim()" v-html="employerAddress.replaceAll('\\n', '<br>')"></span>
			</template>

			<template v-slot:letter-details="{ language, stage }">
				<template v-if="language === 'en'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Date:</strong> {{ currentDate.toLocaleDateString("en-US") }}
					<template v-if="employeeNumber"><br><strong>Employee number: </strong> {{ employeeNumber }}</template>
				</template>
				<template v-if="language === 'de'">
					<strong>Name:</strong> <blank :key="uid('fullNameBlank')" placeholder="Your full name">{{ fullName }}</blank><br>
					<strong>Datum:</strong> {{ currentDate.toLocaleDateString("de-DE") }}
					<template v-if="employeeNumber"><br><strong>Personalnummer: </strong> {{ employeeNumber }}</template>
				</template>
			</template>

			<template v-slot:before-print-preview="{ language }">
				<p class="input-instructions" v-if="language == 'en'">Send the German version to your employer.</p>
			</template>

			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Subject: Termination of my employment contract</strong>
					<template v-if="employeeNumber"><br>Employee number: {{ employeeNumber }}</template>
				</p>
				<p v-if="language === 'de'">
					<strong>Betreff: Kündigung meines Arbeitsvertrages</strong>
					<template v-if="employeeNumber"><br>Personalnummer: {{ employeeNumber }}</template>
				</p>

				<p v-text="formatSalutations(recipientGender, recipientFirstName, recipientLastName, language)"></p>

				<p v-if="language === 'en' && lastDayOfWork">
					I hereby give notice of my resignation in accordance with the applicable notice period on {{ formatDate(lastDayOfWork, 'en-US') }}. Alternatively, I hereby resign at the earliest possible date.
				</p>
				<p v-if="language === 'en' && !lastDayOfWork">
					I hereby give notice of my resignation of my employment in accordance with the applicable notice period, effective at the earliest possible date.
				</p>

				<p v-if="language === 'de' && lastDayOfWork">
					Hiermit kündige ich mein Arbeitsverhältnis unter Einhaltung der maßgeblichen Kündigungsfrist ordentlich zum {{ formatDate(lastDayOfWork, 'de-DE') }}. Hilfsweise kündige ich zum nächstmöglichen Termin.
				</p>
				<p v-if="language === 'de' && !lastDayOfWork">
					Hiermit kündige ich mein Arbeitsverhältnis unter Einhaltung der maßgeblichen Kündigungsfrist ordentlich zum nächstmöglichen Termin.
				</p>

				<p v-if="language === 'en'">
					Please confirm receipt of this resignation notice and the termination date of my employment in writing.
				</p>
				<p v-if="language === 'de'">
					Bitte bestätigen Sie mir den Erhalt dieser Kündigung und das Beendigungsdatum meines Arbeitsverhältnisses schriftlich.
				</p>

				<p v-if="language === 'en'&& hasRequestedAnyDocuments">
					Additionally, please promptly send me the following documents:
				</p>
				<p v-if="language === 'de'&& hasRequestedAnyDocuments">
					Zusätzlich, senden Sie mir bitte umgehend die folgenden Dokumente:
				</p>

				<ul v-if="language === 'en' && hasRequestedAnyDocuments">
					<li v-if="requestLetterOfReference">a letter of reference (<em>Arbeitszeugnis</em>)</li>
					<li v-if="requestProvisionalLetterOfReference">a provisional letter of reference (<em>vorläufiges Arbeitszeugnis</em>)</li>
					<li v-if="requestQualifiedLetterOfReference">a qualified letter of reference (<em>qualifiziertes Arbeitszeugnis</em>)</li>
					<li v-if="requestVacationCertificate">a vacation certificate (<em>Urlaubsbescheinigung</em>)</li>
				</ul>
				<ul v-if="language === 'de' && hasRequestedAnyDocuments">
					<li v-if="requestLetterOfReference">Arbeitszeugnis</li>
					<li v-if="requestProvisionalLetterOfReference">vorläufiges Arbeitszeugnis</li>
					<li v-if="requestQualifiedLetterOfReference">qualifiziertes Arbeitszeugnis</li>
					<li v-if="requestVacationCertificate">Urlaubsbescheinigung</li>
				</ul>

				<p v-if="language === 'en'">
					Best regards,<br>
					<blank :key="uid('fullNameBlankEn')" placeholder="Your full name">{{ fullName }}</blank>
				</p>
				<p v-if="language === 'de'">
					Mit freundlichen Grüßen,<br>
					<blank :key="uid('fullNameBlankDe')" placeholder="Your full name">{{ fullName }}</blank>
				</p>

				<p class="signature" v-if="stage === 'printPreview'">
					{{ language === 'en' ? 'Signature' : 'Unterschrift' }}
				</p>
			</template>

			<template v-slot:form="{ language }">
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
					<label :for="uid('employeeNumber')">Employee number</label>
					<input type="text" :id="uid('employeeNumber')" v-model="employeeNumber">
					<span class="input-instructions">You might not have an employee number.</span>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('employerCompanyName')">Employer name</label>
					<input
						:id="uid('employerCompanyName')"
						type="text"
						v-model="employerCompanyName"
						placeholder="Musterfirma GmbH"
						autocomplete="organization"
						required>
				</div>
				<div class="form-group">
					<label :for="uid('employerAddress')">Employer address</label>
					<address-input :id="uid('employerAddress')" v-model="employerAddress" work required></address-input>
				</div>
				<div class="form-group">
					<span class="label">Letter recipient</span>
					<div class="input-group">
						<gender-input v-model="recipientGender"></gender-input>
						<first-name-input
							v-model="recipientFirstName"
							autocomplete="off"
							required></first-name-input>
						<last-name-input
							v-model="recipientLastName"
							autocomplete="off"
							required></last-name-input>
						<span class="input-instructions">This should be your manager or a human resources employee.</span>
					</div>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('last-workday')">Last day of work</label>
					<date-picker
						v-model="lastDayOfWork"
						:id="uid('last-workday')"></date-picker>
					<span class="input-instructions">To resign at the earliest possible date, leave this field empty.</span>
				</div>
				<div class="form-group">
					<span class="label">Ask for documents</span>
					<checkbox v-model="requestVacationCertificate">
						<div><glossary term="Urlaubsbescheinigung">Vacation certificate</glossary>&nbsp; <recommended></recommended></div>
						<span class="input-instructions">Your next employer might need it.</span>
					</checkbox>
					<checkbox v-model="requestLetterOfReference">
						<div><glossary term="Arbeitszeugnis">Letter of reference</glossary>&nbsp; <recommended></recommended></div>
						<span class="input-instructions">It proves that you worked there. Your employer can't refuse to give you this letter.</span>
					</checkbox>
					<checkbox v-model="requestProvisionalLetterOfReference">
						<div>Provisional <glossary term="Arbeitszeugnis">letter of reference</glossary></div>
						<span class="input-instructions">Get a letter of reference before your last day of work. It can help your job search.</span>
					</checkbox>
					<checkbox v-model="requestQualifiedLetterOfReference">
						<div>Qualified <glossary term="Arbeitszeugnis">letter of reference</glossary></div>
						<span class="input-instructions">It includes an evaluation of your performance. Your employer can refuse to give you this letter.</span>
					</checkbox>
				</div>
			</template>
		</letter-generator>
	`
}
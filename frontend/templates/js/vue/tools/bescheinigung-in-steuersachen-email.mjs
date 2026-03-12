import AddressInput from '/js/vue/components/address-input.mjs';
import Blank from '/js/vue/components/blank.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';
import { formatCurrency } from '/js/utils/currency.mjs';
import { formatDate } from '/js/utils/date.mjs';
import { formatSalutations } from '/js/utils/letter.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { bescheinigungInSteuersachenFee } from '/js/utils/constants.mjs';

export default {
	components: {
		AddressInput,
		Blank,
		Checkbox,
		DatePicker,
		FullNameInput,
		LetterGenerator,
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
			taxID: '',
			finanzamt: '',
			currentDate: new Date(),
			hasPaidFee: false,
			formatSalutations,
			formatDate,
			bescheinigungInSteuersachenFee: {
				en: formatCurrency(bescheinigungInSteuersachenFee, true, false, false, "en-US"),
				de: formatCurrency(bescheinigungInSteuersachenFee, true, false, false, "de-DE"),
			},
		};
	},
	template: `
		<letter-generator
			aria-label="Bescheinigung in Steuersachen email generator"
			aria-description="Generate an email to request a Bescheinigung in Steuersachen from your Finanzamt"
			track-as="Bescheinigung in Steuersachen letter"
			:printable="false"
			:static="static">
			<template v-slot:header>Request for a Bescheinigung in Steuersachen</template>

			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Request for a Bescheinigung in Steuersachen</strong>
				</p>
				<p v-if="language === 'de'">
					<strong>Antrag auf Erteilung einer Bescheinigung in Steuersachen</strong>
				</p>

				<p v-text="formatSalutations(null, null, null, language)"></p>

				<p v-if="language === 'en'">
					I am applying for the issuance of a <em>Bescheinigung in Steursachen</em>. The application form is attached.
				</p>
				<p v-if="language === 'de'">
					hiermit beantrage ich die Erteilung einer Bescheinigung in Steursachen. Das Antragsformular ist beigefügt.
				</p>

				<p v-if="language === 'en'">
					My details are as follows:
				</p>
				<p v-if="language === 'de'">
					Meine Angaben lauten wie folgt:
				</p>

				<ul>
					<li>
						Name:
						<blank :key="uid('fullNameBlank')" placeholder="Full name">{{ fullName }}</blank>
					</li>
					<li>
						<template v-if="language === 'en'">Address:</template>
						<template v-if="language === 'de'">Anschrift:</template>
						<blank :key="uid('addressBlank')" placeholder="Address">{{ address.replaceAll('\\n', ', ') }}</blank>
					</li>
					<li>
						<template v-if="language === 'en'">Date of birth:</template>
						<template v-if="language === 'de'">Geburtsdatum:</template>
						<blank :key="uid('dateOfBirthBlank' + language)" placeholder="Date of birth">{{ formatDate(dateOfBirth, language) }}</blank>
					</li>
					<li>
						<template v-if="language === 'en'">Tax ID:</template>
						<template v-if="language === 'de'">Steuer-ID:</template>
						<blank :key="uid('taxIdBlank')" placeholder="Tax ID">{{ taxID }}</blank>
					</li>
				</ul>

				<p v-if="language === 'en'">
					<template v-if="hasPaidFee">I have already paid the fee of €{{ bescheinigungInSteuersachenFee.en }} on {{ currentDate.toLocaleDateString("en-US") }}. </template>
					Please issue the requested document to my home address as soon as possible.
				</p>
				<p v-if="language === 'de'">
					<template v-if="hasPaidFee">Ich habe die Gebühr von €{{ bescheinigungInSteuersachenFee.de }} bereits am {{ currentDate.toLocaleDateString("de-DE") }} bezahlt. </template>
					Bitte stellen Sie die angeforderte Bescheinigung so schnell wie möglich an meine Privatadresse aus.
				</p>

				<p v-if="language === 'en'">
					Best regards,<br>
					<blank :key="uid('fullNameSignatureBlank')" placeholder="Full name">{{ fullName }}</blank>
				</p>
				<p v-if="language === 'de'">
					Mit freundlichen Grüßen,<br>
					<blank :key="uid('fullNameSignatureBlank')" placeholder="Full name">{{ fullName }}</blank>
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
				</div>
				<div class="form-group">
					<label :for="uid('date-of-birth')">Date of birth</label>
					<date-picker
						v-model="dateOfBirth"
						:id="uid('date-of-birth')"
						autocomplete="bday" required></date-picker>
				</div>
				<div class="form-group">
					<label :for="uid('taxID')">Tax ID</label>
					<input type="text" :id="uid('taxID')" v-model="taxID" placeholder="12 345 678 901" required>
					<a class="input-instructions internal-link" href="/guides/german-tax-id-steuernummer#where-to-find-your-tax-id" target="_blank">Find your tax ID</a>
				</div>
				<hr>
				<checkbox v-model="hasPaidFee">
					<div>I already transferred €{{ bescheinigungInSteuersachenFee.en }} to the <em>Finanzamt</em> (optional)</div>
				</checkbox>
			</template>
		</letter-generator>
	`,
}
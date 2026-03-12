import AddressInput from '/js/vue/components/address-input.mjs';
import Blank from '/js/vue/components/blank.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import Eur from '/js/vue/components/eur.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import GenderInput from '/js/vue/components/gender-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

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
		Eur,
		FirstNameInput,
		FullNameInput,
		GenderInput,
		Glossary,
		IncomeInput,
		LastNameInput,
		LetterGenerator,
		Tabs,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			fullName: userDefaults.empty,
			oldAddress: '',
			newAddress: '',

			recipientType: 'company',
			recipientCompanyName: '',
			recipientGender: 'man',
			recipientFirstName: '',
			recipientLastName: '',
			recipientAddress: '',
			kautionAmount: '',
			remainingKautionAmount: '',
			bankAccountName: '',
			bankAccountIBAN: '',
			hasReceivedNebenkostenabrechnung: true,
			hasReceivedPartOfKaution: false,

			currentDate: new Date(),
			moveOutDate: '',
			deadlineWeeks: 2,
		};
	},
	computed: {
		longDeadline() {
			const deadlineDate = new Date();
			deadlineDate.setDate(deadlineDate.getDate() + this.deadlineWeeks * 7)
			return deadlineDate.toLocaleDateString('en-US', {
				day: 'numeric',
				month: 'long',
			});
		}
	},
	methods: {
		formatDate,
		formatName,
		formatSalutations,
		deadline(language) {
			const deadlineDate = new Date();
			deadlineDate.setDate(deadlineDate.getDate() + this.deadlineWeeks * 7)
			return formatDate(deadlineDate, {en: 'en-US', de: 'de-DE'}[language]);
		}
	},
	template: `
		<letter-generator
			aria-label="Letter generator to ask for your apartment deposit back"
			track-as="Return of apartment deposit letter generator"
			:static="static">
			<template v-slot:header>Return of apartment deposit</template>

			<template v-slot:letter-recipient="{ language, stage }">
				<span class="letter-return-address">
					<blank placeholder="Your full name">{{ fullName }}</blank>,
					<blank placeholder="your address">{{ newAddress.replaceAll('\\n', ', ') }}</blank>
				</span>

				<blank placeholder="Housing company name" v-if="recipientType === 'company'" :key="uid('landlordCompanyNameBlank')">
					{{ recipientCompanyName }}
				</blank>
				<blank placeholder="Landlord's name" v-if="recipientType === 'private'" :key="uid('landlordNameBlank')">
					{{ formatName(recipientGender, recipientFirstName, recipientLastName, language) }}
				</blank>

				<br>
				<blank :placeholder="recipientType === 'company' ? 'Housing company address' : 'Landlord\\'s address'" :key="uid('recipientAddressBlank')">
					<span v-if="recipientAddress" v-html="recipientAddress.replaceAll('\\n', '<br>')"></span>
				</blank>
			</template>

			<template v-slot:letter-details="{ language, stage }">
				<template v-if="language === 'en'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Date:</strong> {{ currentDate.toLocaleDateString("en-US") }}
				</template>
				<template v-if="language === 'de'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Datum:</strong> {{ currentDate.toLocaleDateString("de-DE") }}
				</template>
			</template>

			<template v-slot:before-print-preview="{ language }">
				<p class="input-instructions" v-if="language == 'en'">Send the German version to your landlord.</p>
			</template>

			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Subject: Return of apartment deposit</strong>
				</p>
				<p v-if="language === 'de'">
					<strong>Betreff: Rückzahlung der Mietkaution</strong>
				</p>

				<p v-text="formatSalutations(recipientGender, recipientFirstName, recipientLastName, language)"></p>

				<p v-if="language === 'en'">
					Our tenancy for the apartment mentioned below has been terminated since <blank placeholder="Move-out date" key="moveOutDate">{{ formatDate(moveOutDate, 'en-US') }}</blank>. The apartment has been vacated and properly handed over to you<template v-if="hasReceivedNebenkostenabrechnung">, and there is no outstanding utility bill</template>.
				</p>
				<p v-if="language === 'de'">
					Unser Mietverhältnis über die unten genannte Wohnung ist seit dem <blank placeholder="Move-out date" key="moveOutDate">{{ formatDate(moveOutDate, 'de-DE') }}</blank> beendet und die Wohnung wurde geräumt und ordnungsgemäß an Sie übergeben<template v-if="hasReceivedNebenkostenabrechnung">, und es gibt keine offenen Nebenkostenabrechnungen</template>.
				</p>

				<p v-if="language === 'en'">
					Address: <blank :key="uid('oldAddressBlankEn')" placeholder="Apartment address" key="oldAddress">{{ oldAddress.replaceAll('\\n', ', ') }}</blank>
					<br>
					Tenant name: <blank :key="uid('tenantNameBlankEn')" placeholder="Full name" key="fullName">{{ fullName }}</blank>
				</p>
				<p v-if="language === 'de'">
					Anschrift: <blank :key="uid('oldAddressBlankDe')" placeholder="Apartment address" key="oldAddress">{{ oldAddress.replaceAll('\\n', ', ') }}</blank>
					<br>
					Name des Mieters/der Mieterin: <blank :key="uid('tenantNameBlankDe')" placeholder="Full name" key="fullName">{{ fullName }}</blank>
				</p>

				<p v-if="language === 'en' && !hasReceivedNebenkostenabrechnung && !hasReceivedPartOfKaution">
					The outstanding utility bill does not entitle you to retain the entire deposit, but only an amount equivalent to the expected utility costs.
				</p>
				<p v-if="language === 'de' && !hasReceivedNebenkostenabrechnung && !hasReceivedPartOfKaution">
					Die ausstehende Nebenkostenabrechnung berechtigt nicht zur Einbehaltung der gesamten Kaution, sondern nur zur Einbehaltung eines Betrages in Höhe der zu erwartenden Nebenkosten.
				</p>

				<p v-if="language === 'en'">
					I request that you transfer
					<template v-if="hasReceivedPartOfKaution">
						the remaining
						<blank :key="uid('remainingDepositBlankEn')" placeholder="Remaining deposit" v-if="!remainingKautionAmount"></blank><eur cents :amount="remainingKautionAmount" v-if="remainingKautionAmount"></eur>
						of the
						<blank :key="uid('totalDepositBlankEn')" placeholder="Total deposit" v-if="!kautionAmount"></blank><eur cents :amount="kautionAmount" v-if="kautionAmount"></eur>
						deposit
					</template>
					<template v-if="!hasReceivedPartOfKaution">
						the deposit of
						<blank :key="uid('totalDepositBlankEn')" placeholder="Deposit amount" v-if="!kautionAmount"></blank><eur cents :amount="kautionAmount" v-if="kautionAmount"></eur>
					</template>
					plus interest to my account by {{ deadline(language) }} at the latest.
				</p>
				<p v-if="language === 'de'">
					Ich fordere Sie auf,
					<template v-if="hasReceivedPartOfKaution">
						die restlichen
						<blank :key="uid('remainingDepositBlankDe')" placeholder="Remaining deposit" v-if="!remainingKautionAmount"></blank><eur cents :amount="remainingKautionAmount" locale="de-DE" v-if="remainingKautionAmount"></eur>
						der
						<blank :key="uid('totalDepositBlankDe')" placeholder="Total deposit" v-if="!kautionAmount"></blank><eur cents :amount="kautionAmount" locale="de-DE" v-if="kautionAmount"></eur> Kaution
					</template>
					<template v-if="!hasReceivedPartOfKaution">
						die Kaution in Höhe von
						<blank :key="uid('totalDepositBlankDe')" placeholder="Deposit amount" v-if="!kautionAmount"></blank><eur cents :amount="kautionAmount" locale="de-DE" v-if="kautionAmount"></eur>
					</template>
					zuzüglich Zinsen bis spätestens {{ deadline(language) }} auf mein Konto zu überweisen.
				</p>

				<p v-if="language === 'en'">
					Account holder: <blank  :key="uid('bankAccountNameBlankEn')" placeholder="Full name" key="bankAccountName">{{ bankAccountName || fullName }}</blank>
					<br>
					IBAN: <blank :key="uid('ibanBlankEn')" placeholder="Account IBAN" key="bankAccountIBAN">{{ bankAccountIBAN }}</blank>
				</p>
				<p v-if="language === 'de'">
					Kontoinhaber:</strong> <blank  :key="uid('bankAccountNameBlankDe')" placeholder="Full name" key="bankAccountName">{{ bankAccountName || fullName }}</blank>
					<br>
					IBAN: <blank :key="uid('ibanBlankDe')" placeholder="Account IBAN" key="bankAccountIBAN">{{ bankAccountIBAN }}</blank>
				</p>

				<p v-if="language === 'en'">
					Should you have any reasons against paying out my rental deposit, please let me know by {{ deadline(language) }} at the latest.
				</p>
				<p v-if="language === 'de'">
					Sollten aus Ihrer Sicht Gründe gegen die Auszahlung meiner Mietkaution sprechen, bitte ich Sie, mir diese bis spätestens {{ deadline(language) }} mitzuteilen.
				</p>

				<p v-if="language === 'en'">
					Best regards<template v-if="fullName">,<br></template>
					{{ fullName }}
				</p>
				<p v-if="language === 'de'">
					Mit freundlichen Grüßen<template v-if="fullName">,<br></template>
					{{ fullName }}
				</p>

				<p class="signature"
					v-if="stage === 'printPreview'"
					v-text="language === 'en' ? 'Signature' : 'Unterschrift'"></p>
			</template>

			<template v-slot:form="{ language }">
				<div class="form-group">
					<label :for="uid('fullName')">Your full name</label>
					<full-name-input :id="uid('fullName')" v-model="fullName" required></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('oldAddress')">Old address</label>
					<address-input :id="uid('oldAddress')"
						v-model="oldAddress"
						:placeholder="'Alte Wohnungstraße 123\\n12345 Berlin'"
						required></address-input>
					<span class="input-instructions">This is the apartment for which you want the deposit back.</span>
					<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#how-to-write-german-addresses" target="_blank">How to write your address</a>
				</div>
				<div class="form-group">
					<label :for="uid('moveOutDate')">Move-out date</label>
					<date-picker v-model="moveOutDate" :id="uid('moveOutDate')" required></date-picker>
				</div>
				<div class="form-group">
					<label :for="uid('newAddress')">Current address</label>
					<address-input :id="uid('newAddress')"
						v-model="newAddress"
						:placeholder="'Neue Wohnungstraße 123\\n12345 Berlin'"
						home></address-input>
					<span class="input-instructions">
						The return address for this letter.
					</span>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('kautionAmount')">Deposit amount</label>
					<div class="input-group">
						<income-input :id="uid('kautionAmount')" v-model="kautionAmount" required></income-input>&nbsp;€
					</div>
					<checkbox v-model="hasReceivedPartOfKaution">
						I already got part of my deposit back
					</checkbox>
				</div>
				<div class="form-group" v-if="hasReceivedPartOfKaution">
					<label :for="uid('remainingKautionAmount')">Remaining deposit</label>
					<div class="input-group" v-if="hasReceivedPartOfKaution">
						<income-input :id="uid('remainingKautionAmount')" v-model="remainingKautionAmount" required></income-input>€ left&nbsp;to&nbsp;pay
					</div>
				</div>
				<div class="form-group">
					<span class="label">Utilities bill</span>
					<checkbox v-model="hasReceivedNebenkostenabrechnung">
						<div>
							I received the last <glossary>Nebenkostenabrechnung</glossary>
						</div>
					</checkbox>
					<span class="input-instructions">
						Landlords wait for the Nebenkostenabrechnung to return your deposit. This can take up to 12 months. They can only keep a part of your deposit for this.
					</span>
					<a class="input-instructions internal-link" href="/guides/mietkaution#when-do-i-get-my-kaution-back" target="_blank">More information</a>
				</div>
				<hr>
				<div class="form-group">
					<span class="label">Landlord type</span>
					<tabs
						aria-label="Landlord type"
						v-model="recipientType"
						:id="uid('recipientType')"
						:options="[{label: 'Housing company', value: 'company'}, {label: 'Private landlord', value: 'private'}]"
						required>
					</tabs>
				</div>
				<div class="form-group" v-if="recipientType == 'company'">
					<label :for="uid('recipientCompanyName')">Company name</label>
					<input
						:id="uid('recipientCompanyName')"
						type="text"
						v-model="recipientCompanyName"
						autocomplete="organization"
						placeholder="Muster Hausverwaltung GmbH"
						required>
				</div>
				<div class="form-group" v-if="recipientType == 'private'">
					<span class="label">Landlord's name</span>
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
					</div>
				</div>
				<div class="form-group">
					<label :for="uid('recipientAddress')">Address</label>
					<address-input
						:id="uid('recipientAddress')"
						v-model="recipientAddress"
						:placeholder="'Vermieterstraße 123\\n12345 Berlin'"
						autocomplete="off"
						required></address-input>
				</div>
				<div class="form-group">
					<label :for="uid('deadlineWeeks')">Time to respond</label>
					<select :id="uid('deadlineWeeks')" v-model="deadlineWeeks">
						<option :value="2">2 weeks</option>
						<option :value="4">4 weeks</option>
						<option :value="6">6 weeks</option>
					</select>
					<span class="input-instructions">Ask for a reply before {{ longDeadline }}</span>
				</div>
				<hr>
				<p>Where should your landlord return your deposit? Deposits are usually paid by <glossary term="SEPA-Überweisung">bank transfer</glossary>.</p>
				<div class="form-group">
					<label :for="uid('bankAccountName')">Bank account holder</label>
					<full-name-input :id="uid('bankAccountName')" v-model="bankAccountName" :placeholder="fullName"></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('bankAccountIBAN')"><glossary>IBAN</glossary></label>
					<input type="text"
						:id="uid('bankAccountIBAN')"
						v-model="bankAccountIBAN"
						placeholder="DE00 0000 0000 0000 0000 00"
						required>
				</div>
			</template>
		</letter-generator>
	`,
}
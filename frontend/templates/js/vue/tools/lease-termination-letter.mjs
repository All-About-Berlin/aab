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
import Tabs from '/js/vue/components/tabs.mjs';

import { dateFromString, formatLongDate, isoDay } from '/js/utils/date.mjs';
import { formatName, formatSalutations } from '/js/utils/letter.mjs';
import { getMoveOutDate, getLatestNoticeDate } from '/js/utils/lease.mjs';
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
		Tabs,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			people: [],
			address: '',
			fullName: userDefaults.empty,  // Just used to load the name from userdefaults
			recipientGender: 'man',
			recipientFirstName: '',
			recipientLastName: '',
			askForDepositReturn: false,
			bankAccountName: '',
			bankAccountIBAN: '',

			recipientType: 'company',
			recipientCompanyName: '',
			recipientGender: 'man',
			recipientFirstName: '',
			recipientLastName: '',
			recipientAddress: '',

			currentDate: new Date(),
			customMoveOutDate: false,
			desiredMoveOutDate: '',  // YYYY-MM-DD string
		};
	},
	mounted() {
		this.addPerson();
	},
	computed: {
		de(){
			const many = this.people.length > 1;
			return {
				wir: many ? 'wir' : 'ich',
				unser: many ? 'unser' : 'mein',
				uns: many ? 'uns' : 'mich',
			}
		},
		en(){
			const many = this.people.length > 1;
			return {
				we: many ? 'we' : 'I',
				our: many ? 'our' : 'my',
				us: many ? 'us' : 'me',
			}
		},
		minimumMoveOutDate(){
			return getMoveOutDate(new Date());
		},
		maximumNoticeDate(){
			const noticeDate = getLatestNoticeDate(dateFromString(this.desiredMoveOutDate) || this.minimumMoveOutDate);
			// Add one day, because it must be delivered "before the 4th workday". February 4 -> "Before February 5"
			noticeDate.setDate(noticeDate.getDate() + 1);
			return noticeDate;
		},
		isDesiredMoveOutDateValid(){
			return new Date() < this.maximumNoticeDate;
		},
		effectiveMoveOutDate(){
			// Leases end on the last day of the month
			return this.isDesiredMoveOutDateValid && getMoveOutDate(this.maximumNoticeDate);
		},
		firstPersonName(){
			return this.people?.[0]?.fullName || '';
		}
	},
	methods: {
		addPerson(){
			this.people.push({
				id: Math.floor(Math.random() * 10000),
				fullName: this.people.length === 0 ? this.fullName : '',
			})
		},
		formatName,
		formatSalutations,
		formatLongDate,
		isoDay,
	},
	watch: {
		isDesiredMoveOutDateValid(isValid) {
			this.$refs.desiredMoveOutDatePicker.$el.setCustomValidity(isValid ? '' : "This move-out date is too early.");
		},
	},
	template: `
		<letter-generator
			aria-label="Lease termination letter generator"
			class="lease-termination-letter"
			track-as="Lease termination letter"
			:static="static">
			<template v-slot:header>Lease termination letter</template>

			<template v-slot:letter-recipient="{ language, stage }">
				<span class="letter-return-address">
					<blank placeholder="Your full name">{{ firstPersonName }}</blank>,
					<blank placeholder="your address">{{ address.replaceAll('\\n', ', ') }}</blank>
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
					<template v-if="firstPersonName"><strong>Name:</strong> {{ firstPersonName }}<br></template>
					<strong>Date:</strong> {{ currentDate.toLocaleDateString("en-US") }}
					<template v-if="address"><br>{{ address.replaceAll('\\n', ', ') }}</template>
				</template>
				<template v-if="language === 'de'">
					<strong>Name:</strong> <blank :key="uid('fullNameBlank')" placeholder="Your full name">{{ firstPersonName }}</blank><br>
					<strong>Datum:</strong> {{ currentDate.toLocaleDateString("de-DE") }}
					<template v-if="address"><br>{{ address.replaceAll('\\n', ', ') }}</template>
				</template>
			</template>

			<template v-slot:before-print-preview="{ language }">
				<p class="input-instructions" v-if="language == 'en'">Send the German version to your landlord.</p>
			</template>

			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Subject: Termination of {{ en.our }} lease agreement</strong>
					<br><blank :key="uid('addressBlank')" placeholder="Apartment address">{{ address.replaceAll('\\n', ', ') }}</blank>
				</p>
				<p v-if="language === 'de'">
					<strong>Betreff: Kündigung {{ de.unser }}es Mietvertrags</strong>
					<br><blank :key="uid('addressBlank')" placeholder="Apartment address">{{ address.replaceAll('\\n', ', ') }}</blank>
				</p>

				<p v-text="formatSalutations(recipientGender, recipientFirstName, recipientLastName, language)"></p>

				<p v-if="language === 'en'">
					I hereby terminate the rental agreement for the above-mentioned apartment
					<template v-if="customMoveOutDate">
						effective <blank :key="uid('desiredMoveOutDateBlankEn')" placeholder="Move-out date">{{ formatLongDate(desiredMoveOutDate, "en-US", true) }}</blank>.
					</template>
					<template v-else>
						at the earliest possible date.
					</template>
				</p>
				<p v-if="language === 'de'">
					hiermit kündige ich den Mietvertrag für die oben genannte Wohnung
					<template v-if="customMoveOutDate">
						unter Einhaltung der gesetzlichen Kündigungsfrist zum <blank :key="uid('desiredMoveOutDateBlankDe')" placeholder="Move-out date">{{ formatLongDate(desiredMoveOutDate, "de-DE", true) }}</blank>.
					</template>
					<template v-else>
						zum nächstmöglichen Termin.
					</template>
				</p>

				<template v-if="askForDepositReturn">
					<p v-if="language === 'en'">
						Please transfer the rental deposit with interest, as well as any credit balances from utility bills, to the following bank account:
					</p>
					<p v-if="language === 'de'">
						Bitte überweisen Sie die Mietkaution mit Zinsen sowie etwaige Guthaben aus Nebenkostenabrechnungen auf das folgende Bankkonto:
					</p>

					<p>
						{{ language === 'en' ? 'Account holder' : 'Kontoinhaber' }}:</strong> <blank :key="uid('bankAccountNameBlank')" placeholder="Full name">{{ bankAccountName || firstPersonName }}</blank>
						<br>
						IBAN: <blank :key="uid('bankAccountIBAN')" placeholder="Account IBAN">{{ bankAccountIBAN }}</blank>
					</p>
				</template>

				<p v-if="language === 'en'">
					Please confirm receipt of this termination and the effective end date of the lease in writing.
				</p>
				<p v-if="language === 'de'">
					Bitte bestätigen Sie den Erhalt dieser Kündigung und das Datum des Inkrafttretens der Kündigung schriftlich.
				</p>

				<p v-if="language === 'en'">
					Best regards,<br>
					<blank :key="uid('fullNameBlankEn')" placeholder="Your full name">{{ firstPersonName }}</blank>
				</p>
				<p v-if="language === 'de'">
					Mit freundlichen Grüßen,<br>
					<blank :key="uid('fullNameBlankDe')" placeholder="Your full name">{{ firstPersonName }}</blank>
				</p>

				<p v-for="person in people" :key="person.fullName"
					class="signature"
					v-if="stage === 'printPreview'"
					v-text="person.fullName"></p>

				<p class="signature" v-if="stage === 'printPreview'">Vermieter</p>
			</template>

			<template v-slot:form="{ language }">
				<div class="form-group">
					<label :for="uid('address')">Apartment address</label>
					<address-input :id="uid('address')" v-model="address" home required></address-input>
					<span class="input-instructions">The address of the apartment you are leaving</span>
				</div>
				<div class="form-group show-errors">
					<label :for="uid('desiredMoveOutDate')">Move-out date</label>
					<tabs
						aria-label="Move-out date"
						v-model="customMoveOutDate"
						:id="uid('customMoveOutDate')"
						:options="[{label: 'As soon as possible', value: false}, {label: 'Choose a date', value: true}]"
						required>
					</tabs>
					<date-picker
						ref="desiredMoveOutDatePicker"
						:min="isoDay(currentDate)"
						v-if="customMoveOutDate"
						v-model="desiredMoveOutDate"
						:id="uid('desiredMoveOutDate')"></date-picker>

					<span class="input-instructions" v-if="desiredMoveOutDate && isDesiredMoveOutDateValid">
						<template v-if="effectiveMoveOutDate !== desiredMoveOutDate">
							Leases usually end on the last day of the month.
						</template>
						Deliver this letter before {{ formatLongDate(maximumNoticeDate) }} to move out on {{ formatLongDate(effectiveMoveOutDate) }}.
					</span>
					<span class="input-instructions error" v-if="desiredMoveOutDate && !isDesiredMoveOutDateValid">
						The earliest move-out date is {{ formatLongDate(minimumMoveOutDate) }}. Ask your landlord if you can end your lease sooner.
					</span>
					</span>
					<span class="input-instructions" v-if="!desiredMoveOutDate">
						Deliver this letter before {{ formatLongDate(maximumNoticeDate) }} to move out on {{ formatLongDate(minimumMoveOutDate) }}.
					</span>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('fullName')">{{ people.length > 1 ? "Tenants' names" : "Your full name"}}</label>
					<full-name-input v-for="person in people" :id="uid('fullName')" v-model="person.fullName" required></full-name-input>
					<span class="input-instructions">
						Every tenant who signed the lease must sign this letter.
					</span>
					<a class="input-instructions" href="#" @click.prevent="addPerson">
						Add another tenant
					</a>
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
				<hr>
				<div class="form-group no-label">
					<checkbox v-model="askForDepositReturn"><span>Ask for your <glossary term="Kaution">deposit</glossary> back</span></checkbox>
				</div>
				<template v-if="askForDepositReturn">
					<hr>
					<p>Where should your landlord refund your deposit? Deposits are usually paid by <glossary term="SEPA-Überweisung">bank transfer</glossary>.</p>
					<div class="form-group">
						<label :for="uid('bankAccountName')">Bank account holder</label>
						<full-name-input :id="uid('bankAccountName')" v-model="bankAccountName" :placeholder="firstPersonName"></full-name-input>
					</div>
					<div class="form-group">
						<label :for="uid('bankAccountIBAN')"><glossary>IBAN</glossary></label>
						<input type="text"
							:id="uid('bankAccountIBAN')"
							v-model="bankAccountIBAN"
							placeholder="DE00 0000 0000 0000 0000 00">
					</div>
				</template>
			</template>
		</letter-generator>
	`
}
import AddressInput from '/js/vue/components/address-input.mjs';
import Blank from '/js/vue/components/blank.mjs';
import Checkbox from '/js/vue/components/checkbox.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';

import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default {
	components: {
		AddressInput,
		Blank,
		Checkbox,
		FullNameInput,
		Glossary,
		LetterGenerator,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin],
	props: {
		static: Boolean,
	},
	data(){
		return {
			fullName: userDefaults.empty,
			newAddress: '',
			isNewAddressAbroad: true,
			backupRecipient: '',
			backupAddress: '',
		};
	},
	computed: {
		fullNewAddress(){
			if(!this.fullName){
				return this.newAddress.replaceAll('\n', '<br>');
			}
			return `${this.fullName}<br>${this.newAddress.replaceAll('\n', '<br>')}`;
		},
		fullBackupAddress() {
			if(!this.isNewAddressAbroad || !this.backupAddress){
				return null;
			}

			const recipient = this.backupRecipient ? `${this.fullName}<br>bei ${this.backupRecipient}` : this.fullName;

			return `${recipient}<br>${this.backupAddress.replaceAll('\n', '<br>')}`;
		},
	},
	template: `
		<letter-generator
			aria-label="Letter generator to deregister your address"
			track-as="Abmeldung email"
			:printable="false"
			:static="static">
			<template v-slot:header>Abmeldung – Deregister your address</template>
			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Subject: Address deregistration</strong>
				</p>
				<p v-if="language === 'de'">
					<strong>Betreff: Abmeldung einer Wohnung</strong>
				</p>

				<p v-if="language === 'en'">Dear sir or madam,</p>
				<p v-if="language === 'de'">Sehr geehrte Damen und Herren,</p>

				<p v-if="language === 'en'">
					I hereby wish to deregister my address following my move. Please find enclosed the completed deregistration form and a copy of my identity card.
				</p>
				<p v-if="language === 'de'">
					hiermit melde ich meine Wohnung ab. Im Anhang finden Sie das Abmeldeformular und eine Kopie meines Personalausweises.
				</p>

				<p v-if="language === 'en'">
					Please send me the confirmation of deregistration by email. If this is not possible, please send it to my new address. If it is not possible to send it abroad, please send it to the following person in Germany:
				</p>
				<p v-if="language === 'de'">
					Bitte senden Sie mir die Abmeldebestätigung per E-Mail zu. Falls das nicht möglich ist, senden Sie sie bitte an meine neue Adresse. Sollte ein Versand ins Ausland nicht möglich sein, senden Sie sie bitte an folgende Person in Deutschland:
				</p>

				<p>
					<strong v-if="language === 'en'">New address:</strong>
					<strong v-if="language === 'de'">Neue Adresse:</strong>
					<br>
					<blank :key="uid('newAddressBlank')" placeholder="Your new address" v-if="!newAddress"></blank>
					<span v-else v-html="fullNewAddress"></span>
				</p>

				<p v-if="isNewAddressAbroad">
					<strong v-if="language === 'en'">Alternative address in Germany:</strong>
					<strong v-if="language === 'de'">Alternative Lieferadresse in Deutschland:</strong>
					<br>
					<blank :key="uid('backupAddressBlank')" placeholder="Backup address in Germany" v-if="!fullBackupAddress"></blank>
					<span v-else v-html="fullBackupAddress"></span>
				</p>

				<p>
					<template v-if="language === 'en'">Best regards,</template>
					<template v-if="language === 'de'">Mit freundlichen Grüßen,</template>
					<br>
					<blank :key="uid('fullNameBlank')" placeholder="Your name">{{ fullName }}</blank>
				</p>
			</template>

			<template v-slot:form>
				<div class="form-group">
					<label :for="uid('fullName')">Your full name</label>
					<full-name-input :id="uid('fullName')" v-model="fullName" required></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('newAddress')">Your new address</label>
					<address-input :id="uid('newAddress')" v-model="newAddress" :abroad="isNewAddressAbroad" :home="!isNewAddressAbroad" required></address-input>
					<checkbox v-model="isNewAddressAbroad">This address is in another country</checkbox>
				</div>
				<template v-if="isNewAddressAbroad">
					<hr>
					<p>
						The <glossary>Bürgeramt</glossary> might refuse to mail your <glossary>Abmeldebescheinigung</glossary> to another country.
						Give them a backup German address where they can mail it.
					</p>
					<div class="form-group">
						<label :for="uid('backupRecipient')">Backup recipient</label>
						<full-name-input :id="uid('backupRecipient')" v-model="backupRecipient" :placeholder="fullName" autocomplete="off"></full-name-input>
						<span class="input-instructions">This must be a person, not a business. That name must be on the mailbox.</span>
					</div>
					<div class="form-group">
						<label :for="uid('backupAddress')">Backup address</label>
						<address-input :id="uid('backupAddress')" v-model="backupAddress" home></address-input>
						<span class="input-instructions">This must be an address in Germany.</span>
						<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#how-to-write-german-addresses" target="_blank">How to write your address</a>
					</div>
				</template>
			</template>
		</letter-generator>
	`,
}
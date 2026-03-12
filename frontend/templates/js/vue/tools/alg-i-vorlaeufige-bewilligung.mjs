import AddressInput from '/js/vue/components/address-input.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import GenderInput from '/js/vue/components/gender-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import LetterGenerator from '/js/vue/components/letter-generator.mjs';
import { formatName, formatSalutations } from '/js/utils/letter.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';

export default{
	components: {
		AddressInput,
		FirstNameInput,
		FullNameInput,
		GenderInput,
		Glossary,
		LastNameInput,
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
			agenturFurArbeitAddress: '',
			recipientGender: 'man',
			recipientFirstName: '',
			recipientLastName: '',
			caseNumber: '',
			currentDate: new Date(),
		};
	},
	methods: {
		formatName,
		formatSalutations,
	},
	template: `
		<letter-generator
			aria-label="Letter generator to request a preliminary decision for ALG I"
			track-as="ALG I vorläufige Bewilligung"
			:static="static">
			<template v-slot:header>ALG I – Request a preliminary decision</template>

			<template v-slot:letter-recipient="{ language, stage }">
				<span class="letter-return-address" v-if="address">
					{{ fullName }}<template v-if="fullName && address">, </template>
					{{ address.replaceAll('\\n', ', ') }}
				</span>

				<template v-if="formatName(recipientGender, recipientFirstName, recipientLastName, language)">
					{{ formatName(recipientGender, recipientFirstName, recipientLastName, language) }}<br>
				</template>
				<span v-html="agenturFurArbeitAddress.replaceAll('\\n', '<br>')"></span>
			</template>

			<template v-slot:letter-details="{ language, stage }">
				<template v-if="language === 'en'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Date:</strong> {{ currentDate.toLocaleDateString("en-US") }}
					<template v-if="caseNumber"><br><strong>Case number: </strong> {{ caseNumber }}</template>
				</template>
				<template v-if="language === 'de'">
					<template v-if="fullName"><strong>Name:</strong> {{ fullName }}<br></template>
					<strong>Datum:</strong> {{ currentDate.toLocaleDateString("de-DE") }}
					<template v-if="caseNumber"><br><strong>Aktenzeichen: </strong> {{ caseNumber }}</template>
				</template>
			</template>

			<template v-slot:letter-body="{ language, stage }">
				<p v-if="language === 'en'">
					<strong>Subject: Request for preliminary decision (ALG I)</strong>
				</p>
				<p v-if="language === 'de'">
					<strong>Betreff: Antrag auf vorläufige Entscheidung (ALG I)</strong>
				</p>

				<p v-text="formatSalutations(recipientGender, recipientFirstName, recipientLastName, language)"></p>

				<p v-if="language === 'en'">
					Since the processing of my application requires more time, I hereby submit an application for a provisional decision in accordance with § 328 paragraph 1 sentence 3 SGB III, i.e. a provisional grant of unemployment benefits. The requirements for my unemployment benefits claim are met with sufficient probability. I am not responsible for the circumstances that still stand in the way of an immediate final decision.
				</p>
				<p v-if="language === 'de'">
					da die Bearbeitung meines Antrages noch Zeit benötigt, stelle ich hiermit einen Antrag auf vorläufige Entscheidung nach § 328 Abs. 1 Satz 1 Nr. 3 SGB III, d.h. eine vorläufige Arbeitslosengeldgewährung. Die Voraussetzungen für meinen Arbeitslosengeldanspruch liegen mit hinreichender Wahrscheinlichkeit vor. Die Umstände, die einer sofortigen abschließenden Entscheidung noch entgegenstehen, habe ich nicht zu vertreten.
				</p>

				<p v-if="language === 'en'">
					According to § 328 Para. 1 Sentence 1 No. 3 SGB III, a provisional decision is to be made on application in accordance with the law, i.e. you do not have any discretion in this respect. I request that you make a decision within 3 weeks of receipt of this application.
				</p>
				<p v-if="language === 'de'">
					In den Fällen des § 328 Abs. 1 Satz 1 Nr. 3 SGB III ist auf Antrag nach der gesetzlichen Regelung vorläufig zu entscheiden, d.h. ein Ermessen steht Ihnen insoweit nicht zu. Ich bitte um Erteilung eines Leistungsbescheides binnen 3 Wochen ab Zugang dieses Antrags.
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

			<template v-slot:form>
				<div class="form-group">
					<label :for="uid('fullName')">Your full name</label>
					<full-name-input :id="uid('fullName')" v-model="fullName"></full-name-input>
				</div>
				<div class="form-group">
					<label :for="uid('address')">Your address</label>
					<address-input :id="uid('address')" v-model="address" home></address-input>
				</div>
				<div class="form-group">
					<label :for="uid('agenturFurArbeitAddress')">Agentur für Arbeit address</label>
					<address-input :id="uid('agenturFurArbeitAddress')" v-model="agenturFurArbeitAddress" :placeholder="'Agentur für Arbeit Mitte\\nnMusterstraße 123\\n12345 Berlin'"></address-input>
					<a class="input-instructions external-link" href="https://web.arbeitsagentur.de/portal/metasuche/suche/dienststellen" target="_blank">
						Find your Agentur für Arbeit
					</a>
				</div>
				<div class="form-group">
					<span class="label">Case worker</span>
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
						<span class="input-instructions">
							This is the employee who helps you at the <glossary>Agentur für Arbeit</glossary>.
						</span>
					</div>
				</div>
				<div class="form-group">
					<label :for="uid('caseNumber')">Case number</label>
					<input type="text" :id="uid('caseNumber')" v-model="caseNumber">
					<span class="input-instructions">
						This helps the <glossary>Agentur für Arbeit</glossary> find your information.
					</span>
				</div>
			</template>
		</letter-generator>
	`
}
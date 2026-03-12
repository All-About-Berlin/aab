import Checkbox from '/js/vue/components/checkbox.mjs';
import CityInput from '/js/vue/components/city-input.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconCalendar from '/js/vue/components/icons/calendar.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconInterpreter from '/js/vue/components/icons/interpreter.mjs';
import IconPdf from '/js/vue/components/icons/pdf.mjs';
import IconRepresentative from '/js/vue/components/icons/representative.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import PostalcodeInput from '/js/vue/components/postalcode-input.mjs';
import StateInput from '/js/vue/components/state-input.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import preloadPdfMixin from '/js/vue/mixins/preloadPdf.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { formatDate } from '/js/utils/date.mjs';
import { mergeFields } from '/js/utils/letter.mjs';
import { countriesInGerman } from '/js/utils/countries.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { getNearestHeadingId } from '/js/utils/tracking.mjs';
import { fillAndSavePDF } from '/js/utils/pdf.mjs';

export default {
	components: {
		Checkbox,
		CityInput,
		Collapsible,
		CountryInput,
		DatePicker,
		FirstNameInput,
		Glossary,
		IconCalendar,
		IconDonate,
		IconInterpreter,
		IconPdf,
		IconRepresentative,
		LastNameInput,
		PostalcodeInput,
		StateInput,
		Tabs,
	},
	mixins: [uniqueIdsMixin, multiStageMixin, trackedStagesMixin, preloadPdfMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			trackAs: 'Anmeldung form',

			moveInDate: '',
			newAddress: '',
			newBuildingDetails: '',
			newPostCode: '',
			oldAddress: '',
			oldBuildingDetails: '',
			oldCity: '',
			oldPostCode: '',
			oldCountry: '',
			oldState: '',
			people: [],
			namesAreOnMailbox: true,
			nameOnMailbox: '',
			stages: [
				'start',
				'newAddress',
				'oldAddress',
				'addPeople',
				'beiAddress',
				'idDocuments',
				'options',
			],
			inputsToFocus: {
				start: () => this.$refs.startButton,
				newAddress: () => this.$refs.newAddressInput,
				oldAddress: () => this.$refs.oldAddressCountryInput.$el,
				addPeople: () => this.$refs.firstNameInput[0].$el,
				beiAddress: () => this.$refs.namesAreOnMailboxCheckbox.$el.querySelector('input'),
			},
			downloadInProgress: false,
			pdfUrl: '/documents/anmeldung-original.pdf',
		};
	},
	computed: {
		peoplePairs(){
			// Split this.people in arrays of two people
			return this.people
				.slice(this.people.length/2)
				.map((_,i) => this.people.slice(i*=2,i+2));
		},
	},
	methods: {
		addPerson(){
			this.people.push({
				id: Math.floor(Math.random() * 10000),
				title: '',
				firstName: '',
				lastName: '',
				birthName: '',
				nationality: userDefaults.empty,
				religion: userDefaults.empty,
				dateOfBirth: userDefaults.empty,
				gender: '',
				birthPlace: '',
				showExtraFields: false,
				documentType: 'RP',
				documentNumber: '',
				documentIssueDate: '',
				documentIssuingAuthority: '',
				documentExpirationDate: '',
			})
		},
		personName(person, index){
			if(person.firstName || person.lastName){
				return [person.firstName, person.lastName].filter(Boolean).join(' ');
			}
			return `person #${index}`;
		},
		async generatePDF(person1, person2){
			this.downloadInProgress = true;

			let beiAddress = this.namesAreOnMailbox ? '' : `bei ${this.nameOnMailbox}`;
			const textFields = {
				'Tag des EinzugsRow1': formatDate(this.moveInDate, 'de-DE'),
				'Tag des AuszugsRow1': formatDate(this.moveInDate, 'de-DE'),
				'Straße Hausnummer ZusätzeRow1': mergeFields([
					this.newAddress,
					this.newBuildingDetails,
					beiAddress
				]),
				'Postleitzahl Gemeinde OrtsteilRow1': mergeFields([
					this.newPostCode,
					'Berlin'
				]),
				'Straße Hausnummer ZusätzeRow1_2': mergeFields([
					this.oldAddress,
					this.oldBuildingDetails
				]),
				'Postleitzahl GemeindeKreisLandRow1': mergeFields([
					this.oldPostCode,
					this.oldCity,
					this.oldState.toUpperCase() // Just the abbreviation
				]),
				'Bei Zuzug aus dem Ausland StaatRow1': this.oldCountry === 'DE' ? '' : countriesInGerman[this.oldCountry],
			};
			const checkboxFields = {
				'alleinige': true,
				'alleinige_2': true,
				'Nein': true,
				'Nein_2': true,
			};

			if(person1){
				textFields['Familienname ggf Doktorgrad Passname'] = mergeFields([
					person1.lastName,
					person1.title
				]);
				textFields['Vornamen Rufnamen unterstreichen'] = person1.firstName;
				textFields['Geburtsname'] = person1.birthName;
				textFields['Geschlecht'] = person1.gender;
				textFields['Tag Ort Land der Geburt'] = mergeFields([
					formatDate(person1.dateOfBirth, 'de-DE'),
					person1.birthPlace
				]);
				textFields['Religionsgesellschaft'] = person1.religion;
				textFields['Staatsangehörigkeiten'] = countriesInGerman[person1.nationality];
				textFields['OrdensKünstlername'] = person1.artistName;

				textFields['ArtRow1'] = person1.documentType;
				textFields['AusstellungsbehördeRow1'] = person1.documentIssuingAuthority;
				textFields['SeriennummerRow1'] = person1.documentNumber;
				textFields['DatumRow1'] = formatDate(person1.documentIssueDate, 'de-DE');
				textFields['gültig bisRow1'] = formatDate(person1.documentExpirationDate, 'de-DE');
				textFields['Name Vorname'] = mergeFields([
					person1.lastName,
					person1.firstName
				]);
			}

			if(person2){
				textFields['Familienmitglied istFamilienname ggf Doktorgrad Passname'] = mergeFields([
					person2.lastName,
					person2.title
				]);
				textFields['Familienmitglied istVornamen Rufnamen unterstreichen'] = person2.firstName;
				textFields['Familienmitglied istGeburtsname'] = person2.birthName;
				textFields['Familienmitglied istGeschlecht'] = person2.gender;
				textFields['Familienmitglied istTag Ort Land der Geburt'] = mergeFields([
					formatDate(person2.dateOfBirth, 'de-DE'),
					person2.birthPlace
				]);
				textFields['Familienmitglied istReligionsgesellschaft'] = person2.religion;
				textFields['Familienmitglied istStaatsangehörigkeiten'] = countriesInGerman[person2.nationality];
				textFields['Familienmitglied istOrdensKünstlername'] = person2.artistName;

				textFields['ArtRow1_2'] = person2.documentType;
				textFields['AusstellungsbehördeRow1_2'] = person2.documentIssuingAuthority;
				textFields['SeriennummerRow1_2'] = person2.documentNumber;
				textFields['DatumRow1_2'] = formatDate(person2.documentIssueDate, 'de-DE');
				textFields['gültig bisRow1_2'] = formatDate(person2.documentExpirationDate, 'de-DE');
				textFields['Name Vorname_2'] = mergeFields([
					person2.lastName,
					person2.firstName
				]);
			}

			await fillAndSavePDF(this.pdfUrl, textFields, checkboxFields, null, 'anmeldung-form-filled.pdf', this.trackAs, getNearestHeadingId(this.$el));
			this.downloadInProgress = false;
		}
	},
	watch: {
		newPostCode(newVal) {
			const postalCodeIsValid = parseInt(newVal, 10) > 10100 && parseInt(newVal, 10) < 14200;
			try{
				this.$refs.newPostCodeInput.$el.setCustomValidity(postalCodeIsValid ? '' : 'This is not a valid Berlin post code.');
			} catch (e) {}
		},
	},
	created() {
		this.addPerson();
	},
	template: `
		<collapsible
			aria-label="Tool to fill the Anmeldung form"
			class="anmeldung-form"
			:static="static">
			<template v-slot:header>
				<small>Fill the form online</small>
				Anmeldung form
			</template>
			<progress v-if="stage !== 'start'" aria-label="Form progress" :max="stages.length - 1" :value="stageIndex"></progress>
			<template v-if="stage === 'start'">
				<picture>
					<source srcset="/documents/anmeldung-original.webp 1600w, /documents/previews/anmeldung-original.webp 300w, /documents/previews2x/anmeldung-original.webp 600w" type="image/webp">
					<source srcset="/documents/previews/anmeldung-original.png 300w, /documents/previews2x/anmeldung-original.png 600w" type="image/png">
					<img alt="Berlin Anmeldung form" loading="lazy" src="/documents/previews/anmeldung-original.png">
				</picture>
				<p>This tool helps you <strong>fill the <glossary>Anmeldung</glossary> form</strong> in 3 minutes. You can save the completed form, print it, and bring it to your <glossary>Bürgeramt</glossary> appointment.</p>
				<p>Your personal information stays on your computer. No one else can see it.</p>
			</template>
			<template v-if="stage === 'newAddress'">
				<h2>Your new address</h2>
				<p>Where are you moving? Enter the address that you want to register.</p>
				<hr>
				<div class="form-group">
					<label :for="uid('newAddress')">Street address</label>
					<input
						:id="uid('newAddress')"
						ref="newAddressInput"
						type="text"
						v-model="newAddress"
						placeholder="Neue Straße 123"
						autocomplete="address-line1"
						required>
				</div>
				<div class="form-group">
					<label :for="uid('newPostCode')">
						<glossary term="Postleitzahl">Post code</glossary> and city
					</label>
					<div class="input-group">
						<postalcode-input ref="newPostCodeInput" :id="uid('newPostCode')" v-model="newPostCode" required></postalcode-input>
						Berlin
					</div>
				</div>
				<div class="form-group">
					<label :for="uid('newBuildingDetails')">Building details</label>
					<input
						:id="uid('newBuildingDetails')"
						type="text"
						v-model="newBuildingDetails"
						placeholder="Haus B, 2. Etage rechts"
						autocomplete="address-line2">
					<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#extra-information" target="_blank">How to write your building details</a>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('moveInDate')">Move-in date</label>
					<date-picker v-model="moveInDate" :id="uid('moveInDate')" required></date-picker>
					<span class="input-instructions">Use the same date as on your <em><glossary>Wohnungsgeberbestätigung</glossary></em>.</span>
				</div>
			</template>
			<template v-if="stage === 'oldAddress'">
				<h2>Your previous address</h2>
				<p>Where did you live before? Your old address be deregistered automatically.</p>
				<hr>
				<div class="form-group">
					<label :for="uid('oldCountry')">Country</label>
					<country-input
						country-code
						v-model="oldCountry"
						ref="oldAddressCountryInput"
						:id="uid('oldCountry')"
						placeholder="Country of your previous address"
						:aria-describedby="uid('oldCountry-instructions')"
						required></country-input>
					<span v-if="oldCountry && oldCountry !== 'DE'" :id="uid('oldCountry-instructions')" class="input-instructions">You don't need to share your foreign address.</span>
				</div>
				<template v-if="oldCountry === 'DE'">
					<div class="form-group">
						<label :for="uid('oldAddress')">Street address</label>
						<input
							:id="uid('oldAddress')"
							type="text"
							v-model="oldAddress"
							placeholder="Alte Straße 12"
							autocomplete="address-line1"
							required>
					</div>
					<div class="form-group">
						<label :for="uid('oldPostCode')">
							<glossary term="Postleitzahl">Post code</glossary> and city
						</label>
						<div class="input-group">
							<postalcode-input :id="uid('oldPostCode')" v-model="oldPostCode" required></postalcode-input>
							<city-input v-model="oldCity" required></city-input>
						</div>
					</div>
					<div class="form-group">
						<label :for="uid('oldBuildingDetails')">Building details</label>
						<input
							:id="uid('oldBuildingDetails')"
							type="text"
							v-model="oldBuildingDetails"
							placeholder="Haus B, 2. Etage rechts"
							autocomplete="address-line2">
					</div>
					<div class="form-group">
						<label :for="uid('germanState')">
							State
						</label>
						<state-input :id="uid('germanState')" v-model="oldState" required></state-input>
					</div>
				</template>
			</template>
			<template v-if="stage === 'addPeople'">
				<h2>Who is registering?</h2>
				<p>You can register your whole family at the same time.</p>
				<template v-for="(person, index) in people">
					<hr>
					<div class="form-group" v-if="person.showExtraFields">
						<label :for="uid('title') + person.id">Title</label>
						<input type="text"
							:id="uid('title') + person.id"
							v-model="person.title"
							autocomplete="honorific-prefix"
							placeholder="Dr."
							class="anrede-input">
					</div>
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
						<span class="label">Gender</span>
						<tabs
							aria-label="Gender"
							v-model="person.gender"
							:id="uid('gender-' + person.id)"
							:options="[{label: 'Male', value: 'Männlich'}, {label: 'Female', value: 'Weiblich'}, {label: 'Other', value: 'Divers'}]"
							required>
						</tabs>
					</div>
					<div class="form-group">
						<label :for="uid('nationality-' + person.id)">Nationality</label>
						<country-input
							country-code
							v-model="person.nationality"
							ref="oldAddressCountryInput"
							:id="uid('nationality-' + person.id)"
							required></country-input>
					</div>
					<div class="form-group">
						<label :for="uid('religion-' + person.id)">Religion</label>
						<select :id="uid('religion-' + person.id)" v-model="person.religion" :aria-describedby="uid('religion-instructions-' + person.id)"  :class="{placeholder: !person.religion}" required>
							<option disabled hidden default :value="null">Choose a church</option>
							<option value="Evangelische Kirche">Evangelical Church</option>
							<option value="Römisch-katholische Kirche">Roman Catholic Church</option>
							<option value="Jüdische Gemeinde">Jewish Community</option>
							<option value="Altkatholische Kirche">Old Catholic Church</option>
							<option value="Freireligiöse Gemeinden">Free Religious communities</option>
							<option disabled>──────────</option>
							<option value="Sonstiges, nicht kirchensteuerpflichtig">Other / No religion</option>
						</select>
						<span :id="uid('religion-instructions-' + person.id)" class="input-instructions">Members of some churches must pay the <glossary term="Kirchensteuer">church tax</glossary>.</span>
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
				<checkbox v-model="namesAreOnMailbox" ref="namesAreOnMailboxCheckbox">
					{{ people.length > 1 ? 'Our names are on our mailbox' : 'My name is on my mailbox' }}
				</checkbox>
				<p v-if="!namesAreOnMailbox">If your name is not on your mailbox, you must <a href="/guides/anmeldung-in-english-berlin#if-your-name-is-not-on-your-mailbox" target="_blank">add “c/o” or “bei” to your address</a>. This tells postal workers to put your mail in another person's mailbox.</p>
				<div class="form-group" v-if="!namesAreOnMailbox">
					<label :for="uid('nameOnMailbox')">Name on mailbox</label>
					<input :id="uid('nameOnMailbox')" type="text" v-model="nameOnMailbox" placeholder="Max Mustermann" required>
				</div>
			</template>
			<template v-if="stage === 'idDocuments'">
				<h2>ID documents</h2>
				<p>During your <em>Anmeldung</em> appointment, you must prove your identity. Which documents will you use?</p>
				<template v-for="(person, index) in people">
					<hr>
					<h3 v-if="people.length > 1">ID document for {{ personName(person, index + 1) }}</h3>
					<div class="form-group">
						<span class="label">
							Document type
						</span>
						<tabs
							aria-label="Document type"
							v-model="person.documentType"
							:id="uid('documentType-' + person.id)"
							:options="[{label: 'Passport', value: 'RP'}, {label: 'Personal ID', value: 'PA'}]"
							required>
						</tabs>
					</div>
					<div class="form-group">
						<label :for="uid('documentType-' + person.id)">
							{{ person.documentType === 'RP' ? 'Passport' : 'ID card' }} number
						</label>
						<input
							class="documentnumber-input"
							ztype="text"
							v-model="person.documentNumber"
							:id="uid('documentType-' + person.id)"
							:placeholder="person.documentType === 'RP' ? 'AB12345678' : 'A12B34C56'"
							required>
					</div>
					<div class="form-group">
						<label :for="uid('documentIssueDate-' + person.id)">Date issued</label>
						<date-picker :key="person.id" :id="uid('documentIssueDate-' + person.id)" v-model="person.documentIssueDate" required></date-picker>
					</div>
					<div class="form-group" v-if="person.documentType === 'PA'">
						<label :for="uid('documentIssuingAuthority-' + person.id)">Issuing authority</label>
						<input type="text" placeholder="Berlin" :id="uid('documentIssuingAuthority-' + person.id)" v-model="person.documentIssuingAuthority" required>
						<span class="input-instructions" >It's written on the back of your ID card.</span>
					</div>
					<div class="form-group" v-if="person.documentType !== 'PA'">
						<label :for="uid('documentIssuingAuthority-' + person.id)">Issuing authority</label>
						<input type="text" placeholder="Ottawa" :id="uid('documentIssuingAuthority-' + person.id)" v-model="person.documentIssuingAuthority" required>
						<span class="input-instructions" v-if="person.documentType !== 'PA'">It's written in your passport, on the photo page.</span>
					</div>
					<div class="form-group">
						<label :for="uid('documentExpirationDate-' + person.id)">Expiration date</label>
						<date-picker :key="person.id" :id="uid('documentExpirationDate-' + person.id)" v-model="person.documentExpirationDate" required></date-picker>
					</div>
				</template>
			</template>
			<template v-if="stage === 'options'">
				<h2>You are almost done!</h2>
				<template v-if="peoplePairs.length > 1">
					<p>Print these forms, sign them, and bring them to your <em>Anmeldung</em> appointment.</p>
					<ul class="buttons list">
						<li v-for="([person1, person2], index) in peoplePairs">
							<button :aria-labelledby="uid('h-btnDownload') + index" @click="generatePDF(person1, person2)" :disabled="downloadInProgress">
								<icon-pdf/>
								<div>
									<h3 :id="uid('h-btnDownload') + index">Download your Anmeldung form (part {{ index + 1 }})</h3>
									<p v-if="person1.firstName">For {{ person1.firstName }}<template v-if="person2"> and {{ person2.firstName }}</template>.</p>
								</div>
							</button>
						</li>
					</ul>
				</template>
				<ul class="buttons list">
					<li v-if="peoplePairs.length === 1">
						<button @click="generatePDF(people[0], people[1])" :disabled="downloadInProgress" :aria-labelledby="uid('h-btnDownload')">
							<icon-pdf/>
							<div>
								<h3 :id="uid('h-btnDownload')">Download your Anmeldung form</h3>
								<p>Print and sign this form, and bring it to your <em>Anmeldung</em> appointment.</p>
							</div>
						</button>
					</li>
				</ul>
				<h3>What to do next</h3>
				<p>To register your address, you must book a Bürgeramt appointment and go there in person. You can also send someone else to do it for you.</p>
				<ul class="buttons list">
					<li>
						<a href="/guides/anmeldung-in-english-berlin#get-a-burgeramt-appointment" target="_blank">
							<icon-calendar/>
							<div>
								<h3>Book a Bürgeramt appointment</h3>
								<p>You need an appointment to register your address.</p>
							</div>
						</a>
					</li>
					<li>
						<a href="/out/red-tape-translation-interpreter" target="_blank">
							<icon-interpreter/>
							<div>
								<h3>Hire a translator</h3>
								<p>Bring a German speaker to your <em>Anmeldung</em> appointment.</p>
							</div>
						</a>
					</li>
					<li>
						<a href="/out/red-tape-translation-anmeldung" target="_blank">
							<icon-representative/>
							<div>
								<h3>Pay someone to register you</h3>
								<p>Let an expert do your <em>Anmeldung</em>, get your <glossary term="Anmeldebestätigung">registration certificate</glossary> by email.</p>
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
					@click="nextStage">Continue <i class="icon right" aria-hidden="true"></i></button>
				<button v-if="stageIndex === stages.length - 2" class="button primary" @click="nextStage">Finish</button>
			</div>
		</collapsible>
	`
}
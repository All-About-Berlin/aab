import Collapsible from '/js/vue/components/collapsible.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import Eur from '/js/vue/components/eur.mjs';
import FirstNameInput from '/js/vue/components/first-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconCalendar from '/js/vue/components/icons/calendar.mjs';
import IconExit from '/js/vue/components/icons/exit.mjs';
import IconMail from '/js/vue/components/icons/mail.mjs';
import IconPdf from '/js/vue/components/icons/pdf.mjs';
import IconRepresentative from '/js/vue/components/icons/representative.mjs';
import LastNameInput from '/js/vue/components/last-name-input.mjs';
import PostalcodeInput from '/js/vue/components/postalcode-input.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import preloadPdfMixin from '/js/vue/mixins/preloadPdf.mjs';
import { mergeFields } from '/js/utils/letter.mjs';
import { countriesInGerman } from '/js/utils/countries.mjs';
import { formatDate } from '/js/utils/date.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { getNearestHeadingId } from '/js/utils/tracking.mjs';
import { fillAndSavePDF } from '/js/utils/pdf.mjs';

export default {
	components: {
		Collapsible,
		CountryInput,
		DatePicker,
		Eur,
		FirstNameInput,
		Glossary,
		IconCalendar,
		IconExit,
		IconMail,
		IconPdf,
		IconRepresentative,
		LastNameInput,
		PostalcodeInput,
		Tabs,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, multiStageMixin, trackedStagesMixin, preloadPdfMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			trackAs: 'Abmeldung form',

			moveOutDate: '',
			oldAddress: '',
			oldBuildingDetails: '',
			oldPostCode: '',
			newAddress: '',
			newCityAndPostCode: '',
			newCountry: userDefaults.empty,
			people: [],

			stages: [
				'start',
				'oldAddress',
				'newAddress',
				'addPeople',
				'offlineFinish',
			],
			inputsToFocus: {
				start: () => this.$refs.startButton,
				oldAddress: () => this.$refs.oldAddressInput,
				newAddress: () => this.$refs.newAddressInput,
				addPeople: () => this.$refs.firstNameInput[0].$el,
			},
			downloadInProgress: false,
			pdfUrl: '/documents/abmeldung-original.pdf',
		};
	},
	computed: {
		peopleTriples(){
			// Split this.people in arrays of 3 people
			const peopleGroups = [];
			for(let i = 0; i < this.people.length / 3; i++){
				peopleGroups.push(this.people.slice(i*3, i*3 + 3));
			}
			return peopleGroups;
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
				nationality: null,
				religion: null,
				dateOfBirth: '',
				gender: '',
				birthPlace: '',
				showExtraFields: false,
			})
		},
		async generatePDF(person1, person2, person3){
			this.downloadInProgress = true;
			const textFields = {
				'Tag des Auszugs': formatDate(this.moveOutDate, 'de-DE'),
				'Postleitzahl Gemeinde Ortsteil bisherige Wohnung': mergeFields([
					this.oldPostCode,
					'Berlin'
				]),
				'Straße Hausnummer Zusätze bisherige Wohnung': mergeFields([
					this.oldAddress,
					this.oldBuildingDetails
				]),
				'Postleitzahl Gemeinde Kreis Land (falls Ausland: Staat) künftige Wohnung': mergeFields([
					this.newCityAndPostCode,
					countriesInGerman[this.newCountry]
				]),
				'Straße Hausnummer Zusätze künftige Wohnung': this.newAddress,
			};
			const checkboxFields = {
				'bisherige Wohnung war alleinige Wohnung': true,
				'nein': true,
				'künftige Wohunung wird alleinige Wohnung': true,
			};

			if(person1){
				textFields['Person 1 Familienname ggf Doktorgrad Zeile 1'] = mergeFields([
					person1.lastName,
					person1.title
				]);
				textFields['Person 1 Vornamen Rufnamen unterstreichen'] = person1.firstName;
				textFields['Person 1 Geburtsname'] = person1.birthName;
				textFields['Person 1 Geschlecht'] = person1.gender;
				textFields['Person 1 Tag Ort Land der Geburt'] = mergeFields([
					formatDate(person1.dateOfBirth, 'de-DE'),
					person1.birthPlace
				]);
				textFields['Person 1 Religionsgesellschaft'] = person1.religion;
				textFields['Person 1 Staatsangehörigkeiten'] = countriesInGerman[person1.nationality];
				textFields['Person 1 Ordens- Künstlername'] = person1.artistName;
			}

			if(person2){
				textFields['Person 2 Familienmitglied ist Familienname ggf Doktorgrad'] = mergeFields([
					person2.lastName,
					person2.title
				]);
				textFields['Person 2 Familienmitglied ist Vornamen Rufnamen unterstreichen'] = person2.firstName;
				textFields['Person 2 Familienmitglied ist Geburtsname'] = person2.birthName;
				textFields['Person 2 Familienmitglied istGeschlecht'] = person2.gender;
				textFields['Person 2 Familienmitglied ist Tag Ort Land der Geburt'] = mergeFields([
					formatDate(person2.dateOfBirth, 'de-DE'),
					person2.birthPlace
				]);
				textFields['Person 2 Familienmitglied ist Religionsgesellschaft'] = person2.religion;
				textFields['Person 2 Familienmitglied ist Staatsangehörigkeiten'] = countriesInGerman[person2.nationality];
				textFields['Person 2 Familienmitglied ist Ordens- Künstlername'] = person2.artistName;
			}

			if(person3){
				textFields['Person 3 Familienmitglied ist Familienname ggf Doktorgrad'] = mergeFields([
					person3.lastName,
					person3.title
				]);
				textFields['Person 3 Familienmitglied ist Vornamen Rufnamen unterstreichen'] = person3.firstName;
				textFields['Person 3 Familienmitglied ist Geburtsname'] = person3.birthName;
				textFields['Person 3 Familienmitglied ist Geschlecht'] = person3.gender;
				textFields['Person 3 Familienmitglied ist Tag Ort Land der Geburt'] = mergeFields([
					formatDate(person3.dateOfBirth, 'de-DE'),
					person3.birthPlace
				]);
				textFields['Person 3 Familienmitglied ist Religionsgesellschaft'] = person3.religion;
				textFields['Person 3 Familienmitglied istStaatsangehörigkeiten'] = countriesInGerman[person3.nationality];
				textFields['Person 3 Familienmitglied ist OrdensKünstlername'] = person3.artistName;
			}

			await fillAndSavePDF(this.pdfUrl, textFields, checkboxFields, null, 'abmeldung-form-filled.pdf', this.trackAs, getNearestHeadingId(this.$el));
			this.downloadInProgress = false;
		},
	},
	watch: {
		oldPostCode(newVal) {
			const postalCodeIsValid = parseInt(newVal, 10) > 10100 && parseInt(newVal, 10) < 14200;
			try{
				this.$refs.oldPostCodeInput.$el.setCustomValidity(postalCodeIsValid ? '' : 'This is not a valid Berlin post code.');
			} catch (e) {}
		},
		newCountry(newVal) {
			try{
				this.$refs.newCountryInput.$el.setCustomValidity(newVal === 'DE' ? "You probably don't need to deregister." : '');
			} catch (e) {}
		},
	},
	created() {
		this.addPerson();
	},
	template: `
		<collapsible
			aria-label="Tool to fill the Abmeldung form"
			class="abmeldung-form"
			:static="static">

			<template v-slot:header>
				<small>Fill the form online</small>
				Abmeldung form
			</template>
			<progress v-if="stage !== 'start'" aria-label="Form progress" :max="stages.length - 1" :value="stageIndex"></progress>
			<template v-if="stage === 'start'">
				<picture>
					<source srcset="/documents/abmeldung-original.webp 1600w, /documents/previews/abmeldung-original.webp 300w, /documents/previews2x/abmeldung-original.webp 600w" type="image/webp">
					<source srcset="/documents/previews/abmeldung-original.png 300w, /documents/previews2x/abmeldung-original.png 600w" type="image/png">
					<img alt="Berlin Abmeldung form" loading="lazy" src="/documents/previews/abmeldung-original.png">
				</picture>
				<p>This tool helps you <strong>fill the <glossary>Abmeldung</glossary> form</strong> in 3 minutes. You can save the completed form, print it, and bring it to your <glossary>Bürgeramt</glossary> appointment.</p>
				<p>Your personal information stays on your computer. No one else can see it.</p>
			</template>
			<template v-if="stage === 'oldAddress'">
				<h2>Your old address</h2>
				<p>Where did you live? Enter the address that you want to deregister.</p>
				<hr>
				<div class="form-group">
					<label :for="uid('oldAddress')">Street address</label>
					<input
						:id="uid('oldAddress')"
						ref="oldAddressInput"
						type="text"
						v-model="oldAddress"
						placeholder="Alte Straße 123"
						autocomplete="address-line1"
						required>
				</div>
				<div class="form-group">
					<label :for="uid('oldPostCode')">
						<glossary term="Postleitzahl">Post code</glossary>
					</label>
					<div class="input-group">
						<postalcode-input ref="oldPostCodeInput" :id="uid('oldPostCode')" v-model="oldPostCode" required></postalcode-input>
						Berlin
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
					<a class="input-instructions internal-link" href="/guides/addressing-a-letter-in-germany#extra-information" target="_blank">How to write your building details</a>
				</div>
				<hr>
				<div class="form-group">
					<label :for="uid('moveOutDate')">Move-out date</label>
					<date-picker v-model="moveOutDate" :id="uid('moveOutDate')" required></date-picker>
				</div>
			</template>
			<template v-if="stage === 'newAddress'">
				<h2>Your next address</h2>
				<p>Where will you live after you leave Germany?</p>
				<hr>
				<div class="form-group">
					<label :for="uid('newAddress')">Street address</label>
					<input
						:id="uid('newAddress')"
						type="text"
						ref="newAddressInput"
						v-model="newAddress"
						placeholder="123 Maple Street, Apt. 102"
						autocomplete="address-line1"
						required>
				</div>
				<div class="form-group">
					<label :for="uid('newCityAndPostCode')">
						City and post code
					</label>
					<input
						:id="uid('newCityAndPostCode')"
						placeholder="Montreal, Quebec, H3E 1J4"
						type="text"
						v-model="newCityAndPostCode"
						autocomplete="address-level2" required>
				</div>
				<div class="form-group">
					<label :for="uid('newCountry')">Country</label>
					<country-input
						country-code
						v-model="newCountry"
						ref="newCountryInput"
						:id="uid('newCountry')"
						required></country-input>
					<span v-if="newCountry === 'DE'" class="input-instructions">If you stay in Germany, you probably don't need to deregister your address&nbsp;&mdash;&nbsp;<a href="/guides/abmeldung#who-needs-to-deregister" target="_blank">More information</a></span>
				</div>
			</template>
			<template v-if="stage === 'addPeople'">
				<h2>Who is deregistering?</h2>
				<p>Enter the same information as on your <em><glossary term="Anmeldebestätigung">Anmeldebestätigung</glossary></em>.</p>
				<template v-for="(person, index) in people">
					<hr>
					<h3 v-if="people.length > 1">
						<i class="icon person" aria-hidden="true"></i> {{ person.firstName ? [person.title, person.firstName, person.lastName].join(' ') : ['Person #', index + 1].join() }}
					</h3>
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
							:id="uid('nationality-' + person.id)"
							required></country-input>
					</div>
					<div class="form-group">
						<label :for="uid('religion-' + person.id)">Religion</label>
						<select required :id="uid('religion-' + person.id)" v-model="person.religion" :class="{placeholder: !person.religion}">
							<option disabled hidden default :value="null">Choose a church</option>
							<option value="Evangelische Kirche">Evangelical Church</option>
							<option value="Römisch-katholische Kirche">Roman Catholic Church</option>
							<option value="Jüdische Gemeinde">Jewish Community</option>
							<option value="Altkatholische Kirche">Old Catholic Church</option>
							<option value="Freireligiöse Gemeinden">Free Religious communities</option>
							<option disabled>──────────</option>
							<option value="Sonstiges, nicht kirchensteuerpflichtig">Other / No religion</option>
						</select>
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
			<template v-if="stage === 'offlineFinish'">
				<h2>You are almost done!</h2>
				<template v-if="peopleTriples.length > 1">
					<p>Print the forms, sign them, and bring them to your <em>Abmeldung</em> appointment.</p>
					<ul class="buttons list">
						<li v-for="([person1, person2, person3], index) in peopleTriples">
							<button @click="generatePDF(person1, person2, person3)" :disabled="downloadInProgress">
								<icon-pdf/>
								<div>
									<h3>Download part {{ index + 1 }} of the form</h3>
									<p v-if="person1.firstName">For {{ person1.firstName }}<template v-if="person2 && !person3"> and {{ person2.firstName }}</template><template v-if="person2 && person3">, {{ person2.firstName }} and {{ person3.firstName }}</template>.</p>
								</div>
							</button>
						</li>
					</ul>
				</template>
				<ul class="buttons list">
					<li v-if="peopleTriples.length === 1">
						<button @click="generatePDF(people[0], people[1], people[2])" :disabled="downloadInProgress">
							<icon-pdf/>
							<div>
								<h3>Download the filled form</h3>
								<p>Print this form, sign it, then send it to any <em>Bürgeramt</em> in Berlin.</p>
							</div>
						</button>
					</li>
				</ul>
				<h3>What to do next</h3>
				<p>To deregister your address, send this form to <a target="_blank" href="https://service.berlin.de/standorte/buergeraemter">any Bürgeramt</a>. You can do this by email, by post or in person.</p>
				<ul class="buttons list">
					<li>
						<a class="recommended" href="/guides/abmeldung#in-person-at-the-burgeramt" target="_blank">
							<icon-calendar/>
							<div>
								<h3>Book a Bürgeramt appointment</h3>
								<p>Deregister in person, get your deregistration certificate faster.</p>
							</div>
						</a>
					</li>
					<li>
						<a href="/guides/abmeldung#by-registered-mail" target="_blank">
							<icon-mail/>
							<div>
								<h3>Send the Abmeldung form</h3>
								<p>Deregister your address by post or by email. It's easier, but slower.</p>
							</div>
						</a>
					</li>
					<li>
						<a href="/out/deregistrationde-abmeldung" target="_blank">
							<icon-representative/>
							<div>
								<h3>Pay someone to deregister you</h3>
								<p>Let an expert do your <em>Abmeldung</em>, get your <glossary term="Abmeldebescheinigung">deregistration certificate</glossary> by email.</p>
							</div>
						</a>
					</li>
					<li>
						<a href="/guides/leaving-germany" target="_blank">
							<icon-exit/>
							<div>
								<h3>Leave Germany</h3>
								<p>Use my checklist for moving to another country.</p>
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
	`,
}
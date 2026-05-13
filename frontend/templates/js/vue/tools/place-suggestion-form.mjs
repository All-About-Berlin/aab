import Checkbox from '/js/vue/components/checkbox.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import Radio from '/js/vue/components/radio.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { googleMapsApiKey } from '/js/utils/constants.mjs';
import { validateForm } from '/js/utils/form.mjs';

import metadata from '/js/vue/tools/place-suggestion-form.metadata.json' with { type: 'json' };

export default {
	components: {
		Checkbox,
		Collapsible,
		EmailInput,
		Glossary,
		IconDonate,
		Radio,
	},
	mixins: [uniqueIdsMixin],
	props: {
		ariaLabel: String, // Catch the initial aria-label attribute, so it doesn't override ours
		category: {
			type: String,
			required: true,
		},
		static: Boolean,
		embedded: Boolean,  // This form can be standalone tool, or embedded in another component
	},
	data() {
		return {
			metadata,
			stage: 'form',
			isLoading: false,
			businessName: '',
			selectedPlace: null,
			languages: '',
			acceptsPublicHealthInsurance: null,
			notes: '',
			isOwner: false,
			email: '',
			autocomplete: null,
		};
	},
	mounted() {
		this.initAutocomplete();
	},
	beforeDestroy() {
		if(this.autocomplete){
			google.maps.event.clearInstanceListeners(this.autocomplete);
			this.autocomplete = null;
		}
	},
	computed: {
		showHealthInsuranceField(){
			return ["doctors", "psychotherapists", "psychiatrists", "gynecologists"].includes(this.category);
		},
		categoryDisplay(){
			return {
				'cinemas': "cinema",
				'dentists': "dentist",
				'doctors': "doctor",
				'driving-schools': "driving school",
				'foreign-ingredients': "shop",
				'gyms': "gym",
				'gynecologists': "gynecologist",
				'hairdressers': "hair salon",
				'lawyers': "lawyer",
				'motorcycle-stores': "store",
				'pizza': "restaurant",
				'psychiatrists': "psychiatrist",
				'psychotherapists': "therapist",
				'relocation-agencies': "relocation agency",
				'steuerberater': "tax advisor",
				'veterinarians': "vet",
			}[this.category] || 'place';
		}
	},
	methods: {
		loadGooglePlaces() {
			return new Promise((resolve, reject) => {
				if (window.google?.maps?.places) {
					resolve();
					return;
				}
				const script = document.createElement('script');
				script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&language=en`;
				script.onload = resolve;
				script.onerror = reject;
				document.head.appendChild(script);
			});
		},
		initAutocomplete() {
			this.$refs.businessNameInput.setCustomValidity('Select a place.');

			if (!window.google?.maps?.places) {
				this.loadGooglePlaces().then(() => this.initAutocomplete());
				return;
			}

			this.autocomplete = new google.maps.places.Autocomplete(this.$refs.businessNameInput, {
				types: ['establishment'],
				componentRestrictions: { country: 'de' },
				bounds: new google.maps.LatLngBounds(
					{ lat: 52.3383, lng: 13.0884 },
					{ lat: 52.6755, lng: 13.7611 },
				),
				strictBounds: true,
				fields: ['name', 'formatted_address', 'place_id'],
			});

			this.autocomplete.addListener('place_changed', () => {
				this.selectedPlace = this.autocomplete.getPlace();
				this.selectedPlace.formatted_address = this.selectedPlace.formatted_address.replace(/(, (\d{5} )?Berlin)?, Germany$/, "").trim();
				this.businessName = this.selectedPlace.name;
			});
		},
		async submit() {
			if (!validateForm(this.$el)) {
				return;
			}
			this.isLoading = true;
			const response = await fetch('/api/forms/place-suggestion', {
				method: 'POST',
				keepalive: true,
				headers: { 'Content-Type': 'application/json; charset=utf-8' },
				body: JSON.stringify({
					category: this.category,
					business_name: this.businessName,
					google_maps_id: this.selectedPlace?.place_id,
					languages: this.languages,
					notes: this.notes,
					is_owner: this.isOwner,
					email: this.email,
					accepts_public_health_insurance: this.acceptsPublicHealthInsurance,
				}),
			});
			this.isLoading = false;
			this.$el.scrollIntoView({ block: 'start', behavior: 'auto' });
			this.stage = response.ok ? 'thank-you' : 'error';
		},
	},
	watch: {
		selectedPlace(newVal) {
			try{
				this.$refs.businessNameInput.setCustomValidity(newVal ? '' : 'Select a place.');
			} catch (e) {}
		},
	},
	template: `
		<component
			:aria-label="'Recommend a ' + categoryDisplay"
			:aria-description="metadata.description"
			class="place-suggestion-form"
			:static="static"
			:is="embedded ? 'div' : 'collapsible'">
			<template v-slot:header>
				Recommend a {{ categoryDisplay }}
			</template>
			<template v-if="stage === 'form'">
				<h3 v-if="embedded || static">Recommend a {{ categoryDisplay }}</h3>
				<div class="form-group">
					<label :for="uid('businessName')">Business name</label>
					<input
						type="text"
						ref="businessNameInput"
						:id="uid('businessName')"
						v-model="businessName"
						placeholder="Search for a business"
						required
					/>
					<span class="input-instructions" v-if="selectedPlace">{{ selectedPlace.formatted_address }}</span>
				</div>
				<template v-if="selectedPlace || embedded">
					<hr>
					<div class="form-group">
						<label :for="uid('languages')">Languages spoken</label>
						<input
							type="text"
							:id="uid('languages')"
							v-model="languages"
							placeholder="English, German"
						/>
						<span class="input-instructions">In which languages do they serve customers?</span>
					</div>
					<div class="form-group" v-if="showHealthInsuranceField">
						<label :for="uid('acceptsPublicHealthInsurance')">Health insurance</label>
						<radio
							v-model="acceptsPublicHealthInsurance"
							:value="true">
							<span>They accept <glossary term="gesetzliche Krankenversicherung">public health insurance</glossary></span>
						</radio>
						<radio
							v-model="acceptsPublicHealthInsurance"
							:value="false">
							They don't accept public health insurance
						</radio>
						<radio
							v-model="acceptsPublicHealthInsurance"
							:value="null">
							I don't know
						</radio>
					</div>
					<div class="form-group">
						<label :for="uid('notes')">Notes</label>
						<textarea
							:id="uid('notes')"
							v-model="notes"
							placeholder="Tell us more about this business"
						></textarea>
					</div>
					<div class="form-group">
						<label>Do you work there?</label>
						<checkbox v-model="isOwner">I work for this business</checkbox>
					</div>
					<div class="form-group" v-if="isOwner">
						<label :for="uid('email')">Email address</label>
						<email-input :id="uid('email')" v-model="email" required></email-input>
						<span class="input-instructions">In case I have questions about this business</span>
					</div>
					<hr>
					<div class="buttons bar">
						<button v-if="embedded" class="button" @click="$emit('cancel')"><i class="icon left" aria-hidden="true"></i> Go back</button>
						<button class="button primary" @click="submit" :disabled="isLoading" :class="{loading: isLoading}">Submit</button>
					</div>
				</template>
			</template>
			<template v-if="stage === 'thank-you'">
				<p><strong>Thank you!</strong> I will review your recommendation and update the list. This can take some time.</p>
				<ul class="buttons list">
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
			<template v-if="stage === 'error'">
				<p><strong>An error occurred.</strong> If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
			</template>
			<div class="buttons bar" v-if="stage === 'thank-you' || stage === 'error'">
				<button class="button" v-if="embedded" @click="$emit('cancel')"><i class="icon left" aria-hidden="true"></i> Go back</button>
				<button class="button" v-if="!embedded" @click="stage = 'form'"><i class="icon left" aria-hidden="true"></i> Go back</button>
			</div>
		</component>
	`,
};

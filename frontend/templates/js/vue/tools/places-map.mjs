import PlaceSuggestionForm from '/js/vue/tools/place-suggestion-form.mjs';
import Recommended from '/js/vue/components/recommended.mjs';

export default {
	components: {
		PlaceSuggestionForm,
		Recommended,
	},
	props: {
		category: {
			type: String,
			required: true,
		},
	},
	data() {
		return {
			places: [],
			selectedPlaceId: null,
			mapReadyPromise: null,
			map: null,
			placesLoading: true,
			mapLoading: false,
			mapLoaded: false,
			showSuggestionForm: false,
			healthInsuranceFilter: null,
			locationFilter: null,
		};
	},
	async mounted() {
		this.loadPlaces();
	},
	computed: {
		showHealthInsuranceFilter(){
			return this.places.filter(p => p.accepts_public_health_insurance).length > 0;
		},
		filteredPlaces(){
			return this.places
				.filter(
					p => [`borough-${p.borough}`, `suburb-${p.suburb}`, null].includes(this.locationFilter)
				)
				.filter(
					p => !this.healthInsuranceFilter || p.accepts_public_health_insurance
				);
		},
		boroughsAndSuburbs(){
			const otherSuburbs = new Set();

			const boroughsAndSuburbs = this.places.reduce((boroughsAndSuburbs, place) => {
				if(place.borough && place.suburb){
					boroughsAndSuburbs[place.borough] ||= new Set();
					boroughsAndSuburbs[place.borough].add(place.suburb);
				}
				else if(place.suburb){
					otherSuburbs.add(place.suburb);
				}
				return boroughsAndSuburbs;
			}, {});

			const sortedBoroughs = Object.fromEntries(Object.entries(boroughsAndSuburbs).sort(([a], [b]) => a.localeCompare(b)));
			sortedBoroughs['Other'] = otherSuburbs;
			return sortedBoroughs;
		},
	},
	methods: {
		async loadMap() {
			if (this.mapReadyPromise) {
				return this.mapReadyPromise;
			}

			this.mapLoading = true;
			this.mapReadyPromise = new Promise((resolve) => {
				const link = document.createElement('link');
				link.rel = 'stylesheet';
				link.href = 'https://unpkg.com/maplibre-gl@5.14.0/dist/maplibre-gl.css';
				document.head.appendChild(link);

				const script = document.createElement('script');
				script.src = 'https://unpkg.com/maplibre-gl@5.14.0/dist/maplibre-gl.js';
				script.onload = () => resolve(this.initMap());
				document.head.appendChild(script);

				this.mapLoading = false;
				this.mapLoaded = true;
			});
			return this.mapReadyPromise;
		},
		async initMap() {
			const mapStyleResponse = await fetch('/js/vue/tools/places-map-style.json');
			const map = new maplibregl.Map({
				container: this.$refs.mapEl,
				style: await mapStyleResponse.json(),
				bounds: [13.0884, 52.3383, 13.7611, 52.6755],
				fitBoundsOptions: { padding: 40 },
				attributionControl: false,
			});
			map.addControl(new maplibregl.AttributionControl({ compact: true }));
			this.map = map;
			this.createPlaceMarkers();
			return map;
		},
		async loadPlaces(){
			this.placesLoading = true;
			const response = await fetch(`/places/${this.category}.json`);
			const responseJson = await response.json();
			this.places = responseJson.places.map((place, index) => {
				const query = encodeURIComponent(`${place.name}, ${place.address}`);
				const placeIdParam = place.google_place_id ? `&query_place_id=${place.google_place_id}` : '';
				place.googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${query}${placeIdParam}`;
				place.id = index + 1;
				return place;
			});
			this.placesLoading = false;
		},
		togglePlaceSelected(idToSelect) {
			this.selectedPlaceId = this.selectedPlaceId === idToSelect ? null : idToSelect;
			this.$refs.mapEl.querySelectorAll('.marker').forEach(marker => {
				if(this.selectedPlaceId){
					const showAsHighlighted = !this.selectedPlaceId || String(this.selectedPlaceId) === marker.dataset.placeId;
					marker.classList.toggle('primary', showAsHighlighted);
				}
			});
		},
		scrollMapIntoView(){
			this.$refs.mapEl.scrollIntoView({ behavior: 'auto' });
		},
		selectPlaceInList(place) {
			this.togglePlaceSelected(place.id);
			this.highlightPlaceOnMap(place);
		},
		highlightPlaceInList(place){
			this.$refs[`place-${place.id}`][0].scrollIntoView({ block: 'nearest', behavior: 'auto' });
		},
		selectPlaceOnMap(place) {
			this.togglePlaceSelected(place.id);
			this.highlightPlaceInList(place);
		},
		async highlightPlaceOnMap(place){
			await this.loadMap();
			this.scrollMapIntoView();
			this.map.flyTo({ center: [parseFloat(place.longitude), parseFloat(place.latitude)], zoom: 12 });
		},
		async createPlaceMarkers(){
			const map = await this.loadMap();
			const bounds = new maplibregl.LngLatBounds();
			this.filteredPlaces.forEach(place => {
				const el = document.createElement('div');
				el.textContent = place.id;
				el.dataset.placeId = String(place.id);
				el.className = 'marker button';
				if(!this.selectedPlaceId || this.selectedPlaceId === place.id){
					el.classList.add('primary');
				}

				new maplibregl.Marker({ element: el, anchor: 'bottom-left' })
					.setLngLat([parseFloat(place.longitude), parseFloat(place.latitude)])
					.addTo(map);

				el.addEventListener('click', () => this.selectPlaceOnMap(place));
				bounds.extend([parseFloat(place.longitude), parseFloat(place.latitude)]);
			});
			map.fitBounds(bounds, { maxZoom: 13 });
		},
	},
	watch: {
		filteredPlaces(){
			if(this.mapLoading || this.mapLoaded){
				this.createPlaceMarkers();
			}
		},
	},
	template: `
		<aside
			aria-label="Map with list of places"
			class="places-map"
			:class="{'form-open': this.showSuggestionForm}">
			<div ref="mapEl" class="map no-print" :class="{'not-loaded': !this.mapLoaded}" v-show="!showSuggestionForm">
				<button v-if="!this.mapLoaded" class="load-map-button button primary" @click="loadMap">Show map</button>
			</div>
			<div class="controls" v-if="!showSuggestionForm">
				<details>
					<summary>Filter places</summary>
					<div class="input-group">
					<select v-model="locationFilter">
						<option :value="null">Anywhere</option>
						<option disabled>──────────</option>
						<template v-for="(suburbs, borough) in boroughsAndSuburbs">
							<option :value="'borough-' + borough" :key="borough">{{ borough }}</option>
							<option v-for="suburb in suburbs" :key="borough + suburb" :value="'suburb-' + suburb">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ suburb }}</option>
						</template>
					</select>
					<select v-if="showHealthInsuranceFilter" v-model="healthInsuranceFilter">
						<option :value="null">Any health insurance</option>
						<option :value="true">Public health insurance</option>
					</select>
					</div>
				</details>
				<button class="button link add no-print" @click="showSuggestionForm = true">Add a place</button>
			</div>
			<ol :class="{loading: placesLoading}" v-if="!showSuggestionForm">
				<li v-for="place in filteredPlaces" :key="place.id" :ref="'place-' + place.id">
					<button class="marker button" :class="{ primary: selectedPlaceId === place.id }" @click="selectPlaceInList(place)">{{ place.id }}</button>
					<h4>
						<a v-if="place.website" :title="'Website of ' + place.name" target="_blank" :href="place.website">{{ place.name }}</a>
						<template v-else>{{ place.name }}</template>
					</h4>
					<address>
						<a :href="place.googleMapsUrl" target="_blank" title="Open in Google Maps" v-text="place.suburb"></a>
					</address>
					<recommended v-if="place.recommended"></recommended>
					<p v-if="place.description">{{ place.description }}</p>
					<span class="pill yes" v-if="place.accepts_public_health_insurance && !healthInsuranceFilter" title="Accepts public health insurance">Public health insurance</span>
				</li>
				<li v-if="filteredPlaces.length === 0">No places match your criteria</li>
			</ol>
			<place-suggestion-form embedded v-if="showSuggestionForm" :category="category" @cancel="showSuggestionForm = false"></place-suggestion-form>
		</aside>
	`,
};

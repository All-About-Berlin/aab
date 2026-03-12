import Checkbox from '/js/vue/components/checkbox.mjs';
import Collapsible from '/js/vue/components/collapsible.mjs';
import { isoDay, isoMonth } from '/js/utils/date.mjs';

const ding = new Audio('/js/ding.wav');

export default {
	components: {
		Checkbox,
		Collapsible,
	},
	props: {
		static: Boolean,
	},
	data() {
		return {
			isConnected: null,
			hasError: false,
			originalPageTitle: document.title,
			playSoundOnNewAppointments: false,
			reconnectInterval: null,
			socket: null,
			lastMessage: null,
			secondsToNextMessage: null,
		}
	},
	mounted() {
		this.connect();

		// Connect to API, check every 3 minutes
		setInterval(() => {
			if(this.lastChecked) {
				const nextCheck = new Date(this.lastChecked.getTime() + 180*1000);
				this.secondsToNextMessage = Math.round(
					Math.max((nextCheck.getTime() - (new Date()).getTime()) / 1000, 0)
				);
			}
			else {
				this.secondsToNextMessage = null;
			}
		}, 500);
	},
	methods: {
		connect() {
			this.socket = new WebSocket(`wss://${window.location.hostname}/api/appointments`);
			this.socket.addEventListener('message', this.onMessage);
			this.socket.addEventListener('error', this.onError);
			this.socket.addEventListener('open', this.onConnect);
			this.socket.addEventListener('close', this.onDisonnect);
		},
		onConnect(event) {
			console.log('Connected to appointments API');
			this.isConnected = true;
			if(this.reconnectInterval){ clearInterval(this.reconnectInterval) }
			this.reconnectInterval = null;
		},
		onDisonnect(event) {
			this.isConnected = false;
			this.lastMessage = null;
			console.warn('Lost connection to appointments API. Reconnecting...');
			if(!this.reconnectInterval) {
				this.reconnectInterval = setInterval(this.connect, 5000)
			}
		},
		onMessage(event) {
			if(!event.data) return;
			const currentMessage = JSON.parse(event.data);
			if(currentMessage) {
				if(currentMessage.status === 200){
					this.hasError = false;
				}
				else{
					console.error("Could not fetch appointments", event.data);
					this.hasError = true;
					return;
				}
			}
			this.lastMessage = currentMessage;
		},
		onError(event) {
			console.error('WebSocket error', event);
			this.hasError = true;
			this.lastMessage = null;
		},
		updateWindowTitle() {
			// Only control the title on the dedicated tool page
			if(!window.location.pathname.startsWith('/tools/appointment-finder')) {
				return;
			}

			if(!this.appointments.length) {
				document.title = this.originalPageTitle;
				return;
			}

			const timeToEarliestAppointment = this.appointments[0].getTime() - (new Date()).getTime();
			const daysToEarliestAppointment = Math.ceil(timeToEarliestAppointment / (1000*60*60*24));

			if(daysToEarliestAppointment === 0) {
				document.title = `(${this.appointments.length}) Appointments today!`;
			}
			else if(daysToEarliestAppointment === 1) {
				document.title = `(${this.appointments.length}) Appointment tomorrow!`;
			}
			else {
				document.title = `(${this.appointments.length}) Appointments in ${daysToEarliestAppointment} days`;
			}
		}
	},
	computed: {
		appointments() {
			if(!this.lastMessage) { return []; }
			return this.lastMessage.appointmentDates.sort().map(dateString => new Date(dateString));
		},
		lastChecked() {
			return this.lastMessage ? new Date(this.lastMessage.time) : null;
		},
		lastFoundMessage() {
			if(this.appointments.length || !this.lastMessage || !this.lastMessage.lastAppointmentsFoundOn){
				return null;
			}

			const lastFoundDate = new Date(this.lastMessage.lastAppointmentsFoundOn);
			const secondsAgo = Math.floor((new Date() - lastFoundDate) / 1000) - 10;  // Leave 10s for the refresh

			if (secondsAgo < 60) {
				return "a minute";
			} else if (secondsAgo < 3600) {
				const minutesAgo = Math.floor(secondsAgo / 60);
				return `${minutesAgo} minute${minutesAgo !== 1 ? 's' : ''}`;
			} else {
				const hoursAgo = Math.floor(secondsAgo / 3600);
				return `${hoursAgo} hour${hoursAgo !== 1 ? 's' : ''}`;
			}
		},
		isDuringOfficeHours() {
			const now = new Date();
			return now.getHours() >= 8  && now.getHours() < 17 && now.getDay() > 0 && now.getDay() < 6;
		},
		months(){
			const appointmentsSet = new Set(this.appointments.map(isoDay));

			const today = new Date();
			const year = today.getFullYear();
			return Array.from({length: 4}, (_, m) => {
				const monthIndex = today.getMonth() + m;

				const firstOfMonth = new Date(year, monthIndex, 1);
				const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();

				// Build days array with map
				const days = Array.from({length: daysInMonth}, (_, d) => {
					const date = new Date(year, monthIndex, d + 1);
					const iso = isoDay(date);
					const hasAppointments = appointmentsSet.has(isoDay(date));
					return {
						name: date.toLocaleDateString('en-US', {
							weekday: 'long',
							month: 'long',
							day: 'numeric',
						}),
						weekday: date.getDay(),
						number: date.getDate(),
						iso,
						hasAppointments,
						url: `/out/appointment-anmeldung?date=${iso}`,
						classes: {
							available: hasAppointments,
							unavailable: !hasAppointments,
							past: iso < isoDay(today),
							today: iso === isoDay(today),
						},
					};
				});

				const hasAppointments = days.filter(d => d.hasAppointments).length > 0;
				return {
					name: firstOfMonth.toLocaleDateString('en-US', {month: 'long'}),
					iso: isoMonth(firstOfMonth),
					days,
					hasAppointments,
					classes: {
						available: hasAppointments,
						unavailable: !hasAppointments,
					},
				};
			});
		},
	},
	watch: {
		appointments(newAppointments, oldAppointments) {
			if(newAppointments.length && this.playSoundOnNewAppointments) {
				ding.play();
			}
			this.updateWindowTitle();
		},
		playSoundOnNewAppointments(isChecked) {
			if(isChecked){
				ding.play();
			}
		}
	},
	template: `
		<collapsible
			aria-label="Anmeldung appointment finder"
			class="appointment-finder no-print"
			:static="static">

			<template v-slot:header>Find an Anmeldung appointment</template>
			<h3 v-if="static">Book a Bürgeramt appointment</h3>
			<div class="months" v-if="appointments.length > 0">
				<div class="month" :class="month.classes" v-for="month in months" :key="month.iso" :aria-label="month.name">
					<time :datetime="month.iso" v-text="month.name"></time>
					<ol v-if="month.hasAppointments" class="days weekdays">
						<li data-weekday="1" class="day"><abbr title="Monday">Mo</abbr></li>
						<li data-weekday="2" class="day"><abbr title="Tuesday">Tu</abbr></li>
						<li data-weekday="3" class="day"><abbr title="Wednesday">We</abbr></li>
						<li data-weekday="4" class="day"><abbr title="Thursday">Th</abbr></li>
						<li data-weekday="5" class="day"><abbr title="Friday">Fr</abbr></li>
						<li data-weekday="6" class="day"><abbr title="Saturday">Sa</abbr></li>
						<li data-weekday="7" class="day"><abbr title="Sunday">Su</abbr></li>
					</ol>
					<ol v-if="month.hasAppointments" class="days">
						<li class="day" :class="day.classes" :data-weekday="day.weekday" v-for="day in month.days" :key="day.iso" :aria-label="day.name" :title="day.name">
							<time v-if="!day.hasAppointments" :datetime="day.iso" v-text="day.number"></time>
							<a v-if="day.hasAppointments" :href="day.url" target="_blank">
								<time :datetime="day.iso" v-text="day.number"></time>
							</a>
						</li>
					</ol>
					<div class="no-appointments" v-if="!month.hasAppointments">No appointments</div>
				</div>
			</div>

			<p v-if="isConnected === null">
				Connecting to the appointment finder&hellip;
			</p>
			<template v-if="isConnected === false">
				<h3>Can't connect to the appointment finder</h3>
				<p>Try refreshing the page. You can also <a target="_blank" href="/out/appointment-anmeldung">check Berlin.de</a>, <a href="tel:+49115">call 115</a> or <a href="/guides/berlin-burgeramt-appointment#email-the-burgeramt">email your <em>Bürgeramt</em></a>. If this keeps happening, <a href="/contact">email me</a>.</p>
			</template>
			<template v-if="isConnected && hasError">
				<h3>Can't connect to Berlin.de</h3>
				<p>Berlin.de is having issues or blocking this tool. The error is on their side, and I can't fix it. Try again later.</p>
				<p>You can also <a target="_blank" href="/out/appointment-anmeldung">check Berlin.de</a>, <a href="tel:+49115">call 115</a> or <a href="/guides/berlin-burgeramt-appointment#email-the-burgeramt">email your <em>Bürgeramt</em></a>.</p>
				<p v-if="lastFoundMessage">Last appointments found {{ lastFoundMessage }} ago.</p>
			</template>
			<template v-if="isConnected && !hasError && appointments.length === 0">
				<h3>No appointments found</h3>
				<p>
					<template v-if="isDuringOfficeHours">This happens often.</template>
					<template v-if="!isDuringOfficeHours">There are more appointments on weekdays between 8:00 and 17:00.</template>
					<a target="_blank" href="/out/appointment-anmeldung">Check Berlin.de</a>, <a href="tel:+49115>call 115</a> or <a href="/guides/berlin-burgeramt-appointment#email-the-burgeramt">email your <em>Bürgeramt</em></a>. It might work better. You can also <a href="/guides/anmeldung-in-english-berlin#how-to-register-your-address-online">do your Anmeldung online</a>.
				</p>
			</template>

			<p class="timer" v-if="isConnected && !hasError && secondsToNextMessage > 0">
				<template v-if="lastFoundMessage">Last appointments found {{ lastFoundMessage }} ago.</template>
				Checking again in {{ secondsToNextMessage }} {{ secondsToNextMessage > 1 ? 'seconds' : 'second' }}.
			</p>
			<p class="timer" v-if="isConnected && !hasError && secondsToNextMessage <= 0">
				Looking for appointments...
			</p>
			<checkbox v-if="isConnected" v-model="playSoundOnNewAppointments">
				Play a sound on {{ appointments.length > 0 ? '' : 'new' }} appointments
			</checkbox>
		</collapsible>
	`,
}
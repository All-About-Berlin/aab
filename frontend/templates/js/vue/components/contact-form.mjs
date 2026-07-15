import Collapsible from '/js/vue/components/collapsible.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import IconWhatsapp from '/js/vue/components/icons/whatsapp.mjs';
import Tabs from '/js/vue/components/tabs.mjs';

import multiStageMixin from '/js/vue/mixins/multiStage.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import QRCode from '/js/libs/qrcode.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';

export default {
	components: {
		Collapsible,
		EmailInput,
		FullNameInput,
		IconWhatsapp,
		Tabs,
	},
	mixins: [multiStageMixin, uniqueIdsMixin, trackedStagesMixin],
	props: {
		static: Boolean,
		ariaLabel: String,
		ariaDescription: String,
		recipientName: String,
		recipientEmail: String,
		recipientWhatsapp: String,
		apiEndpoint: String,
		trackAs: String,
	},
	data() {
		return {
			contactMethod: null,
			fullName: '',
			email: '',
			question: '',
			isLoading: false,
			stages: ['contact', 'thank-you', 'error'],
		};
	},
	computed: {
		cleanRecipientWhatsapp() {
			return this.recipientWhatsapp.replace(/[^0-9+]/g, '');
		},
		whatsappMessage() {
			return `Hi ${this.recipientName}, I am ${this.fullName}. I have a question for you.`;
		},
		whatsappUrl() {
			return `https://wa.me/${this.cleanRecipientWhatsapp}?text=${encodeURIComponent(this.whatsappMessage)}`;
		},
		qrCode() {
			var qrcode = new QRCode({
				content: `https://wa.me/${this.cleanRecipientWhatsapp}`,
				width: 150,
				height: 150,
				padding: 0,
				color: 'currentColor',
				background: 'transparent',
				ecl: 'L',
				join: true,
				pretty: false,
				container: 'none',
			});
			return qrcode.svg();
		},
		trackedStagesExtraData() {
			const data = {};
			if (this.contactMethod) {
				data.contactMethod = this.contactMethod;
			}
			return data;
		},
	},
	methods: {
		async createCase(event) {
			if (validateForm(this.$el)) {
				this.isLoading = true;
				const response = await fetch(
					this.apiEndpoint,
					{
						method: 'POST',
						keepalive: true,
						headers: { 'Content-Type': 'application/json; charset=utf-8' },
						body: JSON.stringify({
							name: this.fullName,
							email: this.email || '',
							question: this.question,
							referrer: getReferrer() || '',
							contact_method: this.contactMethod,
						}),
					},
				);
				this.isLoading = false;

				if (response.ok) {
					this.goToStage('thank-you');
				} else {
					this.goToStage('error');
				}
			} else {
				event.preventDefault();
			}
		},
	},
	template: `
		<collapsible
			class="contact-form"
			:aria-label="ariaLabel"
			:aria-description="ariaDescription"
			:static="static">
			<template v-slot:header>
				<slot name="header"></slot>
			</template>

			<template v-if="stage === 'contact'">
				<div class="form-recipient">
					<div>
						<slot name="description"></slot>
					</div>
					<slot name="image"></slot>
				</div>
				<hr>
				<div class="contact-method">
					<h3>How should we talk?</h3>
					<tabs
						aria-label="Preferred contact method"
						v-model="contactMethod"
						:id="uid('contactMethod')"
						:options="[{label: 'WhatsApp', value: 'WHATSAPP'}, {label: 'Email', value: 'EMAIL'}]"></tabs>
				</div>
				<template v-if="contactMethod">
					<hr>
					<div class="form-group">
						<label :for="uid('fullName')">Your name</label>
						<full-name-input
							:id="uid('fullName')"
							v-model="fullName"
							required></full-name-input>
					</div>
					<div class="form-group" v-if="contactMethod === 'EMAIL'">
						<label :for="uid('email')">Email address</label>
						<email-input
							v-model="email"
							:id="uid('email')"
							required></email-input>
					</div>
					<template v-if="contactMethod !== 'WHATSAPP'">
						<hr>
						<div class="form-group">
							<label :for="uid('question')">Your question</label>
							<textarea :id="uid('question')" v-model="question" placeholder="Your question" required></textarea>
						</div>
					</template>
					<hr>
					<div class="buttons bar">
						<button v-if="contactMethod === 'EMAIL'" class="button primary" @click="createCase" :disabled="isLoading" :class="{loading: isLoading}">
							Ask {{ recipientName }}
						</button>
						<a v-if="contactMethod === 'WHATSAPP'" :href="whatsappUrl" @click="createCase" class="button whatsapp" :disabled="isLoading" target="_blank">
							<icon-whatsapp/>
							Chat with {{ recipientName }}
						</a>
					</div>
				</template>
			</template>

			<template v-if="stage === 'thank-you' && contactMethod === 'WHATSAPP'">
				<div class="form-recipient">
					<div>
						<p>
							To chat with {{ recipientName }}, <a :href="whatsappUrl" target="_blank">open WhatsApp</a> <span class="no-mobile">or scan this QR code</span>.
						</p>
						<p>
							His number is <strong class="selectable">{{ recipientWhatsapp }}</strong>.
						</p>
					</div>
					<svg class="no-mobile qr-code" v-html="qrCode" xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 150 150"></svg>
				</div>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button previous" @click="goToStart()">
						<span class="no-mobile">Go back</span>
					</button>
					<a :href="whatsappUrl" class="button whatsapp" target="_blank">
						<icon-whatsapp/>
						Open WhatsApp
					</a>
				</div>
			</template>

			<template v-if="stage === 'thank-you' && contactMethod === 'EMAIL'">
				<p><strong>Thank you!</strong> {{ recipientName }} got your message. You will get an email from <a :href="'mailto:' + recipientEmail">{{ recipientEmail }}</a> in the next 24 hours. If you don't get a response, check your spam folder.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button previous" @click="goToStart()">
						Go back
					</button>
				</div>
			</template>

			<template v-if="stage === 'error'">
				<p><strong>An error occurred</strong> while sending your message. If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
				<hr>
				<div class="buttons bar">
					<button aria-label="Go back" class="button previous" @click="goToStart()">
						Go back
					</button>
				</div>
			</template>
		</collapsible>
	`,
}

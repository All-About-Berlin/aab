import ContactForm from '/js/vue/components/contact-form.mjs';
import { seamusWolf } from '/js/utils/constants.mjs';
import metadata from '/js/vue/tools/insurance-contact-form.metadata.json' with { type: 'json' };

export default {
	components: { ContactForm },
	props: {
		static: Boolean,
	},
	data() {
		return {
			metadata,
			seamusWolf,
		};
	},
	template: `
		<contact-form
			:aria-label="metadata.label"
			:aria-description="metadata.description"
			recipient-name="Seamus"
			:recipient-email="seamusWolf.email"
			:recipient-whatsapp="seamusWolf.phoneNumber"
			api-endpoint="/api/insurance/case"
			track-as="Insurance contact form"
			:static="static">
			<template v-slot:header>Ask our health insurance expert</template>
			<template v-slot:description>
				<h2 class="no-mobile">Ask our insurance expert</h2>
				<p>Seamus will answer your questions. He is an insurance expert with {{ seamusWolf.yearsOfExperience }} years of experience.</p>
				<p>He replies on the same day. His help is <strong>100% free</strong>.</p>
			</template>
			<template v-slot:image>
				<img
					srcset="/experts/photos/bioLarge1x/seamus-wolf.jpg, /experts/photos/bioLarge2x/seamus-wolf.jpg 2x"
					alt="Seamus Wolf" width="125" height="125"
					sizes="125px">
			</template>
		</contact-form>
	`,
}

import Collapsible from '/js/vue/components/collapsible.mjs';
import CountryInput from '/js/vue/components/country-input.mjs';
import DatePicker from '/js/vue/components/date-picker.mjs';
import EmailInput from '/js/vue/components/email-input.mjs';
import Eur from '/js/vue/components/eur.mjs';
import FullNameInput from '/js/vue/components/full-name-input.mjs';
import Glossary from '/js/vue/components/glossary.mjs';
import IconDonate from '/js/vue/components/icons/donate.mjs';
import IconExit from '/js/vue/components/icons/exit.mjs';
import IncomeInput from '/js/vue/components/income-input.mjs';
import Price from '/js/vue/components/price.mjs';
import Radio from '/js/vue/components/radio.mjs';
import Recommended from '/js/vue/components/recommended.mjs';
import StateInput from '/js/vue/components/state-input.mjs';

import { isEastGerman } from '/js/utils/germanStates.mjs';
import { calculatePensionRefund } from '/js/utils/pensionRefund.mjs';
import { pensions } from '/js/utils/constants.mjs';
import trackedStagesMixin from '/js/vue/mixins/trackedStages.mjs';
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import { userDefaults, userDefaultsMixin } from '/js/vue/mixins/userDefaults.mjs';
import { validateForm } from '/js/utils/form.mjs';
import { getNearestHeadingId } from '/js/utils/tracking.mjs';
import { getReferrer } from '/js/utils/tracking.mjs';

const { pensionRefundGermany, fundsback, germanyPensionRefund } = pensions.companies;

export default {
	components: {
		Collapsible,
		CountryInput,
		DatePicker,
		EmailInput,
		Eur,
		FullNameInput,
		Glossary,
		IconDonate,
		IconExit,
		IncomeInput,
		Price,
		Radio,
		Recommended,
		StateInput,
	},
	mixins: [userDefaultsMixin, uniqueIdsMixin, trackedStagesMixin],
	props: {
		static: Boolean
	},
	data() {
		return {
			trackAs: 'Pension refund calculator',

			stage: 'start',
			isLoading: false,
			nationality: userDefaults.empty,
			countryOfResidence: userDefaults.empty,
			yearlyIncome: userDefaults.empty,
			firstMonthOfWork: '',
			firstYearOfWork: '',
			lastMonthOfWork: '',
			lastYearOfWork: '',
			germanState: userDefaults.empty,
			fullName: userDefaults.empty,
			email: userDefaults.empty,
			dateOfBirth: userDefaults.empty,
			showRefundRequestForm: false,
			yearOptions: Array.from({ length: ((new Date()).getFullYear() + 2 - 2000) + 1}, (_, i) => 2000 + i), // From 2000 to currentYear + 2
			monthOptions: [
				{number: '01', name: 'January'},
				{number: '02', name: 'February'},
				{number: '03', name: 'March'},
				{number: '04', name: 'April'},
				{number: '05', name: 'May'},
				{number: '06', name: 'June'},
				{number: '07', name: 'July'},
				{number: '08', name: 'August'},
				{number: '09', name: 'September'},
				{number: '10', name: 'October'},
				{number: '11', name: 'November'},
				{number: '12', name: 'December'},
			],
			partners: [
				{
					name: 'Pension Refund Germany',
					key: 'pensionrefundgermany',
					recommended: true,
					fee: x => Math.min(x * pensionRefundGermany.fee, pensionRefundGermany.maxFee),
				},
				{
					name: 'FundsBack',
					key: 'fundsback',
					fee: x => Math.min(Math.max(x * fundsback.fee, fundsback.minFee), fundsback.maxFee),
				},
				{
					name: 'Germany Pension Refund',
					key: 'germanypensionrefund',
					fee: x => Math.min(x * germanyPensionRefund.fee, germanyPensionRefund.maxFee),
				},
				{
					name: 'Do it yourself',
					fee: x => 0,
				},
			],
			selectedPartner: null,
		};
	},
	methods: {
		hasFlag(flag) {
			return this.results && this.results.flags.has(flag);
		},
		async setReminder() {
			if(validateForm(this.$refs.reminderForm)) {
				this.isLoading = true;
				const response = await fetch(
					'/api/forms/pension-refund-reminder',
					{
						method: 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8',},
						body: JSON.stringify({
							email: this.email,
							refund_amount: Math.round(this.results.refundAmount),
							delivery_date: this.eligibilityDate,
						}),
					}
				);
				this.isLoading = false;
				this.stage = response.ok ? 'reminderConfirmation' : 'error';
			}
		},
		async sendRefundRequest() {
			if(validateForm(this.$refs.contactForm)) {
				this.isLoading = true;
				const response = await fetch(
					'/api/forms/pension-refund-request',
					{
						method: 'POST',
						keepalive: true,
						headers: {'Content-Type': 'application/json; charset=utf-8'},
						body: JSON.stringify({
							arrival_date: `${this.firstYearOfWork}-${this.firstMonthOfWork}-01`,
							departure_date: `${this.lastYearOfWork}-${this.lastMonthOfWork}-01`,
							birth_date: this.dateOfBirth,
							nationality: this.nationality,
							country_of_residence: this.countryOfResidence,
							email: this.email,
							name: this.fullName,
							partner: this.selectedPartner.key,
						}),
					},
				);
				this.isLoading = false;
				if(response.ok){
					plausible('Pension refund request', { props: {
						partner: this.selectedPartner.name,
						pageSection: getNearestHeadingId(this.$el),
						referrer: getReferrer(),
					}});
					this.stage = 'requestConfirmation';
				}
				else{
					this.stage = 'error';
				}
			}
		}
	},
	computed: {
		firstDayOfWork() {
			if(this.firstMonthOfWork && this.firstYearOfWork) {
				return new Date(`${this.firstYearOfWork}-${this.firstMonthOfWork}-01T00:00:00`);
			}
			return null;
		},
		lastDayOfWork() {
			if(this.lastMonthOfWork && this.lastYearOfWork) {
				const lastDayOfWork = new Date(`${this.lastYearOfWork}-${this.lastMonthOfWork}-01T00:00:00`);
				lastDayOfWork.setMonth(lastDayOfWork.getMonth()+1);
				lastDayOfWork.setDate(0);
				return lastDayOfWork; // Last day of the selected month
			}
			return null;
		},
		results() {
			return calculatePensionRefund(
				this.nationality,
				this.countryOfResidence,
				this.firstDayOfWork,
				this.lastDayOfWork,
				this.yearlyIncome,
				isEastGerman(this.germanState)
			);
		},
		isCountriesSelected() {
			return !!(this.nationality && this.countryOfResidence);
		},
		isCountryOfResidenceEligible() {
			return (
				this.results
				&& !this.hasFlag('eu-resident')
				&& !this.hasFlag('disqualifying-country-resident')
				&& !(
					this.hasFlag('israel-national')
					&& this.hasFlag('israel-resident')
				)
				&& !this.hasFlag('uk-resident')
			);
		},
		isNationalityEligible() {
			return (
				this.results
				&& !this.hasFlag('eu-national')
				&& !this.hasFlag('eea-national')
				&& !this.hasFlag('uk-national')
			);
		},
		isCountriesEligible() {
			return this.results && this.isCountryOfResidenceEligible && this.isNationalityEligible
		},
		isDateRangeSelected() {
			return this.firstDayOfWork && this.lastDayOfWork;
		},
		isDateRangeEligible() {
			return this.isDateRangeSelected && this.lastDayOfWork >= this.firstDayOfWork && this.results && !this.hasFlag('not-eligible');
		},
		eligibilityDate() {
			if(this.isDateRangeEligible) {
				const twoYearsAfterDeparture = new Date(this.lastDayOfWork.getTime());
				twoYearsAfterDeparture.setMonth(this.lastDayOfWork.getMonth() + 24 + 1); // +1 because last payment is 1 month after last month of work
				return twoYearsAfterDeparture;
			}
		},
		eligibilityDateString() {
			const monthName = this.monthOptions.find(m => m.number == (this.eligibilityDate.getMonth() + 1).toString().padStart(2, '0')).name;
			return `${monthName} ${this.eligibilityDate.getFullYear()}`;
		},
		monthsUntilEligible() {
			if(this.isDateRangeEligible) {
				const months = Math.floor((this.eligibilityDate.getTime() - (new Date()).getTime()) / (2e3 * 3600 * 365.25))
				if(months === 0) {
					return 'a few days';
				}
				else if(months === 1) {
					return '1 month';
				}
				else {
					return `${months} months`;
				}
			}
		},
		showStatePicker() {
			// Only show the state picker if the state can affect the refund amount
			if(!(this.results && this.results.refundAmount)) { return false; }

			const args = [this.nationality, this.countryOfResidence, this.firstDayOfWork, this.lastDayOfWork, this.yearlyIncome];
			const eastGermanResults = calculatePensionRefund(...args, true).refundAmount;
			const westGermanResults = calculatePensionRefund(...args, false).refundAmount;
			return eastGermanResults != westGermanResults;
		},
	},
	watch: {
		results(){
			this.selectedPartner = this.partners[0];
		}
	},
	template: `
		<collapsible
			aria-description="Calculate how much money you get back when you request a refund of your German pension payments."
			aria-label="Pension refund calculator"
			class="pension-refund-calculator"
			:static="static">
			<template v-slot:header>Calculate your pension refund</template>

			<p v-if="stage === 'start'">This calculator tells you if you can get a pension refund, and how much you can get back.</p>
			<template v-if="stage === 'start'">
				<hr>
				<div class="form-group">
					<label :for="uid('nationality')">
						Nationality
					</label>
					<country-input
						country-code
						:class="{'error': !isNationalityEligible}"
						:id="uid('nationality')"
						v-model="nationality"
						required></country-input>
				</div>
				<div class="form-group">
					<label :for="uid('countryOfResidence')">
						Where do you live?
					</label>
					<country-input
						country-code
						:class="{'error': !isCountryOfResidenceEligible}"
						:id="uid('countryOfResidence')"
						v-model="countryOfResidence"
						required></country-input>
				</div>
				<template v-if="results && !isCountriesEligible">
					<hr>
					<h3>You can't get a pension refund</h3>
					<p v-if="hasFlag('eu-national')">You can't get a German pension refund because you are a European Union citizen.</p>
					<p v-if="hasFlag('eea-national')">You can't get a German pension refund because you are a <glossary term="EEA">European Economic Area</glossary> citizen.</p>
					<p v-if="hasFlag('eu-resident')">You can't get a German pension refund while you live in the European Union. If you leave the European Union, you can get a refund.</p>
					<p v-if="hasFlag('disqualifying-country-resident')">You can't get a German pension refund while you live in Bosnia-Herzegovina, Kosovo, North Macedonia, Serbia or Turkey.</p>
					<p v-if="hasFlag('israel-national') && hasFlag('israel-resident')">You can't get a pension refund because you live in Israel. If you leave Israel, you can get a pension refund.</p>
					<p v-if="hasFlag('uk-national')">You can't get a pension refund because you are a citizen of the United Kingdom.</p>
					<p v-else-if="hasFlag('uk-resident')">You can't get a pension refund while you live in the United Kingdom. If you leave the UK, you can get a pension refund.</p>
				</template>
				<template v-if="isCountriesSelected && isCountriesEligible">
					<hr>
					<div class="form-group">
						<span class="label">First day of work</span>
						<div class="input-group">
							<select
								class="month-input"
								:class="{error: isDateRangeSelected && !isDateRangeEligible, placeholder: !firstMonthOfWork}"
								aria-label="First month of work in Germany"
								:aria-describedby="uid('instructions-time-in-germany')"
								title="First month of work in Germany"
								v-model="firstMonthOfWork">
								<option value="" disabled selected hidden>Month</option>
								<option v-for="month in monthOptions" :key="month.number" :value="month.number">{{ month.name }}</option>
							</select>
							<select
								class="year-input"
								:class="{error: isDateRangeSelected && !isDateRangeEligible, placeholder: !firstYearOfWork}"
								aria-label="First year of work in Germany"
								:aria-describedby="uid('instructions-time-in-germany')"
								title="First year of work in Germany"
								v-model="firstYearOfWork">
								<option value="" disabled selected hidden>Year</option>
								<option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
							</select>
						</div>
					</div>
					<div class="form-group">
						<span class="label">Last day of work</span>
						<div class="input-group">
							<select
								class="month-input"
								:class="{error: isDateRangeSelected && !isDateRangeEligible, placeholder: !lastMonthOfWork}"
								aria-label="Last month of work in Germany"
								:aria-describedby="uid('instructions-time-in-germany')"
								title="Last month of work in Germany"
								v-model="lastMonthOfWork">
								<option value="" disabled selected hidden>Month</option>
								<option v-for="month in monthOptions" :key="month.number" :value="month.number">{{ month.name }}</option>
							</select>
							<select
								class="year-input"
								:class="{error: isDateRangeSelected && !isDateRangeEligible, placeholder: !lastYearOfWork}"
								aria-label="Last year of work in Germany"
								:aria-describedby="uid('instructions-time-in-germany')"
								title="Last year of work in Germany"
								v-model="lastYearOfWork">
								<option value="" disabled selected hidden>Year</option>
								<option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
							</select>
							<span class="input-instructions" :id="uid('instructions-time-in-germany')">Only include the months that you worked in Germany.</span>
						</div>
					</div>
					<template v-if="isDateRangeSelected && isDateRangeEligible">
						<hr>
						<div class="form-group show-errors">
							<label :for="uid('income')">
								Salary in Germany
							</label>
							<div class="input-group">
								<income-input :id="uid('income')" v-model="yearlyIncome"></income-input>
								€&nbsp;per&nbsp;year
							</div>
						</div>
						<div class="form-group" v-if="showStatePicker">
							<label :for="uid('germanState')">
								Where did you work?
							</label>
							<state-input east-west-berlin :id="uid('germanState')" v-model="germanState" :aria-describedby="uid('instructions-east-west')"></state-input>
							<span class="input-instructions" :id="uid('instructions-east-west')">You lived in a former East German state. You made smaller pension payments, so your refund is smaller.</span>
						</div>
						<template v-if="results && results.refundAmount">
							<hr>
							<price class="large" :amount="results.refundAmount"></price>
							<p>You can get <eur :amount="results.refundAmount"></eur> back. This is what you paid into the German pension system.</p>
							<hr>
							<template v-if="hasFlag('eligible')">
								<div class="buttons bar">
									<button class="button primary" target="_blank" @click="stage = 'partnerSelection'">
										Apply for a refund <i class="icon right" aria-hidden="true"></i>
									</button>
								</div>
							</template>
							<template v-if="hasFlag('eligible-later')">
								<p>You can apply for a refund in <strong>{{ monthsUntilEligible }}</strong>. That's 2 years after your last pension contribution.</p>
								<p class="no-print">Enter your email to get a reminder in {{ eligibilityDateString }}.</p>
								<div class="input-group email-reminder no-print" ref="reminderForm">
									<email-input v-model="email" required></email-input>
									<button class="button primary" @click="setReminder" :disabled="isLoading" :class="{loading: isLoading}">
										Remind me in {{ monthsUntilEligible }}
									</button>
								</div>
							</template>
						</template>
					</template>
					<template v-if="isDateRangeSelected && !isDateRangeEligible && firstDayOfWork <= lastDayOfWork">
						<hr>
						<h3>You can't get a pension refund</h3>
						<p v-if="hasFlag('over-5-years')">You can't get a pension refund because you made pension payments for over 60 months. When you are 67 years old, you can receive a German pension.</p>
						<p v-if="hasFlag('uk-national') && hasFlag('uk-prebrexit')">You can't get a pension refund because <strong>you are a UK citizen, and you worked in Germany before Brexit</strong>. When you are 67 years old, you can receive a German pension.</p>
						<p v-if="hasFlag('uk-resident') && hasFlag('uk-prebrexit') && !hasFlag('uk-national')">You can't get a pension refund because <strong>you live in the UK, and you worked in Germany before Brexit</strong>. If you leave the UK, you can get a pension refund.</p>
						<p v-if="hasFlag('japan-national') && hasFlag('japan-resident')">If you leave Japan, you can ask for a refund.</p>
					</template>
				</template>
			</template>
			<template v-if="stage === 'reminderConfirmation'">
				<p><strong>Reminder set!</strong> We will send you an email in {{ monthsUntilEligible }}.</p>
				<ul class="buttons list">
					<li>
						<a href="/guides/leaving-germany" target="_blank">
							<icon-exit/>
							<div>
								<h3>Learn how to leave Germany</h3>
								<p>Use my checklist for moving to another country.</p>
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
				<div class="buttons bar">
					<button class="button" @click="email = '';stage = 'start'"><i class="icon left" aria-hidden="true"></i> Back to calculator</button>
				</div>
			</template>
			<template v-if="stage === 'partnerSelection'">
				<p>You can pay someone to request your pension refund. They do all the work for you, and transfer the refund to your bank account.&thinsp;—&thinsp;<a href="/guides/pension-payments-refund#get-help-from-someone">More information</a></p>
				<div class="form-group">
					<span class="label">Choose a helper</span>
					<radio v-for="partner in partners" v-model="selectedPartner" :value="partner" :key="partner.name">
						<div>{{ partner.name }} <recommended v-if="partner.recommended"></recommended></div>
					</radio>
				</div>
				<hr>
				<template v-if="selectedPartner.name === 'Do it yourself'">
					<p>You can apply for a pension refund without help. It's harder, but if you speak German, it's not so bad.</p>
					<p><strong><a class="internal-link" href="/guides/pension-payments-refund#do-it-yourself">How to apply without help</a></strong></p>
				</template>
				<template v-if="selectedPartner.name !== 'Do it yourself'">
					<div class="form-group">
						<span class="label">Estimated refund</span>
						<div>
							<p class="price-line">
								Your pension refund
								<price :amount="results.refundAmount"></price>
							</p>
							<p class="price-line">
								{{ selectedPartner.name }} fee
								<price :amount="selectedPartner.fee(results.refundAmount)"></price>
							</p>
							<p class="price-line highlighted">
								You keep
								<price :amount="Math.max(results.refundAmount - selectedPartner.fee(results.refundAmount), 0)"></price>
							</p>
						</div>
					</div>
					<hr>
					<div class="buttons bar">
						<button class="button" @click="stage = 'start'"><i class="icon left" aria-hidden="true"></i> Back</button>
						<button class="button primary" @click="stage = 'contactInfo'">Request a refund</button>
					</div>
				</template>
			</template>
			<template v-if="stage === 'contactInfo'">
				<div ref="contactForm">
					<div class="form-group">
						<label :for="uid('name')">Full name</label>
						<full-name-input v-model="fullName" :id="uid('name')" required></full-name-input>
					</div>
					<div class="form-group">
						<label :for="uid('email')">Email address</label>
						<email-input v-model="email" :id="uid('email')" required></email-input>
					</div>
					<div class="form-group">
						<label :for="uid('date-of-birth')">Date of birth</label>
						<date-picker v-model="dateOfBirth" :id="uid('date-of-birth')" required autocomplete="bday" :aria-describedby="uid('instructions-date-of-birth')"></date-picker>
						<span class="input-instructions" :id="uid('instructions-date-of-birth')">Required by the <glossary>Deutsche Rentenversicherung</glossary></span>
					</div>
				</div>
				<hr>
				<div class="buttons bar">
					<button class="button" @click="stage = 'partnerSelection'"><i class="icon left" aria-hidden="true"></i> Back</button>
					<button class="button primary" target="_blank" @click="sendRefundRequest" :disabled="isLoading" :class="{loading: isLoading}">Send request</button>
				</div>
			</template>
			<template v-if="stage === 'requestConfirmation'">
				<p><strong>Request sent!</strong> Your pension refund request was sent to {{ selectedPartner.name }}. They will contact you soon.</p>
				<hr>
				<div class="buttons bar">
					<button class="button" @click="stage = 'start'"><i class="icon left" aria-hidden="true"></i> Back</button>
				</div>
			</template>
			<template v-if="stage === 'error'">
				<p><strong>An error occurred.</strong> If this keeps happening, <a target="_blank" href="/contact">contact me</a>.</p>
				<hr>
				<div class="buttons bar">
					<button class="button" @click="email = '';stage = 'start'"><i class="icon left" aria-hidden="true"></i> Back to calculator</button>
				</div>
			</template>
		</collapsible>
	`
}
import { calculatePensionRefund } from '/js/utils/pensionRefund.mjs';
import { assert } from '/js/libs/chai.mjs';
import { yearsAgo, hasFlags } from '/js/utils/test.mjs';

describe('calculatePensionRefund', () => {
	describe('a 30,000€ income for 12 months in 2005', () => {
		const output = calculatePensionRefund('US', 'US', new Date(2005, 0, 1), new Date(2005, 11, 1), 30000, false);
		it('should calculate the correct pension refund', () => assert.equal(output.refundAmount, 30000 * 19.5/100 / 2));
	});

	describe('a 30,000€ income for 6 months in 2006 and 6 months in 2007', () => {
		const output = calculatePensionRefund('US', 'US', new Date(2006, 6, 1), new Date(2007, 5, 1), 30000, false);
		it('should calculate the correct pension refund', () => {
			assert.equal(output.refundAmount,
				(30000 * 19.5/100 / 2 * 6/12)
				+ (30000 * 19.9/100 / 2 * 6/12)
			);
		});
	});

	describe('a 30,000€ income from 2012 to 2015', () => {
		const output = calculatePensionRefund('US', 'US', new Date(2012, 6, 1), new Date(2015, 5, 1), 30000, false);
		it('should calculate the correct pension refund', () => {
			assert.equal(output.refundAmount,
				(30000 * 19.6/100 / 2 * 6/12) // 2012 (6 months)
				+ (30000 * 18.9/100 / 2) // 2013
				+ (30000 * 18.9/100 / 2) // 2014
				+ (30000 * 18.7/100 / 2 * 6/12) // 2015 (6 months)
			);
		});
	});

	describe('an EU national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('FR', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU national', () => {
				hasFlags(output, ['not-eligible', 'eu-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('FR', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU national', () => {
				hasFlags(output, ['not-eligible', 'eu-national']);
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('FR', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU national', () => {
				hasFlags(output, ['not-eligible', 'eu-national', 'uk-resident']);
			});
		});

		describe('who lives in a contracting country', () => {
			const output = calculatePensionRefund('FR', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU national', () => {
				hasFlags(output, ['not-eligible', 'eu-national']);
			});
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('FR', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU national', () => {
				hasFlags(output, ['not-eligible', 'eu-national']);
			});
		});
	});

	describe('a EEA national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('CH', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EEA national', () => {
				hasFlags(output, ['not-eligible', 'eea-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('CH', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EEA national', () => {
				hasFlags(output, ['not-eligible', 'eea-national']);
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('CH', 'UK', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EEA national', () => {
				hasFlags(output, ['not-eligible', 'eea-national']);
			});
		});

		describe('who lives in a contracting country', () => {
			const output = calculatePensionRefund('CH', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EEA national', () => {
				hasFlags(output, ['not-eligible', 'eea-national']);
			});
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('CH', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EEA national', () => {
				hasFlags(output, ['not-eligible', 'eea-national']);
			});
		});
	});

	describe('a contracting country national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('CA', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'contracting-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('CA', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'contracting-national']));
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('CA', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'contracting-national', 'uk-resident']));
		});

		describe('who lives in a contracting country', () => {
			const output = calculatePensionRefund('CA', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'contracting-national']));
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('CA', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'contracting-national']));
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputBa = calculatePensionRefund('CA', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMk = calculatePensionRefund('CA', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRs = calculatePensionRefund('CA', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXk = calculatePensionRefund('CA', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('CA', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputBa, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputMk, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputRs, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputXk, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputMe, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('CA', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
			});
		});

		describe('who worked more than 5 years in Germany', () => {
			const outputLessThan2YearsAgo = calculatePensionRefund('CA', 'AO', yearsAgo(7), yearsAgo(1), 30000, false);
			const outputOver2YearsAgo = calculatePensionRefund('CA', 'AO', yearsAgo(16), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputLessThan2YearsAgo, ['not-eligible', 'over-5-years', 'contracting-national']);
				hasFlags(outputOver2YearsAgo, ['not-eligible', 'over-5-years', 'contracting-national']);
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('CA', 'AO', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => hasFlags(output, ['eligible-later', 'contracting-national']));
		});
	});

	describe('a Brazilian national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('BR', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'contracting-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('BR', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'contracting-national']);
			});
		});

		describe('who lives in Brazil', () => {
			describe('and worked in Germany for over 5 years', () => {
				const output = calculatePensionRefund('BR', 'BR', yearsAgo(15), yearsAgo(8), 30000, false);
				it('is not eligible for a refund', () => {
					hasFlags(output, ['not-eligible', 'contracting-national', 'over-5-years']);
				});
			});
			describe('and worked in Germany for less than 5 years', () => {
				const output = calculatePensionRefund('BR', 'BR', yearsAgo(15), yearsAgo(13), 30000, false);
				it('is eligible for a refund', () => {
					hasFlags(output, ['eligible', 'contracting-national']);
				});
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('BR', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'contracting-national', 'uk-resident']);
			});
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputBa = calculatePensionRefund('BR', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMk = calculatePensionRefund('BR', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRs = calculatePensionRefund('BR', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXk = calculatePensionRefund('BR', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('BR', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputBa, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputMk, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputRs, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputXk, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
				hasFlags(outputMe, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('BR', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'contracting-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in another country', () => {
			describe('and worked in Germany for over 5 years', () => {
				const output = calculatePensionRefund('BR', 'CA', yearsAgo(15), yearsAgo(8), 30000, false);
				it('is not eligible for a refund', () => {
					hasFlags(output, ['not-eligible', 'contracting-national', 'over-5-years' ]);
				});
			});
			describe('and worked in Germany for less than 5 years', () => {
				const output = calculatePensionRefund('BR', 'CA', yearsAgo(15), yearsAgo(13), 30000, false);
				it('is eligible for a refund', () => {
					hasFlags(output, ['eligible', 'contracting-national']);
				});
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('BR', 'CA', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => {
				hasFlags(output, ['eligible-later', 'contracting-national']);
			});
		});
	});

	describe('a British national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('GB', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'uk-national']);
			});
		});

		describe('who lives in Canada', () => {
			const output = calculatePensionRefund('GB', 'CA', new Date(2021, 0, 1), new Date(2021, 3, 1), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'uk-national']);
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('GB', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'uk-national', 'uk-resident']);
			});
		});
	});

	describe('a Bosnian, Kosovar, Macedonian, Serbian or Montenegran national', () => {
		describe('who lives in the EU', () => {
			const outputRs = calculatePensionRefund('RS', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('ME', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(outputRs, ['not-eligible', 'eu-resident', 'balkanblock-national']);
				hasFlags(outputMe, ['not-eligible', 'eu-resident', 'balkanblock-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('RS', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'balkanblock-national']));
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('RS', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'balkanblock-national', 'uk-resident']));
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputRsBa = calculatePensionRefund('RS', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRsMk = calculatePensionRefund('RS', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRsRs = calculatePensionRefund('RS', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRsXk = calculatePensionRefund('RS', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRsMe = calculatePensionRefund('RS', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);

			const outputBaBa = calculatePensionRefund('BA', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputBaMk = calculatePensionRefund('BA', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputBaRs = calculatePensionRefund('BA', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputBaXk = calculatePensionRefund('BA', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputBaMe = calculatePensionRefund('BA', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);

			const outputMkBa = calculatePensionRefund('MK', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMkMk = calculatePensionRefund('MK', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMkRs = calculatePensionRefund('MK', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMkXk = calculatePensionRefund('MK', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMkMe = calculatePensionRefund('MK', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);

			const outputXkBa = calculatePensionRefund('XK', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXkMk = calculatePensionRefund('XK', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXkRs = calculatePensionRefund('XK', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXkXk = calculatePensionRefund('XK', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXkMe = calculatePensionRefund('XK', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);

			const outputMeBa = calculatePensionRefund('ME', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMeMk = calculatePensionRefund('ME', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMeRs = calculatePensionRefund('ME', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMeXk = calculatePensionRefund('ME', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMeMe = calculatePensionRefund('ME', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);

			it('is not eligible for a refund', () => {
				hasFlags(outputRsBa, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputRsMk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputRsRs, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputRsXk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputRsMe, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);

				hasFlags(outputBaBa, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputBaMk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputBaRs, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputBaXk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputBaMe, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);

				hasFlags(outputMkBa, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMkMk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMkRs, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMkXk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMkMe, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);

				hasFlags(outputXkBa, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputXkMk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputXkRs, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputXkXk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputXkMe, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);

				hasFlags(outputMeBa, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMeMk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMeRs, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMeXk, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
				hasFlags(outputMeMe, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('RS', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'balkanblock-national', 'disqualifying-country-resident']));
		});

		describe('who lives in a contracting country', () => {
			const output = calculatePensionRefund('RS', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'balkanblock-national']));
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('RS', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'balkanblock-national']));
		});

		describe('who worked more than 5 years in Germany', () => {
			const outputLessThan2YearsAgo = calculatePensionRefund('RS', 'AO', yearsAgo(7), yearsAgo(1), 30000, false);
			const outputOver2YearsAgo = calculatePensionRefund('RS', 'AO', yearsAgo(16), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputLessThan2YearsAgo, ['not-eligible', 'over-5-years', 'balkanblock-national']);
				hasFlags(outputOver2YearsAgo, ['not-eligible', 'over-5-years', 'balkanblock-national']);
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('RS', 'AO', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => hasFlags(output, ['eligible-later', 'balkanblock-national']));
		});
	});

	describe('an Israeli national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('IL', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'israel-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('IL', 'CH', yearsAgo(12), yearsAgo(10), false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'israel-national']));
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('IL', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'israel-national', 'uk-resident']);
			});
		});

		describe('who lives in Israel', () => {
			const output = calculatePensionRefund('IL', 'IL', yearsAgo(12), yearsAgo(10), false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'israel-national', 'israel-resident']));
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputBa = calculatePensionRefund('IL', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMk = calculatePensionRefund('IL', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRs = calculatePensionRefund('IL', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXk = calculatePensionRefund('IL', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('IL', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputBa, ['not-eligible', 'israel-national', 'disqualifying-country-resident']);
				hasFlags(outputMk, ['not-eligible', 'israel-national', 'disqualifying-country-resident']);
				hasFlags(outputRs, ['not-eligible', 'israel-national', 'disqualifying-country-resident']);
				hasFlags(outputXk, ['not-eligible', 'israel-national', 'disqualifying-country-resident']);
				hasFlags(outputMe, ['not-eligible', 'israel-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('IL', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'israel-national', 'disqualifying-country-resident']));
		});

		describe('who lives in another contracting country', () => {
			const output = calculatePensionRefund('IL', 'CA', yearsAgo(12), yearsAgo(10), false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'israel-national']));
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('IL', 'AO', yearsAgo(12), yearsAgo(10), false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'israel-national']));
		});

		describe('who worked more than 5 years in Germany', () => {
			const outputLessThan2YearsAgo = calculatePensionRefund('IL', 'AO', yearsAgo(7), yearsAgo(1), false);
			const outputOver2YearsAgo = calculatePensionRefund('IL', 'AO', yearsAgo(16), yearsAgo(10), false);
			it('is not eligible for a refund', () => {
				hasFlags(outputLessThan2YearsAgo, ['not-eligible', 'over-5-years', 'israel-national']);
				hasFlags(outputOver2YearsAgo, ['not-eligible', 'over-5-years', 'israel-national']);
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('IL', 'AO', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => hasFlags(output, ['eligible-later', 'israel-national']));
		});
	});

	describe('a Japanese national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('JP', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'japan-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('JP', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'japan-national']));
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('JP', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'japan-national', 'uk-resident']);
			});
		});

		describe('who lives in Japan', () => {
			describe('and worked for over 5 years in Germany', () => {
				const output = calculatePensionRefund('JP', 'JP', yearsAgo(17), yearsAgo(10), 30000, false);
				it('is not eligible for a refund', () => {
					hasFlags(output, ['not-eligible', 'japan-national', 'japan-resident', 'over-5-years']);
				});
			});
			describe('and worked for less than 5 years in Germany', () => {
				const output = calculatePensionRefund('JP', 'JP', yearsAgo(12), yearsAgo(10), 30000, false);
				it('is eligible for a refund', () => hasFlags(output, ['eligible', 'japan-national', 'japan-resident']));
			});
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputBa = calculatePensionRefund('JP', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMk = calculatePensionRefund('JP', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRs = calculatePensionRefund('JP', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXk = calculatePensionRefund('JP', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('JP', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(outputBa, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
				hasFlags(outputMk, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
				hasFlags(outputRs, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
				hasFlags(outputXk, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
				hasFlags(outputMe, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('JP', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => {
				hasFlags(output, ['not-eligible', 'japan-national', 'disqualifying-country-resident']);
			});
		});

		describe('who lives in another country', () => {
			describe('and worked for over 5 years in Germany', () => {
				const output = calculatePensionRefund('JP', 'CA', yearsAgo(17), yearsAgo(10), 30000, false);
				it('is eligible for a refund', () => hasFlags(output, ['eligible', 'japan-national']));
			});
			describe('and worked for less than 5 years in Germany', () => {
				const output = calculatePensionRefund('JP', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
				it('is eligible for a refund', () => hasFlags(output, ['eligible', 'japan-national']));
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			describe('and worked for over 5 years in Germany', () => {
				it('is not eligible for a refund while in Japan', () => {
					const output = calculatePensionRefund('JP', 'JP', yearsAgo(7), yearsAgo(1), 30000, false);
					hasFlags(output, ['not-eligible', 'japan-national', 'japan-resident', 'over-5-years']);
				});
				it('is eligible for a refund while not in Japan', () => {
					const output = calculatePensionRefund('JP', 'CA', yearsAgo(7), yearsAgo(1), 30000, false);
					hasFlags(output, ['eligible-later', 'japan-national']);
				});
			});
			describe('and worked for less than 5 years in Germany', () => {
				it('is eligible for a refund while in Japan', () => {
					const output = calculatePensionRefund('JP', 'JP', yearsAgo(3), yearsAgo(1), 30000, false);
					hasFlags(output, ['eligible-later', 'japan-national', 'japan-resident']);
				});
				it('is eligible for a refund while not in Japan', () => {
					const output = calculatePensionRefund('JP', 'CA', yearsAgo(3), yearsAgo(1), 30000, false);
					hasFlags(output, ['eligible-later', 'japan-national']);
				});
			});
		});
	});

	describe('a Turkish national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('TR', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'turkey-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('TR', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'turkey-national']));
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('TR', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'turkey-national', 'uk-resident']));
		});

		describe('who lives in another contracting country', () => {
			const output = calculatePensionRefund('TR', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'turkey-national']));
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('TR', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => hasFlags(output, ['eligible', 'turkey-national']));
		});

		describe('who worked more than 5 years in Germany', () => {
			it('is eligible for a refund if he lives in Turkey', () => {
				const outputLessThan2YearsAgo = calculatePensionRefund('TR', 'TR', yearsAgo(7), yearsAgo(1), 30000, false);
				const outputOver2YearsAgo = calculatePensionRefund('TR', 'TR', yearsAgo(16), yearsAgo(10), 30000, false);
				hasFlags(outputLessThan2YearsAgo, ['eligible-later', 'turkey-national', 'turkey-resident']);
				hasFlags(outputOver2YearsAgo, ['eligible', 'turkey-national', 'turkey-resident']);
			});

			it('is not eligible for a refund', () => {
				const outputLessThan2YearsAgo = calculatePensionRefund('TR', 'AO', yearsAgo(7), yearsAgo(1), 30000, false);
				const outputOver2YearsAgo = calculatePensionRefund('TR', 'AO', yearsAgo(16), yearsAgo(10), 30000, false);
				hasFlags(outputLessThan2YearsAgo, ['not-eligible', 'over-5-years', 'turkey-national']);
				hasFlags(outputOver2YearsAgo, ['not-eligible', 'over-5-years', 'turkey-national']);
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('IL', 'AO', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => hasFlags(output, ['eligible-later', 'israel-national']));
		});
	});

	describe('a Uruguayan national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('UY', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'contracting-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('UY', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'contracting-national']);
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('UY', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'contracting-national', 'uk-resident']));
		});

		describe('who lives in Uruguay', () => {
			describe('and worked in Germany for over 5 years', () => {
				const output = calculatePensionRefund('UY', 'UY', yearsAgo(15), yearsAgo(8), 30000, false);
				it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'contracting-national', 'over-5-years']));
			});
			describe('and worked in Germany for less than 5 years', () => {
				const output = calculatePensionRefund('UY', 'UY', yearsAgo(15), yearsAgo(13), 30000, false);
				it('is eligible for a refund', () => hasFlags(output, ['eligible', 'contracting-national']));
			});
		});

		describe('who lives in another country', () => {
			describe('and worked in Germany for over 5 years', () => {
				const output = calculatePensionRefund('UY', 'CA', yearsAgo(15), yearsAgo(8), 30000, false);
				it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'contracting-national', 'over-5-years']));
			});
			describe('and worked in Germany for less than 5 years', () => {
				const output = calculatePensionRefund('UY', 'CA', yearsAgo(15), yearsAgo(13), 30000, false);
				it('is eligible for a refund', () => hasFlags(output, ['eligible', 'contracting-national']));
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const output = calculatePensionRefund('UY', 'CA', yearsAgo(3), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => hasFlags(output, ['eligible-later', 'contracting-national']));
		});
	});

	describe('a non-contracting country national', () => {
		describe('who lives in the EU', () => {
			const output = calculatePensionRefund('AO', 'FR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund, because he is an EU resident', () => {
				hasFlags(output, ['not-eligible', 'eu-resident', 'noncontracting-national']);
			});
		});

		describe('who lives in the EEA', () => {
			const output = calculatePensionRefund('AO', 'CH', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'noncontracting-national']);
			});
		});

		describe('who lives in a contracting country', () => {
			const output = calculatePensionRefund('AO', 'CA', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'noncontracting-national']);
			});
		});

		describe('who lives in a non-contracting country', () => {
			const output = calculatePensionRefund('AO', 'AO', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'noncontracting-national']);
			});
		});

		describe('who lives in the UK', () => {
			const output = calculatePensionRefund('AO', 'GB', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is not eligible for a refund', () => hasFlags(output, ['not-eligible', 'noncontracting-national', 'uk-resident']));
		});

		describe('who worked more than 5 years in Germany', () => {
			const outputLessThan2YearsAgo = calculatePensionRefund('AO', 'AO', yearsAgo(7), yearsAgo(1), 30000, false);
			const outputOver2YearsAgo = calculatePensionRefund('AO', 'AO', yearsAgo(16), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(outputLessThan2YearsAgo, ['eligible-later', 'noncontracting-national']);
				hasFlags(outputOver2YearsAgo, ['eligible', 'noncontracting-national']);
			});
		});

		describe('who lives in Bosnia, Kosovo, Macedonia, Serbia or Montenegro', () => {
			const outputBa = calculatePensionRefund('AO', 'BA', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMk = calculatePensionRefund('AO', 'MK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputRs = calculatePensionRefund('AO', 'RS', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputXk = calculatePensionRefund('AO', 'XK', yearsAgo(12), yearsAgo(10), 30000, false);
			const outputMe = calculatePensionRefund('AO', 'ME', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(outputBa, ['eligible', 'noncontracting-national',]);
				hasFlags(outputMk, ['eligible', 'noncontracting-national',]);
				hasFlags(outputRs, ['eligible', 'noncontracting-national',]);
				hasFlags(outputXk, ['eligible', 'noncontracting-national',]);
				hasFlags(outputMe, ['eligible', 'noncontracting-national',]);
			});
		});

		describe('who lives in Turkey', () => {
			const output = calculatePensionRefund('AO', 'TR', yearsAgo(12), yearsAgo(10), 30000, false);
			it('is eligible for a refund', () => {
				hasFlags(output, ['eligible', 'noncontracting-national']);
			});
		});

		describe('who left the EU less than 2 years ago', () => {
			const outputUnder5YearsInGermany = calculatePensionRefund('AO', 'AO', yearsAgo(3), yearsAgo(1), 30000, false);
			const outputOver5YearsInGermany = calculatePensionRefund('AO', 'AO', yearsAgo(8), yearsAgo(1), 30000, false);
			it('is eligible for a refund later', () => {
				hasFlags(outputUnder5YearsInGermany, ['eligible-later', 'noncontracting-national']);
				hasFlags(outputOver5YearsInGermany, ['eligible-later', 'noncontracting-national']);
			});
		});
	});
});
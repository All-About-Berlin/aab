---
title: What is the trade tax (Gewerbesteuer)?
short_title: How the trade tax works
description: If you are self-employed in Germany, you might need to pay a trade tax. This is how it works, and how much it costs.
date_created: 2021-01-19
---

Most German businesses must pay a trade tax (*[[Gewerbesteuer]]*) on their [profits](/glossary/Gewinn). If you [start a business in Germany](/guides/start-a-business-in-germany), you must understand how the trade tax works. This guide explains it.

{% tableOfContents %}

## Who must pay trade tax

**Sole proprietorships, partnerships and corporations** must pay the trade tax. This includes *[[Kleinunternehmer]]*.

Freelancers (*[[Freiberufler]]*) do not pay the trade tax. [Not all self-employed people](/guides/freiberufler-or-gewerbe) are freelancers. If you work alone, you might still need to pay the trade tax.

## How much is the trade tax?

In Berlin, trade tax is {{ GEWERBESTEUER_RATE_BERLIN }}% of all profit above €{{GEWERBESTEUER_FREIBETRAG|cur}} per year.[^1] As a sole proprietor, you get most of it back as an income tax credit.[^12] In the end **you pay {{GEWERBESTEUER_EXTRA_COST_BERLIN}}% more taxes** in total.

To calculate your trade tax:

1. Take your [profit](/glossary/Gewinn) for the year, and round it down to the nearest €100.[^11]
2. If you are a sole proprietor (*Einzelunternehmer*), remove €{{GEWERBESTEUER_FREIBETRAG|cur}} (the tax-free amount).
2. Multiply that by {{ GEWERBESTEUER_RATE }}%.
3. Multiply that by [the *Hebesatz* in your city](https://www.lexoffice.de/wissenswelt/gewerbesteuerhebesatz/). In Berlin, it's {{ GEWERBESTEUER_HEBESATZ_BERLIN }}%.

> **Example trade tax calculation**  
> For a sole proprietor in Berlin

> 1. **€{{45678|cur}} per year profit**, rounded down to €{{45600|cur}}
> 2. €{{45600|cur}} - €{{GEWERBESTEUER_FREIBETRAG|cur}} tax-free amount = €{{(45600 - GEWERBESTEUER_FREIBETRAG)|cur}} taxable profit
> 3. €{{(45600 - GEWERBESTEUER_FREIBETRAG)|cur}} × {{GEWERBESTEUER_RATE}}% = €{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_RATE/100)|cur}}
> 4. €{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_RATE/100)|cur}} × 410% = **€{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_RATE*GEWERBESTEUER_HEBESATZ_BERLIN/100)|cur}} trade tax**

If you are a sole proprietor (*Einzelunternehmer*), you get an income tax credit for the trade tax you pay.[^3] **You pay {{GEWERBESTEUER_RATE_BERLIN}}% trade tax, but you get {{ (GEWERBESTEUER_RATE * GEWERBESTEUER_TAX_CREDIT) }}% income tax back.** In other words, you only pay {{GEWERBESTEUER_EXTRA_COST_BERLIN}}% more taxes in total.

> €{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_RATE_BERLIN/100)|cur}} trade tax - €{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_RATE*GEWERBESTEUER_TAX_CREDIT/100)|cur}} [income tax](/glossary/Einkommensteuer) credit = **€{{((45600 - GEWERBESTEUER_FREIBETRAG)*GEWERBESTEUER_EXTRA_COST_BERLIN/100)|cur}} extra taxes**

**[Trade tax calculator](https://www.smart-rechner.de/gewerbesteuer/rechner.php)** - Smart-Rechner.de (in German)

### Tax-free amount

If you are a sole proprietor (*Einzelunternehmer*), the first €{{GEWERBESTEUER_FREIBETRAG|cur}} per year in profit are not taxed. If you have a society (*Verein*), the first €5,000 per year in profit are not taxed.[^4] If you have a corporation (*Kapitalgesellschaft*, *AG*, *GmbH*), the entire profit is taxed.[^5]

## IHK membership

In Berlin, all businesses that pay trade tax must join the [[IHK]] and pay the membership fee. The IHK membership fee is not the same as the trade tax.

**[IHK membership fee calculator ➞](https://www.ihk.de/berlin/ueber-uns/mitgliedschaft-und-beitrag/das-verfahren-der-beitragserhebung/beitragsberechnung-2280534)**

You get an IHK letter (*Beitragsbescheid*) every year. You have 30 days to pay. You can't automate payments with a [direct debit authorisation](/glossary/SEPA-Lastschriftmandat).[^10]

[![Example IHK Beitragsbescheid](/images/ihk-berlin-beitragsbescheid-gewerbesteuer.png "A Beitragsbescheid from the IHK")](/images/ihk-berlin-beitragsbescheid-gewerbesteuer.png)

## How to pay the trade tax

You start paying trade tax after you [do your *Gewerbeanmeldung*](/guides/gewerbeschein). Trade tax is collected by the *[[Finanzamt]]* at the same time as the [income tax](/glossary/Einkommensteuer).

Every year, you must make a [tax declaration](/glossary/Steuererklärung) for your business. A bit later, the *Finanzamt* will send you a tax assessment for income tax (*[Einkommensteuerbescheid](/glossary/Steuerbescheid)*) and trade tax (*Gewerbesteuerbescheid*). It tells you how much you need to pay.

If you have a high income, the *Finanzamt* can request advance tax payments (*Vorauszahlungen*) every quarter:[^6] on February 15, May 15, August 15 and November 15. You pay income tax and trade tax in advance, and it's adjusted later.

## Need help?

When you [start a business in Germany](/guides/start-a-business-in-germany), you should [hire a tax advisor](/guides/english-speaking-steuerberater-berlin) (*[[Steuerberater]]*). They can help you [register your business](/guides/fragebogen-zur-steuerlichen-erfassung), file your taxes, and solve other tax problems.

**[Where to ask business questions ➞](/guides/help#business-questions)**

[^1]: [Berlin.de](https://service.berlin.de/dienstleistung/325333/)
[^3]: [blog.consultinghouse.eu](https://blog.consultinghouse.eu/compliance/a-guide-to-the-german-trade-tax)
[^4]: [§ 11 GewStG](https://www.buzer.de/11_GewStG.htm)
[^5]: [fuer-gruender.de](https://www.fuer-gruender.de/wissen/unternehmen-gruenden/finanzen/steuern/gewerbesteuer/), [IHK Berlin](https://www.ihk.de/berlin/service-und-beratung/recht-und-steuern/steuern-und-finanzen/ertragssteuern-lohnsteuer/gewerbe-und-grundsteuer-index-2253124)
[^6]: [wwkn.de](https://wwkn.de/en/local-business-tax-gewerbesteuer/), [IHK Berlin](https://www.ihk.de/berlin/service-und-beratung/recht-und-steuern/steuern-und-finanzen/ertragssteuern-lohnsteuer/gewerbe-und-grundsteuer-index-2253124)
[^10]: [ttc.tax](https://ttc.tax/ihk-berlin-bietet-mitgliedern-keine-teilnahme-am-lastschriftverfahren-an/)
[^11]: [§ 11 Abs. 3 GewStG](https://www.buzer.de/11_GewStG.htm)
[^12]: [Haufe.de](https://www.haufe.de/finance/haufe-finance-office-premium/gewerbesteueranrechnung-steuerermaessigung-bei-gewerblich-31-grundfall_idesk_PI20354_HI2179474.html)
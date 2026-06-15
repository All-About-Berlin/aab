---
title: How to run a website in Germany
short_title: How to run a website
description: 'The laws and regulations you must follow to run a website legally in Germany: the Impressum, analytics, cookie banners, GDPR, etc.'
date_created: 2018-05-07
---

This guide explains the rules to follow when you run a website in Germany.

{% tableOfContents %}

## GDPR/[[DSGVO]] compliance

Businesses that serve [[European Union]] customers must follow the General Data Protection Regulation (GDPR in English, DSGVO in German).

The basic principles of GDPR:

1. **Do not collect data without consent**  
    Do not track people or collect information about them without their explicit consent.
2. **[Only collect the data that you need](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/how-much-data-can-be-collected_en)**
3. **[Delete the data when you no longer need it](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/how-long-can-data-be-kept-and-it-necessary-update-it_en)**
4. **[Be transparent about the data you collect from your users](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/what-information-must-be-given-individuals-whose-data-collected_en).**  
    Disclose what data you collect, why you collect it, and who you collect it for. Put this information in your privacy policy.[^20]
5. **[Only use the data for the intended purpose](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/overview-principles/what-data-can-we-process-and-under-which-conditions_en)**
6. **[Store the data about your users securely](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/overview-principles/what-data-can-we-process-and-under-which-conditions_en)**
7. **[Give your users a way to delete their data](https://gdpr-info.eu/art-17-gdpr/)**  
    People have the [right to be forgotten](https://gdpr-info.eu/issues/right-to-be-forgotten/). Give your users a way to close their account and erase their data.

### Who needs to do this?

All websites that serve people in the [[European Union]], no matter who runs the website or where it is hosted. It applies to personal, non-commercial websites too. See **[Who does the data protection law apply to?](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/application-regulation/who-does-data-protection-law-apply_en)** for more details.

### GDPR legal basis

- [General Data Protection Regulation](https://gdpr-info.eu/) ([[DSGVO]] in German)

### GDPR checklist

- [ ] Understand the GDPR regulation
- [ ] Only collect the data you really need
- [ ] Disclose what data you collect about your users
- [ ] Set an expiration date for the data you collect about your users
- [ ] Allow your users to delete the data you collect on them

## Cookies

If you use cookies on your website, you must follow a few rules:

- **Don't set tracking cookies without consent**  
    Before you set any tracking cookies, get consent from the user. Normally, you do this with a cookie banner.
- **Make it easy to refuse tracking**  
    Don't hide the "refuse tracking" button. Refusing must be as easy as accepting.
- **Don't force your users to accept tracking**  
    You can't make tracking cookies a condition for using your service. You can't say "by using this website, you agree to accept our cookies". You can't force users to accept tracking cookies in your terms and conditions.[^22]
- **Allow users to opt out of tracking.**  
    Users must have a way to opt out of tracking cookies, except for cookies that are needed to make the website work. Google Analytics is not needed to make the website work.
- **Necessary cookies do not need consent**  
    You don't need consent to set cookies that are necessary to make the website work. You don't need to allow the users to opt out of these cookies.[^0]
- **Explain how you use cookies in your privacy policy**  
    Your privacy policy must clearly explain what cookies you set, and what they are used for.
- **Be careful with embedded content**  
    YouTube videos, Disqus comments, Facebook buttons and other third-party widgets often set tracking cookies.[^1] Disable these widgets until you get consent from your users, or don't use them at all.

These articles helped me understand how cookies work with the GDPR:

- [Tracking cookies and GDPR](https://techblog.bozho.net/tracking-cookies-gdpr/)
- [Cookie consent: how do I comply with the GDPR?](https://www.cookiebot.com/en/cookie-consent/)

Tools like [CookieBot](https://www.cookiebot.com/en/cookie-consent/) can help you implement a cookie notice that is GDPR compliant.

### Cookie banners legal basis

In the [[European Union]], cookies were regulated by the [Cookie Directive](https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ:L:2009:337:0011:0036:En:PDF) and now by the [General Data Protection Regulation (GDPR)](https://gdpr-info.eu/), particularly articles 6 and 7.

### Cookie banner examples

- [CookieBot](https://www.cookiebot.com/en/cookie-consent/)'s cookie notice lets you choose which cookies you want to allow. Analytics cookies are enabled by default, and marketing cookies are disabled by default. Essential cookies cannot be disabled.
- [Gruender.de](https://www.gruender.de/recht/dsgvo-cookie-law/)'s cookie notice lets you choose which cookies you want to allow, with no pre-selected answer.
- [Piwik Pro](https://piwik.pro/blog/burning-questions-gdpr-answered-part-2-3/)'s cookie notice also lets you choose which cookies you want to allow, with no pre-selected answer.
- Many websites ask for permission before they load content from YouTube, Twitter and other websites.

### Cookies checklist

- [ ] If you use cookies, inform your users with a [detailed](https://www.cookiebot.com/en/cookie-consent/) cookie notice.
- [ ] Explain how and why you use cookies in your website's privacy policy.
- [ ] Require explicit consent from your users before setting tracking cookies, and give them a way to opt out of non-essential cookies.
- [ ] Make it easy to refuse cookies.
- [ ] Test your website with an ad blocker. Some ad blockers hide cookie consent notices, and break the website for some users.

## Tracking and analytics

If you use Google Analytics, you *must* get consent from your visitors before you track them. Do not track your users at all until you get consent.

Other tracking options like [Plausible](https://plausible.io) are privacy-friendly, and don't require a cookie notice. This is what I use on All About Berlin.

### Who needs consent for tracking?

Any EU resident or company who uses Google Analytics on their website.

### Tracking legal basis

The rules for tracking users are defined by the GDPR ([[DSGVO]] in German).

### Tracking checklist

- [ ] Do not track your users before you get their consent.
- [ ] Agree to the Google Analytics [Data Processing Terms](https://support.google.com/analytics/answer/3379636?hl=en).
- [ ] Configure Google Analytics to anonymize IP addresses.
- [ ] Delete the data Google Analytics collected before anonymizing IP addresses.
- [ ] Inform your users about Google Analytics cookies in your cookie notice, and in your privacy policy.
- [ ] Give your users a way to opt out of Google Analytics cookies.
- [ ] [Set the Google Analytics data retention period](https://support.google.com/analytics/answer/7667196?hl=en) to 14 months or less, and enable "Reset on new activity".

## Impressum

The [[Impressum]] is a page with your business' contact information. It helps users contact you.

Your Impressum page must be "easily identifiable, directly accessible and constantly available".[^4] In other words, it must be easy to find from any page on your website. It must be available in the same languages as your website.[^11]

Your Impressum must always contain...

- [ ] **The full name of the website owner**[^5]  
    If it's a company website, it must include the full name of the company, including its legal form (for example, *GmbH* or *UG*).
- [ ] **Contact information**  
    You must be quickly reachable electronically, and non-electronically.[^7] An email address that can be used to reach the company or website owner.[^6]
    - [ ] **Full address**  
        The full address of the company or website owner. You cannot use a PO box.[^8]
    - [ ] **Telephone number** (optional)  
        A phone number is not mandatory if the user has alternative options for rapid contact and direct and efficient communication.[^9]
- [ ] **[VAT number](/glossary/Umsatzsteuernummer)**
- [ ] **[[Handelsregisternummer]]**, if applicable
- [ ] **Names of the managing directors** and authorized representatives, if applicable

It's important to have a complete Impressum. You can get sued for damages if it's missing or incomplete.[^10] Some lawyers make money by finding invalid Impressum pages.

If you can, [hide your Impressum page from Google](https://developers.google.com/search/docs/crawling-indexing/control-what-you-share).

### Who needs an Impressum?

Any German resident or company who runs a commercial website, even if the website is hosted in another country, or has a .com domain.[^2] Personal, non-commercial websites do not need an Impressum.[^3]

**Commercial Facebook, Instagram and social media pages** must also have an Impressum.[^5]

### Impressum legal basis

- [§ 5 Digitale-Dienst-Gesetz (DDG)](https://www.buzer.de/5_DDG.htm)
- [§ 55 Rundfunkstaatsvertrag (RStV)](http://www.urheberrecht.org/law/normen/rstv/RStV-13/text/2010_06.php3)
- [§ 2 DL-InfoV](https://www.buzer.de/gesetz/9221/a165923.htm)

### Impressum examples

- [SAP's Impressum](https://www.sap.com/germany/about/legal/impressum.html)
- [BMW's Impressum](https://www.bmw.com/en/footer/imprint.html)
- [Facebook's Impressum](https://www.facebook.com/terms)
- [Google's Impressum](https://www.google.de/contact/impressum.html), featuring details of the authorized representative
- [A medical clinic's Impressum](https://hausarzt-raile.de/language/en/impress/), featuring details about supervisory authorities

### Impressum checklist

- [ ] Read the [Ministry of Justice's Impressum guidelines](https://www.bmuv.de/themen/verbraucherschutz/digitaler-verbraucherschutz/impressumspflicht).
- [ ] Add an Impressum to your website
    - [ ] Make your Impressum clearly visible and directly accessible from every page on your website.
    - [ ] Remove your Impressum from Google search results.
- [ ] [Add an Impressum to your Facebook page](https://www.facebook.com/help/342430852516247), if applicable.

## Privacy policy

Your website must have a privacy policy (*Datenschutzerklärung*) where you outline how you collect, process and use data about your users. If you fail to include a privacy policy on your website, you can receive an *[[Abmahnung]]*.[^12]

If you need help with your privacy policy, you can either [hire a lawyer](/guides/english-speaking-lawyers-berlin), or use a [privacy policy generator](https://www.iubenda.com/en/privacy-and-cookie-policy-generator).

### Who needs a privacy policy?

Any German resident or company who runs a website, even for non-commercial purposes.[^12]

### Privacy policy legal basis

A privacy policy is required by Articles 13 and 14 of the [[DSGVO]].[^13]

### Privacy policy examples

- [Stripe's privacy policy](https://stripe.com/de/privacy) contains detailed information about how they collect and process data about their users
- [N26's privacy policy](https://docs.n26.com/legal/01+DE/03+Privacy%20Policy/en/01privacy-policy-en.pdf) is a PDF file linked at the bottom of every page on their website
- [All About Berlin's privacy policy](/terms) is on the same page as our Impressum, and is linked at the bottom of every page

### Privacy policy checklist

- [ ] Add a privacy policy to your website
- [ ] Add a link to your privacy policy in the footer of every page

## Terms and conditions

Your website should have a terms and conditions ([[AGB]] or *Allgemeine Geschäftsbedingungen*) page. Usually, it's the page where you say "we are not responsible for the accuracy of our content".

The terms in conditions must be available in the same languages as your website.[^14]

### Who needs an AGB page?

It is not required unless you have customers, but it's always a good idea.[^15]

### AGB legal basis

The AGB is required by [§ 312d BGB](https://www.buzer.de/312d_BGB.htm) if you have customers.

### AGB checklist

- [ ] Add a terms and conditions page to your website. There are many AGB generators and templates online. Most of them are in German.
- [ ] Add a link to your terms an conditions to your website's footer.

## Creative Commons images

If you use images with a Creative Commons licence, make sure you properly attribute the author. In Germany, using the wrong attribution format can be a costly mistake. [I had to pay hundreds of euros in lawyer fees](https://nicolasbouliane.com/blog/abmahnung-creative-commons) for making that mistake.

Here are the basic guidelines about using Creative Commons images on your website:

- **Pay attention to the licence for the images you use on your website**. Wikipedia images are not always free to use. Ideally, use public domain images that can be used without restrictions. You can find public domain images on [pxhere.com](https://pxhere.com/).
- **Understand that "free images" sometimes come with conditions.** Some variants of the Creative Commons licence require attribution to the author, prohibit commercial use, and even prohibit derivative works. See [this overview](https://creativecommons.org/licenses/) for more details.
- **Use the correct format when giving credit to the author.** Proper credit includes the Title, the Author, the Source and the Licence. See [this guide](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License) for more details.

### Which images need attribution?

Anyone who uses Creative Commons media on their website. Most images that come from Wikipedia are under a Creative Commons licence, so you need to give credit to their author.

### Attribution legal basis

The requirement for appropriate attribution is found in the [Creative Commons licence](https://creativecommons.org/licenses/by-sa/2.0/). Later versions of the licence have more relaxed requirements.

### Attribution examples

The correct attribution format for Creative Commons images is described [in this handy guide](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License).

### Images checklist

- [ ] Only use images that are in the public domain, or that you own the rights to.
- [ ] Attribute the Creative Commons images with [the correct format](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License).

## Sponsored content and affiliate links

The *Telemediengestz* says that ads on a website must be clearly labelled. You can't disguise an ad as genuine content. Otherwise, it's surreptitious advertising (*Schleichwerbung*), and you can get an *[[Abmahnung]]* for "unfair competition".[^16]

Here are the basic guidelines for ads and sponsored content on your website:

- **Affiliate links need to be labelled**  
    Affiliate links are "commercial communications" according to [§ 6 DDG](https://www.buzer.de/6_DDG.htm). Multiple lawyers suggest to mark affiliate links as ads,[^17] even if you are not *directly* getting financial compensation for affiliate content. A footnote regarding affiliate links might be insufficient.[^21]
- **Sponsored content needs to be labelled**  
    If you get paid to put a sponsored post on your blog, you need to clearly tell your users that this post is an ad, and tell them who is sponsoring the ad. In other words, you can't disguise an advertisement as an editorial text.

[According to Kanzlei Plutte](https://www.ra-plutte.de/schleichwerbung-sponsored-hinweis-reicht-nicht-aus/), "sponsored content" is not a sufficient label, and you should use a clear word like "advertisement" to label advertising on your website. He backs his opinion with court cases, but admits that Twitter, Facebook and Instagram use the term "sponsored".

### Who needs to mark affiliate links?

Any German resident or company who uses affiliate links, sponsored content or ads on their website.

### Legal basis

According to [§ 6 DDG](https://www.buzer.de/6_DDG.htm), "commercial communications must be clearly recognizable as such."

### Sponsored link examples

Google [marks sponsored search results as ads](/images/google-sponsored-link.png). I disclose affiliate links on this website.

### Sponsored content checklist

- [ ] Clearly mark sponsored content as advertisements
- [ ] Clearly mark affiliate links as advertisements, or at least disclose that the post contains affiliate links

## Income-generating websites

If your website generates income, it's a business. If it's not part of a registered business, you will need to register it with the *Gewerbeamt* and the *[[Finanzamt]]*.

- **If your website qualifies as a [[Gewerbe]], you need a trade licence ([[Gewerbeschein]]).**  
    You must apply for a trade licence at your local *Gewerbeamt*. In Berlin, you can [do it online](/guides/gewerbeschein). If your business generates more than €{{GEWERBESTEUER_FREIBETRAG|cur}} in profit per year, you also need to pay the [trade tax (*Gewerbesteuer*)](/glossary/Gewerbesteuer).[^18] For more information, read my [*Gewerbesteuer* guide](/guides/gewerbesteuer).
- **If your website generates income, you need to register it with the [[Finanzamt]].** You register by [filling the *Fragebogen zur steuerlichen Erfassung*](/guides/fragebogen-zur-steuerlichen-erfassung). You will then receive a tax number (*[[Steuernummer]]*), which you need to put in your website's [[Impressum]].
- **Making money from your website is considered self-employment.**  
    If you are not allowed to be self-employed in Germany, you will also need to [apply for a freelance visa](/guides/freelance-visa). You can get a freelance visa in addition to an existing visa.[^19]

**Related guides:**

- [How to start a business in Germany](/guides/start-a-business-in-germany)
    - [How to apply for a trade licence (*Gewerbeschein*)](/guides/gewerbeschein)
    - [How to register a business with the ](/guides/fragebogen-zur-steuerlichen-erfassung)*[Finanzamt](/guides/fragebogen-zur-steuerlichen-erfassung)*

### Who needs to register a business?

Any German resident or who runs a website as a stand-alone business.

### Examples

Our tax number (*[[Steuernummer]]*) can be found in our [Impressum](/terms).

### Income-generating website checklist

- [ ] Before running a commercial website in Germany, make sure you are allowed to be self-employed in Germany.
- [ ] If your website is a stand-alone business, [apply for a ](/guides/gewerbeschein)*[Gewerbeschein](/guides/gewerbeschein)*.
- [ ] If your website is a stand-alone business, [register it at the ](/guides/fragebogen-zur-steuerlichen-erfassung)*[Finanzamt](/guides/fragebogen-zur-steuerlichen-erfassung)*.
- [ ] When your get your tax number (*[[Steuernummer]]*) from the *[[Finanzamt]]*, add it to your *[[Impressum]]*.

## Need help?

**[Where to ask legal questions ➞](/guides/help#legal-questions)**

[^0]: [gruender.de](https://www.gruender.de/recht/dsgvo-cookie-law/), [cookiebot.com](https://www.cookiebot.com/en/cookie-consent/)
[^1]: [techblog.bozho.net](https://techblog.bozho.net/tracking-cookies-gdpr/)
[^2]: [anbieterkennung.de](http://www.anbieterkennung.de/gesetze.htm)
[^3]: [bmuv.de](https://www.bmuv.de/themen/verbraucherschutz/digitaler-verbraucherschutz/impressumspflicht#c66866)
[^4]: [§ 5 DDG](https://www.buzer.de/5_DDG.htm)
[^5]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html)
[^6]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=in%20der%20regel%20sind%20das%20e-mail-adresse%20und%20telefonnummer%2C)
[^7]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=elektronisch%20als%20auch%20nicht%20elektronisch)
[^8]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=nicht%20ausreichend%20ist%20ein%20postfach)
[^9]: [anbieterkennung.de](http://www.anbieterkennung.de/index.htm), [shopbetreiber-blog.de](https://shopbetreiber-blog.de/2008/10/16/eugh-website-betreiber-muessen-im-impressum-keine-telefonnummer-nennen/)
[^10]: [recht-freundlich.de](https://www.recht-freundlich.de/wettbewerbsrecht/abmahnung-der-portfolio-management-gmbh-wegen-fehlendem-impressum-bei-facebook), [blog.sowhy.de](https://blog.sowhy.de/2014/02/14/abmahneritis-weitere-anwalte-betroffen-abmahnung-zur-ansicht/), [linkedin.com](https://www.linkedin.com/pulse/what-impressum-why-does-facebook-want-one-chris-bangs/), [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html), [e-recht24.de](https://www.e-recht24.de/artikel/datenschutz/209.html#)
[^11]: [kuhlen-berlin.de](https://web.archive.org/web/20211201151350/https://kuhlen-berlin.de/glossar/agb-sprache)
[^12]: [datenschutz.org](https://www.datenschutz.org/datenschutzerklaerung-website/)
[^13]: [gdpr-info.eu](https://gdpr-info.eu/art-13-gdpr/)
[^14]: [lawbster.de](https://www.lawbster.de/wann-muessen-agb-uebersetzt-werden/)
[^15]: [smartlaw.de](https://www.smartlaw.de/rechtsnews/e-commerce/wann-benoetigt-meine-webseite-agb#:~:text=grundsatzlich%20gibt%20es%20keine%20pflicht), [anwalt.de](https://www.anwalt.de/rechtstipps/agb)
[^16]: [ra-plutte.de](https://www.ra-plutte.de/schleichwerbung-sponsored-hinweis-reicht-nicht-aus/)
[^17]: [ra-plutte.de](https://www.ra-plutte.de/schleichwerbung-sponsored-hinweis-reicht-nicht-aus/)
[^18]: [Screenshot](/guides/freiberufler-or-gewerbe)
[^19]: [gesetze-im-internet.de](https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html#p0518)
[^20]: [gdpr-info.eu](https://gdpr-info.eu/art-5-gdpr/)
[^21]: [mynewsdesk.com](https://www.mynewsdesk.com/de/mynewsdesk/blog_posts/werbung-mit-affiliate-links-was-ist-rechtlich-zu-beachten-40948)
[^22]: [Art. 6.1](https://gdpr-info.eu/art-6-gdpr/), [Art. 7.4](https://gdpr-info.eu/art-7-gdpr/)
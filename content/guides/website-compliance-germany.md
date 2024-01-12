---
Title: How to run a website in Germany
Short_title: How to run a website
Description: The laws and regulations you must follow to run a website legally in Germany: the Impressum, analytics, cookie banners, GDPR, etc.
Date_created: 2018-05-07
---

This guide shows you what you must do if you run a website in Germany. It's based on my experience running All About Berlin.

{% include "_blocks/tableOfContents.html" %}

## GDPR/[[DSGVO]] compliance

Since May 2018, all websites that serve [[European Union]] customers must follow the General Data Protection Regulation (GDPR in English, DSGVO in German).

Here are the basic principles of GDPR:

1. **[Only collect the data you really need](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/how-much-data-can-be-collected_en)**  
    Be careful about data you accidentally collect, such as server logs.
2. **[Do not store data for longer than necessary](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/how-long-can-data-be-kept-and-it-necessary-update-it_en)**  
    When you no longer need the data, delete it.[^24]
3. **Do not store personal data without the user's consent.**  
    Get explicit consent from your users before collecting their data. The only exception is for data that's absolutely necessary to make your service work.[^23]
4. **[Be transparent about the data you collect from your users](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/what-information-must-be-given-individuals-whose-data-collected_en).**  
    Disclose the data you collect, why you collect that data, and who you collect that data for. Put this information in your privacy policy (*Datenschutzerklärung*).[^20]
5. **[Only use the data for the purpose it was collected for](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/overview-principles/what-data-can-we-process-and-under-which-conditions_en).**
6. **[Store the data about your users securely](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/overview-principles/what-data-can-we-process-and-under-which-conditions_en).**
7. **[Give your users a way to delete their account and erase their data](https://gdpr-info.eu/art-17-gdpr/)**.  
    They have the [right to be forgotten](https://gdpr-info.eu/issues/right-to-be-forgotten/).

Here are resources that helped us understand and comply with this regulation.

- [GDPR requirements in plain English](https://www.varonis.com/blog/gdpr-requirements-list-in-plain-english)
- [Overview of the General Data Protection Regulation](https://gdpr-info.eu/issues/)
- [The General Data Protection Regulation text in English](https://gdpr-info.eu/)
- [What is personal data?](https://commission.europa.eu/law/law-topic/data-protection/reform/what-personal-data_en)
- [GDPR and cookies](https://www.cookiebot.com/en/gdpr-cookies/)

### Who needs to do this?

All websites that serve people in the [[European Union]], no matter who runs the website or where it is hosted. It applies to personal, non-commercial websites too. See **[Who does the data protection law apply to?](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/application-regulation/who-does-data-protection-law-apply_en)** for more details.

### Legal basis

Read the [General Data Protection Regulation](https://gdpr-info.eu/).

### Examples

All About Berlin does not collect personal data about its visitors (I use [Plausible analytics](https://plausible.io/)). It does not set tracking cookies.

A few forms on the website collect user data, for example to send a message or submit a request. No data is sent without an action from you. The data is deleted from the server as soon as possible.

All of this is explained in the [privacy policy](/terms#privacy-policy).

### To-do list

- Understand the GDPR regulation
- Only collect the data you really need
- Disclose what data you collect about your users
- Set an expiration date for the data you collect about your users
- Allow your users to delete the data you collect on them

## Cookies

If you use cookies on your website, you must follow a few rules:

1. **Don't set tracking cookies without your users' [explicit consent](https://blog.signaturit.com/en/gdpr-explicit-consent-from-your-clients#1).** You can't set tracking cookies before you get permission from your user. This means marketing and tracking cookies must be opt-in. That includes cookies set by Google Analytics. It's not limited to cookies; it also applies to all personal data about your users.
2. **Refusing cookies must be as easy as accepting cookies.**  
    Don't hide the "refuse cookies" button. The "accept" and "refuse" buttons must be equally easy to click. Many websites break this rule.
3. **You can't force your users to accept tracking cookies.** You can't make tracking cookies a condition for using your service. You can't say "by using this website, you agree to accept our cookies". You can't force users to accept tracking cookies in your terms and conditions.[^22]
4. **You must allow users to opt out of tracking cookies.**  
    Users must have a way to opt out of tracking cookies, except for cookies that are needed to make the website work. Google Analytics is not needed to make the website work.
5. **Necessary cookies do not need consent.** You don't need the user's consent to set cookies that contain no [personally identifying information](https://commission.europa.eu/law/law-topic/data-protection/reform/what-personal-data_en), and that are necessary to make the website work. You don't need to allow the users to opt out of these cookies.[^0]
6. **Your privacy policy must clearly explain what cookies you set, and what they are used for.**
7. **Be careful with embedded content.** YouTube videos, Disqus comments, Facebook like buttons and other third-party widgets often set tracking cookies.[^1] Either disable these widgets until you get consent from your users, or don't use them at all.

Here are articles that helped us understand how cookies work with the GDPR:

- [Tracking cookies and GDPR](https://techblog.bozho.net/tracking-cookies-gdpr/)
- [Cookie consent: how do I comply with the GDPR?](https://www.cookiebot.com/en/cookie-consent/)

Tools like [CookieBot](https://www.cookiebot.com/en/cookie-consent/) can help you implement a cookie notice that is GDPR compliant.

### Legal basis

In the [[European Union]], cookies were regulated by the [Cookie Directive](https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ:L:2009:337:0011:0036:En:PDF) and now by the [General Data Protection Regulation (GDPR)](https://gdpr-info.eu/), particularly articles 6 and 7.

### Examples

- [CookieBot](https://www.cookiebot.com/en/cookie-consent/)'s cookie notice lets you choose which cookies you want to allow. Analytics cookies are enabled by default, and marketing cookies are disabled by default. Essential cookies cannot be disabled.
- [Gruender.de](https://www.gruender.de/recht/dsgvo-cookie-law/)'s cookie notice lets you choose which cookies you want to allow, with no pre-selected answer.
- [Piwik Pro](https://piwik.pro/blog/burning-questions-gdpr-answered-part-2-3/)'s cookie notice also lets you choose which cookies you want to allow, with no pre-selected answer.
- Many websites ask for permission before they load content from YouTube, Twitter and other websites.

### To-do list

- If you use cookies, inform your users with a [detailed](https://www.cookiebot.com/en/cookie-consent/) cookie notice.
- Explain how and why you use cookies in your website's privacy policy.
- Require explicit consent from your users before setting tracking cookies, and give them a way to opt out of non-essential cookies.
- Make it easy to refuse cookies.
- Test your website with an ad blocker. Some ad blockers will hide cookie consent notices. This breaks some websites.

## Google Analytics

If you use Google Analytics, you *must* get consent from your visitors. You must not track your users at all before they gave their consent.

### Who needs to do this?

Any EU resident or company who uses Google Analytics on their website.

### Legal basis

The rules regarding the tracking of users are defined by the [DSGVO](https://dsgvo-gesetz.de/).

### To-do list

- Do not track your users until you have their consent.
- Agree to the Google Analytics [Data Processing Terms](https://support.google.com/analytics/answer/3379636?hl=en).
- Configure Google Analytics to anonymize IP addresses.
- Delete the data Google Analytics collected before anonymizing IP addresses.
- Inform your users about Google Analytics cookies in your cookie notice, and in your privacy policy.
- Give your users a way to opt out of Google Analytics cookies.
- [Set the Google Analytics data retention period](https://support.google.com/analytics/answer/7667196?hl=en) to 14 months or less, and enable "Reset on new activity".

## Impressum

The [Impressum](https://en.wikipedia.org/wiki/Impressum) is where you list your contact information. This page is mandatory for all *commercial* websites operated by a German person or organization, even if the website is hosted in another country or has a .com domain.[^2] A personal, non-commercial website does not need an Impressum.[^3] In other words, if you live in Germany and use your website to make money or promote a business, you need an Impressum.

An Impressum must be "easily identifiable, directly accessible and constantly available".[^4] This usually means putting a clearly labelled "Impressum" link at the bottom of every page.

1. **An Impressum must always contain:**
    - The full name of the website owner, or the full name of the company including its legal form.[^5]
        - [SAP's Impressum](https://www.sap.com/germany/about/legal/impressum.html) shows the company's full legal name: SAP Deutschland SE & Co. KG
    - An email address that can be used to reach the company or website owner.[^6] You must be quickly reachable electronically, and non-electronically.[^7]
    - The full address of the company or website owner. You cannot use a PO box.[^8]
    - The telephone number and fax number of the website owner. The European Court of Justice says a phone number is not mandatory if the user has alternative options for rapid contact and direct and efficient communication.[^9]
2. **An Impressum must also contain, if applicable:**
    - Details of any supervisory authority the company is a member of.
        - [The Impressum of the Kottident dental clinic](https://www.kottident.de/impressum.html) includes information about the *Zahnärztekammer Berlin*.
        - [The Impressum of Dr. med. Thomas Raile](https://hausarzt-raile.de/language/en/impress/) includes information about the *Ärztekammer Berlin*.
    - The VAT number (*Umsatzsteuer-Identifikationsnummer*) of the company
        - [BMW's Impressum](https://www.bmw.com/en/footer/imprint.html) includes their VAT number, DE 129273398.
        - [SAP's Impressum](https://www.sap.com/germany/about/legal/impressum.html) includes their VAT number, DE 210157578.
    - The name and address of the company's court of registration and its *[Handelsregisternummer](/guides/handelsregisternummer-germany),* if applicable
        - [BMW's Impressum](https://www.bmw.com/en/footer/imprint.html) includes their entry in Munich's trade register: HRB 42243.
        - [SAP's Impressum](https://www.sap.com/germany/about/legal/impressum.html) includes their entry in Mannheim's trade register: HRB 351694.
    - The names of the managing directors and authorized representatives.
        - [Google's Impressum](https://www.google.de/contact/impressum.html) lists its Chief Executive Officer

It's important to have a complete Impressum. Some lawyers aggressively scrutinise the websites of their clients' competitors, and claim damages when they find a missing or incomplete Impressum.[^10] Website owners even received cease-and-desist letters for not having an Impressum on their Facebook page.

The Impressum must be available in the same languages as your website.[^11]

If you can, [remove your Impressum page from Google search results](https://developers.google.com/search/docs/crawling-indexing/control-what-you-share?hl=en&ref_topic=4598466&visit_id=638146524817495260-4161725088&rd=1). Some lawyers make money by finding invalid Impressum pages. If they find yours, they might send you an *[[Abmahnung]]*.

### Who needs to do this?

Any German resident or company who runs a *commercial* website. It doesn't matter if the website uses a .com domain or is hosted in another country.

**Commercial Facebook, Instagram and social media pages** must also have an Impressum.[^5]

### Legal basis

The rules regarding the Impressum are defined by [§ 5 Telemediengesetz (TMG)](https://www.gesetze-im-internet.de/tmg/__5.html), [§ 55 Rundfunkstaatsvertrag (RStV)](http://www.urheberrecht.org/law/normen/rstv/RStV-13/text/2010_06.php3) and [§ 2 DL-InfoV](https://www.gesetze-im-internet.de/dlinfov/__2.html).

### Examples

- [SAP's Impressum](https://www.sap.com/germany/about/legal/impressum.html)
- [BMW's Impressum](https://www.bmw.com/en/footer/imprint.html)
- [Facebook's Impressum](https://www.facebook.com/terms)
- [Google's Impressum](https://www.google.de/contact/impressum.html), featuring details of the authorized representative
- [A medical clinic's Impressum](https://hausarzt-raile.de/language/en/impress/), featuring details about supervisory authorities

### To-do list

- Read the [Ministry of Justice's Impressum guidelines](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html).
- Add an Impressum to your website with all the required information.
- [Add an Impressum to your Facebook business page](https://www.facebook.com/help/342430852516247), if applicable.
- Make the Impressum clearly visible and directly accessible from every page on your website.
- Remove your Impressum from Google search results.

## Privacy policy (Datenschutzerklärung)

Your website must have a privacy policy where you outline how you collect, process and use data about your users. If you fail to include a privacy policy on your website, you can receive an *[[Abmahnung]]*.[^12]

If you need help with your privacy policy, you can either [hire a lawyer](/guides/english-speaking-lawyers-berlin), or use a [privacy policy generator](https://www.iubenda.com/en/privacy-and-cookie-policy-generator).

### Who needs to do this?

Any German resident or company who runs a website, even for non-commercial purposes.[^12]

### Legal basis

The privacy policy is required by Articles 13 and 14 of the DSGVO.[^13]

### Examples

- [Stripe's privacy policy](https://stripe.com/de/privacy) contains detailed information about how they collect and process data about their users
- [N26's privacy policy](https://docs.n26.com/legal/01+DE/03+Privacy%20Policy/en/01privacy-policy-en.pdf) is a PDF file linked at the bottom of every page on their website
- [All About Berlin's privacy policy](/terms) is on the same page as our Impressum, and is linked at the bottom of every page

### To-do list

- Add a privacy policy to your website

## Terms and conditions

Your website should have a terms and conditions ([[AGB]] or *Allgemeine Geschäftsbedingungen*) page. Usually, it's the page where you say "we are not responsible for the accuracy of our content".

The terms in conditions must be available in the same languages as your website.[^14]

### Who needs to do this?

It is not required unless you have customers, but it's always a good idea.[^15]

### Legal basis

The AGB is required by [§ 312d BGB](https://www.gesetze-im-internet.de/englisch_bgb/englisch_bgb.html#p1086) if you have customers.

### To-do list

- Add a terms and conditions page to your website. There are many AGB generators and templates online. Most of them are in German.

## Creative Commons images

If you use images with a Creative Commons licence, make sure you properly attribute the author. In Germany, using the wrong attribution format can be a costly mistake. [I had to pay hundreds of euros in lawyer fees](https://nicolasbouliane.com/blog/abmahnung-creative-commons) for making that mistake.

Here are the basic guidelines about using Creative Commons images on your website:

1. **Pay attention to the licence for the images you use on your website**. Wikipedia images are not always free to use. Ideally, use public domain images that can be used without restrictions. You can find public domain images on [pxhere.com](https://pxhere.com/).
2. **Understand that "free images" sometimes come with conditions.** Some variants of the Creative Commons licence require attribution to the author, prohibit commercial use, and even prohibit derivative works. See [this overview](https://creativecommons.org/licenses/) for more details.
3. **Use the correct format when giving credit to the author.** Proper credit includes the Title, the Author, the Source and the Licence. See [this guide](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License) for more details.

### Who needs to do this?

Anyone who uses Creative Commons media on their website. Most images that come from Wikipedia are under a Creative Commons licence, so you need to give credit to their author.

### Legal basis

The requirement for appropriate attribution is found in the [Creative Commons licence](https://creativecommons.org/licenses/by-sa/2.0/).

### Examples

The correct attribution format for Creative Commons images is described [in this handy guide](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License).

### To-do list

- Make sure you have the right to use the images on your website.
- Attribute the Creative Commons images you use with [the correct format](https://wiki.creativecommons.org/wiki/Best_practices_for_attribution#Title.2C_Author.2C_Source.2C_License).

## Sponsored content and affiliate links

The *Telemediengestz* says that ads on a website must be clearly labelled. You can't disguise an ad as genuine content. Otherwise, it's surreptitious advertising (*Schleichwerbung*), and you can get an *[[Abmahnung]]* for "unfair competition".[^16]

Here are the basic guidelines for ads and sponsored content on your website:

1. **Affiliate links need to be labelled** Affiliate links are "commercial communications" according to [§ 6 TMG](http://www.gesetze-im-internet.de/tmg/__6.html). Multiple lawyers suggest to mark affiliate links as ads,[^17] even if you are not *directly* getting financial compensation for affiliate content. A footnote regarding affiliate links might be insufficient.[^21]
2. **Sponsored content needs to be labelled** If you get paid to put a sponsored post on your blog, you need to clearly tell your users that this post is an ad, and tell them who is sponsoring the ad. In other words, you can't disguise an advertisement as an editorial text.

[According to Kanzlei Plutte](https://www.ra-plutte.de/schleichwerbung-sponsored-hinweis-reicht-nicht-aus/), "sponsored content" is not a sufficient label, and you should use a clear word like "advertisement" to label advertising on your website. He backs his opinion with court cases, but admits that Twitter, Facebook and Instagram use the term "sponsored".

### Who needs to do this?

Any German resident or company who uses affiliate links, sponsored content or ads on their website.

### Legal basis

According to [§ 6 Telemediengesetz (TMG)](http://www.gesetze-im-internet.de/tmg/__6.html), "commercial communications must be clearly recognizable as such.".

### Examples

Google [marks sponsored search results as ads](/images/google-sponsored-link.png). I disclose affiliate links on this website.

### To-do list

- Clearly mark sponsored content as advertisements
- Clearly mark affiliate links as advertisements, or at least disclose that the post contains affiliate links

## Income-generating websites

If your website generates income, it's a business. If it's not part of a registered business, you will need to register it with the *Gewerbeamt* and the *[[Finanzamt]]*.

- **If your website qualifies as a [[Gewerbe]], you need a trade licence ([[Gewerbeschein]]).**  
    You must apply for a trade licence at your local *Gewerbeamt*. In Berlin, you can [do it online](/guides/gewerbeschein). If your business generates more than {{GEWERBESTEUER_FREIBETRAG|cur}}€ in profit per year, you also need to pay the [trade tax (*Gewerbesteuer*)](/glossary/Gewerbesteuer).[^18] For more information, read my [*Gewerbesteuer* guide](/guides/gewerbesteuer).
- **If your website generates income, you need to register it with the [[Finanzamt]].** You register by [filling the *Fragebogen zur steuerlichen Erfassung*](/guides/fragebogen-zur-steuerlichen-erfassung). You will then receive a tax number (*[[Steuernummer]]*), which you need to put in your website's [[Impressum]].
- **Making money from your website is considered self-employment.**  
    If you are not allowed to be self-employed in Germany, you will also need to [apply for a freelance visa](/guides/freelance-visa). You can get a freelance visa in addition to an existing visa.[^19]

**Related guides:**

- [How to start a business in Germany](/guides/start-a-business-in-germany)
    - [How to apply for a trade licence (*Gewerbeschein*)](/guides/gewerbeschein)
    - [How to register a business with the ](/guides/fragebogen-zur-steuerlichen-erfassung)*[Finanzamt](/guides/fragebogen-zur-steuerlichen-erfassung)*

### Who needs to do this?

Any German resident or who runs a website as a stand-alone business.

### Examples

Our tax number (*[[Steuernummer]]*) can be found in our [Impressum](/terms).

### To-do list

- Before running a commercial website in Germany, make sure you are allowed to freelance in this country.
- If your website is a stand-alone business, [apply for a ](/guides/gewerbeschein)*[Gewerbeschein](/guides/gewerbeschein)*.
- If your website is a stand-alone business, [register it at the ](/guides/fragebogen-zur-steuerlichen-erfassung)*[Finanzamt](/guides/fragebogen-zur-steuerlichen-erfassung)*.
- When your receive your tax number (*[[Steuernummer]]*) from the *[[Finanzamt]]*, add it to your *[[Impressum]]*.

## Need help?

**[Where to ask legal questions ➞](/guides/questions-about-berlin#legal-questions)**

[^0]: [gruender.de](https://www.gruender.de/recht/dsgvo-cookie-law/), [cookiebot.com](https://www.cookiebot.com/en/cookie-consent/)
[^1]: [techblog.bozho.net](https://techblog.bozho.net/tracking-cookies-gdpr/)
[^2]: [anbieterkennung.de](http://www.anbieterkennung.de/gesetze.htm)
[^3]: [rockit-internet.de](https://www.rockit-internet.de/en/what-is-an-impressum/)
[^4]: [gesetze-im-internet.de](https://www.gesetze-im-internet.de/tmg/__5.html)
[^5]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html)
[^6]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=in%20der%20regel%20sind%20das%20e-mail-adresse%20und%20telefonnummer%2C)
[^7]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=elektronisch%20als%20auch%20nicht%20elektronisch)
[^8]: [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html#:~:text=nicht%20ausreichend%20ist%20ein%20postfach)
[^9]: [anbieterkennung.de](http://www.anbieterkennung.de/index.htm), [shopbetreiber-blog.de](https://shopbetreiber-blog.de/2008/10/16/eugh-website-betreiber-muessen-im-impressum-keine-telefonnummer-nennen/)
[^10]: [recht-freundlich.de](https://www.recht-freundlich.de/wettbewerbsrecht/abmahnung-der-portfolio-management-gmbh-wegen-fehlendem-impressum-bei-facebook), [blog.sowhy.de](https://blog.sowhy.de/2014/02/14/abmahneritis-weitere-anwalte-betroffen-abmahnung-zur-ansicht/), [linkedin.com](https://www.linkedin.com/pulse/what-impressum-why-does-facebook-want-one-chris-bangs/), [bmj.de \(archived\)](https://web.archive.org/web/20220425135201/https://www.bmj.de/DE/Verbraucherportal/DigitalesTelekommunikation/Impressumspflicht/Impressumspflicht_node.html)
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
[^23]: [Art. 6.1](https://gdpr-info.eu/art-6-gdpr/)
[^24]: [Art. 5](https://gdpr-info.eu/art-5-gdpr/)
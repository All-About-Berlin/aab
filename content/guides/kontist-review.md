---
Title: My review of Kontist: it's not worth it
Short_title: Review of Kontist
Description: I use Kontist as my business bank since January 2022. All of my business goes through it. This is my honest review of their service.
Date_created: 2023-03-10
---

[Kontist](/out/kontist) is a German bank. They offer a business bank account (*[[Geschäftskonto]]*) for freelancers.

I use Kontist since January 2022. This is my review of Kontist in 2024{{ fail_on('2025-01-01') }}, feature by feature. In my opinion, **there is no good reason to choose Kontist**, and you should look at the [alternatives](#kontist-alternatives).

{% include "_blocks/tableOfContents.html.jinja" %}

![Kontist mobile app and card](/images/kontist-review-proof-of-membership.jpg "Confirmed customer")

## Cost and fees

A Kontist account costs [9€ to 80€ per month](/out/kontist-plans). The other fees are too high:

- 10 free transactions per month, then 0.15€ per transaction (incoming and outgoing).
- 1.7% fee on foreign currency transactions (incoming and outgoing).[^8] For example, if you get 1,000 USD from a client, you pay around 17€ in fees.
- 2€ per ATM withdrawal.

If you get paid in foreign currencies, or have many small transactions, Kontist gets expensive.

They added the transaction fee in October 2022.[^6] Since then, I pay twice as much for the same service. It was a slap in the face, especially when the features I pay for don't work.

[![Kontist invoice with account fees](/images/kontist-account-fees.png "9€ for the account, and 11.68€ in transaction fees.")](/images/kontist-account-fees.png)

### Free account

Kontist has a free account. It's almost useless.

- You only get 10 free transactions per month (incoming and outgoing), then you pay 0.15€ per transaction.[^6]
- It only comes with a virtual Visa card, no physical card.
- No invoicing, no integration with bookkeeping tools, and no MT940 exports (only CSV).
- No automatic bookkeeping.

This means that for almost everyone, the free account is not free. [N26 Business](/out/n26-business) has a better free account.

## Automatic tax deductions

When you are self-employed, you must save some of your income for [income tax](/glossary/Einkommensteuer) and [VAT](/glossary/Umsatzsteuer) payments. It's hard to know how much money you really have. Sometimes, you have 5,000€ in your bank account, but only 1,000€ is really yours. The rest is for the *[[Finanzamt]]*.

Kontist promises to fix this. It automatically saves money for VAT and income tax payments. It shows you how much money is for you, and how much is for the *Finanzamt*. It even categorises your transactions automatically!

[![VAT and tax deductions in the Kontist app](/images/kontist-vat-value.png "I can see how much VAT and income tax I owe on each transaction.")](/images/kontist-vat-value.png)

This is a great feature. It's why I opened a Kontist account. There is only one problem: **it does not work**.

### Automatic VAT

You decide how much [VAT](/glossary/Umsatzsteuer) to set aside for each transaction: 0%, {{ VAT_RATE_REDUCED }}% or {{ VAT_RATE }}%.

Kontist uses AI to guess the correct VAT rate for each transaction. It's wrong more than 30% of the time. Instead of leaving transactions uncategorised, it puts them in the wrong category, with the wrong VAT rate. When you correct the AI, it makes the same mistakes the next month. It does not learn.

Since I have to double-check every transaction, the AI just creates more work for me. There is no way to turn it off.

Like other banks, Kontist integrates with [Lexoffice](/out/lexoffice), where I do all of my bookkeeping. All of my transactions are categorised in Lexoffice already. They already have the right VAT. Kontist sees this information, and still sets the VAT wrong. The Kontist support confirmed this.

**The automatic VAT feature is useless.** It does not work, but it can't be turned off.

[![Screenshot of Kontist app: setting the VAT on a transaction](/images/kontist-sort-transactions.png "You must set the VAT on each transaction. The AI does it automatically, but it's often wrong")](/images/kontist-sort-transactions.png)

### Automatic income tax

Kontist also sets some of your income aside for [income tax](/glossary/Einkommensteuer).

This time, there is no AI magic. You manually set your income tax rate, and Kontist takes that amount out of every transaction.

**[Calculate your income tax rate ➞](/tools/tax-calculator)**

When you pay your income tax, you can't reset how much income tax you owe. Kontist can keep too much money aside. You can't do anything about it.

Kontist does not understand [trade tax](/glossary/Gewerbesteuer). This makes the income tax calculation even less precise.

In the end, this feature is too crude to help.

## Invoicing and bookkeeping

### Invoicing tool

You can create invoices in Kontist, but Kontist does not send them for you. You must download them and email them manually.

If you don't send many invoices, the invoicing tool is good enough. If you plan to grow your business, get real invoicing software. I use [Lexoffice](/out/lexoffice).

When your client pays an invoice you created in Kontist, Kontist marks the invoice as paid. This is a nice feature.

### Reports

You can see how much you have, and how much you owe the *[[Finanzamt]]*. That's all.

You can't see how much you made last month, or last year. If your income varies a lot, this information is really important. Most accounting software shows you this. [Holvi](/out/holvi) is a business bank that shows this information. [Lexoffice](/out/lexoffice)'s reports are much better.

### Exporting your data

You can export your transactions as CSV or MT940. This lets you import them into your accounting software.

There is no way to export all transactions *and* attached invoices. You must ask their customer support.

Kontist makes it too hard to reliably export your data. If you want to use other accounting tools, it's a problem. Kontist should not hold your data hostage.

### Integration with other services

Kontist only syncs with [Lexoffice](/out/lexoffice) and [FastBill](https://www.fastbill.com/). It does not integrate with any English-speaking tax software.

You can match Kontist bank transactions to receipts and invoices in Lexoffice. Most other banks also sync with Lexoffice, so this is nothing special.

**One time, some transactions did not sync.** One time, a client paid me. I could see the transaction in Kontist, but not in Lexoffice. All other transactions were there. I manually marked the invoice as paid.

A few months later, the missing transaction appeared in Lexoffice. There were a dozen more transactions, all of them very late. If this happened a little later, my [tax declaration](/glossary/Steuererkl%C3%A4rung) would have been wrong, and I could have been fined by the *Finanzamt*. This is really bad!

Kontist also syncs in the other direction. You can do your bookkeeping in Lexoffice, and see the changes in Kontist. This is sometimes buggy, and transactions do not sync properly.

In other cases, a transaction type exists in Lexoffice, but not in Kontist. A [trade tax](/glossary/Gewerbesteuer) payment can appear as an expense, and it makes the income tax calculation completely wrong. In other words, **syncing from Lexoffice to Kontist does not work**.

### Tax advisor access

Your tax advisor needs to access your invoices and expenses to prepare your [income tax](/glossary/Steuererklärung) and [VAT](/glossary/Umsatzsteuererklärung) declarations.

Your tax advisor can't access your Kontist account. Other business banks like [Qonto](/out/qonto) and [Holvi](/out/holvi) make it possible. Almost all bookkeeping software does. Instead, you must export MT940 data and send it to them manually, every month.

## Web app and mobile app

The website and mobile app are very reliable. I never had problems with them.

### Everything is in English

The website, the app and the customer support are in English. You don't need to speak German to use Kontist.

[N26 Business](/out/n26-business), [Holvi](/out/holvi) and [Qonto](/out/qonto) also speak English.

### SMS confirmation codes

Kontist uses its mobile app for two-factor authentication. If you log in on the web app, you must confirm it in the mobile app. It works reliably.

When you transfer money or change your card PIN, Kontist sends a confirmation code by SMS. SMS activation codes are not secure,[^9] and it's also hard to receive SMS messages when you travel.[^0]

## Sending and receiving money

### Reliable payments

All my business transactions go through my Kontist account. Bank transfers and card payments always worked reliably. I used my Kontist Visa card in Europe and Asia. It always worked well.

### You can't deposit cash

You can't deposit cash into your Kontist account.[^4] It's simply impossible. You must [transfer money](/glossary/SEPA-%C3%9Cberweisung) from another bank account.

This is rarely a problem, except when you open an account. When you open a Kontist account, you must transfer 9€ from another bank to pay for the monthly fee.

## Customer service

Kontist has phone, email and chat support. Some banks only have email or chat support.

They usually answer in 1 business day. They give complete and helpful answers, and they speak English.

## Opening an account

I opened my Kontist account in 10 minutes: 5 minutes to create the account, and 5 minutes to verify my identity. You can do it in English or in German, but the terms and conditions are only in German.

You only need a phone and an ID document. You don't need a registered address (*[[Anmeldung]]*). Kontist uses IDNow to verify your ID.[^2] Some passports are not supported by IDNow. Other online banks have the same problem.

Only freelancers, [small businesses](/glossary/Kleinunternehmer) and sole traders can open an account. Corporations and partnerships (GmbH, KG, UG, or GbR) are not allowed.[^5]

## Conclusion

**I don't recommend Kontist.** There is no reason to choose them over another business bank. The fees are too high, and the promised features are not good enough. I just don't understand what I'm paying for when other banks have more features for a lower price.

Kontist was supposed to make my bookkeeping easier, but **it makes too many errors**, so I can't trust it.

### The good

- Banking works reliably
- The web app and mobile apps are reliable
- The Kontist Duo plan with Lexoffice is a good deal
- The invoicing tool is basic, but good enough for some people

### The bad

- Transaction fees are too high
- The free account is not really free for most people
- Auto-categorization does not work. The AI keeps making mistakes
- Synchronisation issues with Lexoffice
- The income tax estimation is not precise enough to be useful
- The invoicing tool is very basic

### Don't trust what you read

Bloggers get paid to promote Kontist.[^7] When you open an account, they get around 50€. If they tell you that Kontist is bad, they make less money. They don't know if Kontist is good or bad, because they don't use it.

Read [reviews from real users](https://www.trustpilot.com/review/kontist.com) instead, and decide for yourself.

## Kontist alternatives

If you need a business bank account to [start a business in Germany](/guides/start-a-business-in-germany), there are many other options.

Your bank, your accounting software and your tax advisor should be 3 different services. You can't find one business that does 3 things well. You should find 3 businesses that do one thing well.

**[English-speaking tax advisors in Berlin ➞](/guides/english-speaking-steuerberater-berlin)**

**[German tax software for businesses ➞](/guides/german-tax-software)**

### Other business banks

- **[N26 Business](/out/n26-business)**  
    Exactly like N26 personal accounts, but for businesses. I am with N26 since 2016, and [I like it](/guides/an-honest-review-of-n26). There is no automatic accounting, but you can put money aside in "spaces". You can't have a personal N26 account *and* an N26 Business account.
- **[Holvi](/out/holvi)**  
    Very similar to Kontist. They have better invoicing and better reports. Your tax advisor can access your account and export transactions.
- **[Qonto](/out/qonto)**  
    Similar to Kontist. Corporations and partnerships can also open an account.
- **[bunq Business](/out/bunq-business)**  
    Exactly like bunq personal accounts, but for businesses. They speak English.
- **[Revolut Business](/out/revolut-business)**  
    Exactly like Revolut personal accounts, but for businesses. They speak English.
- **[Finom](/out/finom)**  
    English-speaking business bank.
- **[Fyrst](/out/fyrst)**  
    German-speaking business bank.
- **Traditional banks**  
    [Deutsche Bank](/out/deutsche-bank-business), [Commerzbank](/out/commerzbank-business) and other German banks offer business accounts. They might not speak English.

[^0]: [trustpilot.com](https://www.trustpilot.com/reviews/62eaa6ab8000af4a8853a456)
[^2]: [intercom.help](https://intercom.help/kontist/en/articles/1559626-do-i-need-to-have-german-citizenship-to-open-a-kontist-account)
[^4]: [intercom.help](https://intercom.help/kontist/de/articles/1559937-kann-ich-bareinzahlungen-auf-mein-kontist-konto-vornehmen)
[^5]: [intercom.help](https://intercom.help/kontist/en/articles/1559494-can-i-open-a-kontist-account-for-gmbh-kg-ug-gbr)
[^6]: 0.15€ plus VAT. [mobiflip.de](https://www.mobiflip.de/shortnews/kontist-dreht-an-der-preisschraube/)
[^7]: [kontist.com](https://kontist.com/product/partner/)
[^8]: [kontist.com](https://kontist.com/en/pricing/)
[^9]: [securityboulevard.com](https://securityboulevard.com/2021/12/why-using-sms-authentication-for-2fa-is-not-secure/)
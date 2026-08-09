"""
Populate the Misago forum with credible test data.

Creates 25 users and 20 threads about immigration topics covered on
All About Berlin, each with 1-25 replies. Idempotent: existing users
and threads with the same title are skipped.

Run from the host:
    docker compose exec -T forum python manage.py shell < forum/populate_test_data.py
Or:
    mise forum:populate-test-data
"""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from misago.categories.models import Category
from misago.threads.checksums import update_post_checksum
from misago.threads.models import Post, Thread
from misago.users.models import Rank

User = get_user_model()

PASSWORD = "password"

AVATARS = [
    {"size": 400, "url": "http://dummyimage.com/400/400"},
    {"size": 200, "url": "http://dummyimage.com/200/200"},
    {"size": 100, "url": "http://dummyimage.com/100/100"},
]

USERS = [
    ("amelia_r", "amelia.r@example.com"),
    ("julienp", "julien.p@example.com"),
    ("rohan_g", "rohan.g@example.com"),
    ("mira_k", "mira.k@example.com"),
    ("lucas_bt", "lucas.bt@example.com"),
    ("sofia_a", "sofia.a@example.com"),
    ("dario_r", "dario.r@example.com"),
    ("nadia_z", "nadia.z@example.com"),
    ("tomek_w", "tomek.w@example.com"),
    ("hannah_l", "hannah.l@example.com"),
    ("ruben_c", "ruben.c@example.com"),
    ("anastasia_p", "anastasia.p@example.com"),
    ("felix_m", "felix.m@example.com"),
    ("yara_e", "yara.e@example.com"),
    ("omar_h", "omar.h@example.com"),
    ("clara_j", "clara.j@example.com"),
    ("daniela_o", "daniela.o@example.com"),
    ("paul_s", "paul.s@example.com"),
    ("mei_c", "mei.c@example.com"),
    ("mikael_j", "mikael.j@example.com"),
    ("rachel_v", "rachel.v@example.com"),
    ("luca_ferrari", "luca.ferrari@example.com"),
    ("leyla_d", "leyla.d@example.com"),
    ("jonas_ek", "jonas.ek@example.com"),
    ("beatriz_s", "beatriz.s@example.com"),
]

THREADS = [
    {
        "title": "How long is the Anmeldung wait in Berlin right now?",
        "starter": "amelia_r",
        "body": (
            "Just moved to Kreuzberg last week and I've been refreshing the Bürgeramt "
            "booking page for days. Nothing available anywhere in the city until late "
            "November. My employer needs the Meldebescheinigung before payroll can "
            "process me. Is anyone else in this hole right now, and what worked for you?"
        ),
        "replies": [
            (
                "julienp",
                "Totally normal, sadly. New slots open at 06:00, 12:00 and 18:00 every day — set an alarm and refresh. I finally caught a Neukölln one after four days of that.",
            ),
            (
                "rohan_g",
                "You don't have to book in your own district. Did mine in Marzahn last year — one longer S-Bahn ride, but they had appointments the following week.",
            ),
            (
                "mira_k",
                "Rathaus Charlottenburg sometimes releases Saturday slots at the end of the month. Worth checking on the 30th/31st around 09:00.",
            ),
            (
                "lucas_bt",
                "My HR started payroll based on the appointment confirmation email — I only handed in the actual Meldebescheinigung when I had it. Might be worth asking yours.",
            ),
            (
                "sofia_a",
                'There\'s a Chrome extension that pings you when a slot opens (search "Bürgeramt Termin"). Feels dystopian but saved me hours of refreshing.',
            ),
            (
                "amelia_r",
                "Grabbed a Pankow slot for next Tuesday using the 06:00 trick. Thanks all — updating in case anyone else finds this thread.",
            ),
        ],
    },
    {
        "title": "Wohnungsgeberbestätigung — main tenant won't sign",
        "starter": "dario_r",
        "body": (
            "I signed a WG contract in Friedrichshain but my Hauptmieter refuses to "
            "sign the Wohnungsgeberbestätigung. He says he doesn't want it \"on the "
            'books." Is this even legal? I need to register within 14 days and my '
            "Anmeldung appointment is in 9."
        ),
        "replies": [
            (
                "clara_j",
                "It's not optional for him — landlords and main tenants are legally required to sign within two weeks of your move-in. He can be fined €1000+. If he won't budge, you can report it to your Bürgeramt and they'll pursue him, but that will burn the flat.",
            ),
            (
                "nadia_z",
                "Depending on the arrangement he may not even be allowed to sublet. If he's afraid of the Vermieter finding out through this form, that's his problem, not yours. Move out and find a legal WG — this will bite you later.",
            ),
            (
                "daniela_o",
                "If you can't fix it before the appointment, at least bring the WG contract and any proof you're actually living there (bills, deliveries, key handover). The Bürgeramt can sometimes register you and follow up on the Wohnungsgeber separately.",
            ),
            (
                "paul_s",
                "I had a similar situation, ended up moving. The problem wasn't just the Anmeldung — I also couldn't get a proper Steuerklasse sorted, health insurance registration was a pain, and my Freelance visa application later ran into questions about where I actually lived.",
            ),
            (
                "dario_r",
                'Confronted him with the €1000 fine info and he suddenly "found time" to sign it. Appointment is Thursday. Still looking for a new place though — this isn\'t going to work long-term.',
            ),
        ],
    },
    {
        "title": "Freelance visa renewal — how many letters of intent?",
        "starter": "felix_m",
        "body": (
            "Renewing my Freiberufler visa in three months and my Ausländerbehörde "
            "caseworker said last time to bring at least three letters of intent from "
            "clients. Is that still the going number? My contract list has changed a "
            "lot since my first application so I'm nervous about the paperwork."
        ),
        "replies": [
            (
                "rachel_v",
                "Three is fine but I brought five for my second renewal and the officer thanked me for making her job easier. They mostly want to see you have ongoing income prospects, so recent invoices are just as important.",
            ),
            (
                "yara_e",
                "My caseworker in Friedrichshain didn't even count them — she wanted one from each of my main clients confirming continued collaboration. Two letters covering ~80% of income was enough.",
            ),
            (
                "omar_h",
                'More important than the count: make sure they\'re on client letterhead, dated within the last month, and mention roughly how much they intend to pay you. Generic "we will continue working with X" letters got mine sent back for clarification.',
            ),
            ("felix_m", "Good to know. Do the letters need to be in German?"),
            (
                "omar_h",
                "English is fine for freelance visas as far as I know. Only official documents (Steuerbescheid, insurance letters) need to be German or translated.",
            ),
            (
                "luca_ferrari",
                "My caseworker took English letters no problem. What tripped me up was proving I actually had money coming in — bring bank statements showing the last 6 months of income from those clients, not just their letters.",
            ),
            (
                "nadia_z",
                "Also make sure your Bescheinigung in Steuersachen is fresh. Mine was 8 months old and they asked for a newer one, which delayed the whole thing by three weeks.",
            ),
            (
                "felix_m",
                "Thanks everyone. Going to aim for 4 letters + fresh bank statements + updated Bescheinigung. Will update after the appointment.",
            ),
        ],
    },
    {
        "title": "Blue Card to permanent residence at 21 months — realistic?",
        "starter": "mei_c",
        "body": (
            "I've been on a Blue Card for 21 months with a B1 certificate and continuous "
            "pension contributions. Officially it's 21 months with B1 or 33 months "
            "without. Has anyone actually applied at exactly 21 and gotten the "
            "Niederlassungserlaubnis without pushback?"
        ),
        "replies": [
            (
                "ruben_c",
                "Yes, applied at 22 months. They wanted the B1 (Goethe or telc), 21 months of pension slips, my last three Lohnabrechnungen, and proof of adequate housing. Approved in the appointment.",
            ),
            (
                "anastasia_p",
                "Same experience. Bring EVERYTHING — I brought too many documents rather than too few and my caseworker actually seemed relieved. The 21-month rule is real and they know it.",
            ),
            (
                "mikael_j",
                "Watch the pension contribution requirement carefully. If you had any months where you weren't employed (or your employer messed up the payments), that can reset the clock. I got tripped up on a two-week gap between jobs.",
            ),
            (
                "mei_c",
                "Good point on the pension gap — I did switch jobs but there was no gap in employment. Should I bring the Rentenversicherung summary showing full months?",
            ),
            (
                "mikael_j",
                'Yes, request a "Versicherungsverlauf" from Deutsche Rentenversicherung. It\'s free and shows every contribution month by month. Bring it to the appointment.',
            ),
            (
                "clara_j",
                "Also bring evidence you have German language on your side beyond the certificate if you can — I brought a letter from my employer confirming I use German at work. Not required but it helped when the officer was clearly on the fence.",
            ),
            (
                "omar_h",
                "One thing worth mentioning: some Ausländerbehörden are stricter than others about the 21 vs 33 month rule. Berlin Mitte was fine with 21 in my case, but I know someone in Bavaria who got pushed to 33.",
            ),
            (
                "yara_e",
                "Also: your salary needs to still be above the Blue Card threshold at time of application. Mine dropped slightly (moved to a shorter workweek) and they asked me to explain in writing.",
            ),
            (
                "rachel_v",
                "Just to confirm the housing requirement — they want a rental contract in your name showing at least ~12 m² per person. If you're in a WG with a signed WG contract it should be fine, but bring the contract.",
            ),
            (
                "mei_c",
                "Thanks all. Booked for next month. Bringing: passport, current Aufenthaltstitel, Blue Card, all Lohnabrechnungen, Versicherungsverlauf, B1 certificate, rental contract, latest Meldebescheinigung, employer letter, and biometric photo. Will report back.",
            ),
            ("ruben_c", "That's the full list — you're set. Good luck!"),
        ],
    },
    {
        "title": "Fiktionsbescheinigung expires before my Ausländerbehörde appointment",
        "starter": "leyla_d",
        "body": (
            "Applied to renew my residence permit before it expired (August). Got a "
            "Fiktionsbescheinigung valid until end of October. My actual appointment "
            "is November 12. So my Fiktion will be expired for almost two weeks before "
            "the new permit is issued. Can I still legally work? Travel?"
        ),
        "replies": [
            (
                "ruben_c",
                "The Fiktion covers the gap while your application is being processed, but if it expires you're in a gray zone. Call the Ausländerbehörde and ask them to extend it — they can, and they usually will if the delay is on their side.",
            ),
            (
                "jonas_ek",
                "Same happened to me. I emailed the caseworker directly and they extended the Fiktion by 3 months. Took a week to get the new one via post.",
            ),
            ("leyla_d", "Do you know if I can travel to another Schengen country in the meantime?"),
            (
                "ruben_c",
                "On a Fiktionsbescheinigung: only if it explicitly says \"Erwerbstätigkeit gestattet\" AND permits Schengen travel. Check yours. If it's the type where only the German residence is deemed to continue, you technically can't leave and re-enter Germany.",
            ),
            (
                "beatriz_s",
                "Also worth knowing: with the Fiktion expired but appointment booked, you have proof the delay is on the authorities' side. Some employers accept this, but airlines and border officers don't care about your booking confirmation.",
            ),
            (
                "mira_k",
                "Push for the extension in writing. My caseworker was reachable only by email and it took two reminders, but I got the Fiktion extended before it lapsed.",
            ),
            (
                "leyla_d",
                "Called this morning — they'll issue an extended Fiktion valid to end of December. Should arrive by post next week. Massive relief. Thanks all.",
            ),
        ],
    },
    {
        "title": "Tax ID never arrived after Anmeldung — who to contact?",
        "starter": "tomek_w",
        "body": (
            "Did my Anmeldung 7 weeks ago and the Steuer-ID letter never came. Employer "
            "needs it, currently on the emergency tax class. Who do I contact?"
        ),
        "replies": [
            (
                "hannah_l",
                "Bundeszentralamt für Steuern (BZSt). Fill out the form on their website to request a re-send. Takes ~4 weeks by post.",
            ),
            (
                "daniela_o",
                "You can also walk into your local Finanzamt with your Meldebescheinigung and ID, they'll look it up for you on the spot. Faster than waiting for BZSt.",
            ),
            (
                "tomek_w",
                "Finanzamt worked — walked in yesterday, got my Steuer-ID on a printout in 20 minutes. Employer already updated payroll. Thanks!",
            ),
            ("hannah_l", "Good to know Finanzamt still does this. I'll remember it for next time."),
        ],
    },
    {
        "title": "Public vs private health insurance for freelancers — what's the actual catch?",
        "starter": "julienp",
        "body": (
            "31, freelance software developer, currently on TK (public). Broker keeps "
            "pushing private and the numbers look appealing — €280/mo vs €760 on TK. "
            "What's the actual catch that isn't obvious from the sales pitch?"
        ),
        "replies": [
            (
                "ruben_c",
                "The catch is age 50. Private premiums scale with age and health once you're in, and there's basically no path back to public unless you're employed under the JAEG limit for over a year. I stayed public specifically for this reason.",
            ),
            (
                "anastasia_p",
                "I switched to private at 28 and my premium is now (35) around €480. Still cheaper than TK, but the growth curve is real. If you plan to have kids: private insures each child separately at extra cost, public covers dependents for free.",
            ),
            (
                "felix_m",
                "The other thing brokers don't emphasize: reimbursement. Private is Kostenerstattung — you pay the doctor, submit for reimbursement. Some private plans reimburse based on the GOÄ rates and doctors can bill 2.3x-3.5x, which is fully reimbursed only on the better plans. Read the small print on multiplier caps.",
            ),
            ("julienp", "Hadn't heard of the multiplier thing. Any recommended plans?"),
            (
                "felix_m",
                "Depends on what you want. Ottonova and Hallesche are frequently recommended for freelancers because they're more transparent. Barmenia's cheap ones have real gaps. Don't just pick on price.",
            ),
            (
                "omar_h",
                "Do NOT let the broker be your only source of info. Brokers earn commission on private policies (up to 10 monthly premiums). Get a second opinion from an actual Versicherungsberater — they charge a fee, no commission.",
            ),
            (
                "yara_e",
                "If you have any pre-existing conditions, private will either exclude them or price them into your premium. Public just takes you. This alone made the decision for me.",
            ),
            (
                "rachel_v",
                "Also worth considering: the public plans have a €600ish minimum for freelancers, but you can add Krankengeld (sick pay) as a rider on TK for about €30/mo. Private plans require you to buy sick pay separately and it's more expensive if bought late.",
            ),
            (
                "mei_c",
                "I've been private for 6 years. My monthly went from €390 to €510 in that time. Doctors treat me faster and better, which is real, but the cost trajectory scares me.",
            ),
            (
                "clara_j",
                "The big point people miss: in retirement, private premiums stay high while public premiums drop (based on pension income). Many retirees on private go broke from premiums.",
            ),
            (
                "ruben_c",
                "^ this. There's a Basistarif cap for private in retirement but it's still much more than what public retirees pay. Look up \"PKV im Alter\" horror stories before you switch.",
            ),
            (
                "daniela_o",
                "Counterpoint: if you're a high-earner freelancer and stay one, private can save you tens of thousands. Just go in eyes open.",
            ),
            (
                "mira_k",
                'Compromise option: stay on TK but consider a Zusatzversicherung (private supplement) for things like dental, single-room hospital stays, alternative medicine. Costs €20-40/mo and gives you the "private feel" for specific services without leaving the public system.',
            ),
            (
                "julienp",
                "Really useful, thanks all. I think I'll stay on TK and add a dental Zusatz. The one-way-door aspect is what tips it for me. Especially with wanting kids in the next few years.",
            ),
            (
                "rachel_v",
                "Good call. You can always switch later if your situation is very stable and you're confident.",
            ),
            ("omar_h", "Also good decision-making — don't let a broker rush you. It's a big decision."),
            ("julienp", "Marking this resolved. This forum's worth its weight already."),
        ],
    },
    {
        "title": "Family reunification for non-EU spouse — realistic timeline?",
        "starter": "rohan_g",
        "body": (
            "My wife (Indian passport) is applying for a family reunification visa at "
            "the German embassy in Delhi. I'm here on a Blue Card. Anyone gone through "
            "this recently — realistic timeline from appointment to visa in hand?"
        ),
        "replies": [
            (
                "mikael_j",
                "We did it in 2024, Delhi embassy. Appointment booking took 3 months, visa issued 6 weeks after appointment. Total ~4.5 months from starting to visa in her passport.",
            ),
            ("rohan_g", "3 months just to get the appointment?"),
            (
                "mikael_j",
                "Yep. Delhi is one of the slowest. Some people fly to embassies in nearby countries (Kathmandu, Colombo) — check if she's eligible.",
            ),
            (
                "anastasia_p",
                "Make sure your wife has her A1 German cert BEFORE the appointment. Missing this is the #1 reason applications get delayed. Goethe or telc — but not any random school.",
            ),
            (
                "rohan_g",
                "She has A1 already (Goethe). Also has our marriage certificate translated and apostilled. What about proof of income — is my Lohnabrechnung enough or do I need a Steuerbescheid too?",
            ),
            (
                "mikael_j",
                "Bring both. Also bring your rental contract to show you have adequate housing, and a letter from your employer confirming ongoing employment. Overkill is your friend.",
            ),
            (
                "beatriz_s",
                "One nasty detail: the Ausländerbehörde on your side (in Berlin) may pre-approve the application — this can shave weeks off if you request it. Ask them.",
            ),
            ("rohan_g", "Didn't know that! Will look into pre-approval."),
            (
                "omar_h",
                'The pre-approval is called "Vorabzustimmung." Not all offices do it and it\'s discretionary, but if they say yes it really helps. Good luck!',
            ),
        ],
    },
    {
        "title": "Chancenkarte holders — is it actually working out?",
        "starter": "sofia_a",
        "body": (
            "I got the Chancenkarte back in April and moved to Berlin in June. Being "
            "honest, finding a real job here in tech has been way harder than the news "
            "articles made it sound. Anyone else on the Chancenkarte willing to share "
            "how it's actually going?"
        ),
        "replies": [
            (
                "rohan_g",
                "I've heard mixed things. The card is easy to get if you meet the points, but the job market didn't magically open up. Companies still prefer people they can hire without visa paperwork.",
            ),
            (
                "sofia_a",
                "Yeah I'm getting a lot of \"we love your profile but we don't sponsor\" replies, even from companies that supposedly do sponsor.",
            ),
            (
                "luca_ferrari",
                "Chancenkarte doesn't require sponsorship for most jobs — it lets you work part-time (20h) while you look for full-time. Recruiters often don't know this. Might be worth flagging in your outreach.",
            ),
            (
                "amelia_r",
                "Same experience. What worked for me: I sent a short line about the Chancenkarte in my applications explaining that no sponsorship is needed. Started getting more responses.",
            ),
            (
                "daniela_o",
                'Do you have a Steuer-ID and Anmeldung sorted? I found that "yes I\'m already in Berlin, registered, ready to start" makes a bigger difference than any visa detail.',
            ),
            (
                "sofia_a",
                "All set on that front. I'm mostly worried about the 12-month clock ticking. Any experience extending or converting?",
            ),
            (
                "mira_k",
                "You can convert to a proper work permit (Aufenthaltserlaubnis §18) as soon as you have a job offer that qualifies. Don't wait — book an Ausländerbehörde appointment as soon as you sign.",
            ),
            (
                "clara_j",
                "One thing that's rarely mentioned: the part-time work allowance is genuinely useful. Even a €15-20/hour part-time job buys you time and puts German work experience on your CV.",
            ),
            (
                "mikael_j",
                "I know two Chancenkarte holders who got jobs within 4 months and two who left after 10. Berlin tech is not what it was 3 years ago. Would you consider Munich or Stuttgart?",
            ),
            ("sofia_a", "Not really. Berlin's the reason I came here specifically."),
            (
                "yara_e",
                "Then keep at it, network aggressively (meetups, Betahaus, xHain), and take a part-time role to keep the visa clock manageable. It works out for most people I know who stuck with it.",
            ),
            ("sofia_a", "Thanks all — good perspective. Doing a part-time application push this week."),
        ],
    },
    {
        "title": "KSK application — how long did yours take?",
        "starter": "yara_e",
        "body": (
            "Freelance illustrator. Submitted my KSK application in July with all "
            "documents (contracts, invoices, samples). It's now November and I haven't "
            "heard a peep. Is this normal, or do I need to nudge them?"
        ),
        "replies": [
            ("felix_m", "Totally normal. Mine took 8 months in 2024. They batch through applications in waves."),
            (
                "rachel_v",
                "You can call them but they'll say \"still in queue.\" Faster to just wait. Once accepted they backdate to your application date so you don't lose money.",
            ),
            (
                "luca_ferrari",
                "Backdating is key. Save 25% of income aside for the eventual retroactive contributions bill.",
            ),
            (
                "mira_k",
                "My acceptance letter came at month 11 with a €4,200 retroactive contribution bill. Painful but expected. They'll let you pay in installments if you ask.",
            ),
            (
                "yara_e",
                'Good tip on the installments. Any advice on writing the "artist statement" bit if they ask for clarification later?',
            ),
            (
                "felix_m",
                "Keep it plain — describe what you do, who your clients are, what percentage of your income is artistic. They're looking for clear evidence you're a working artist, not academic prose. If they need more they'll ask a specific question.",
            ),
        ],
    },
    {
        "title": "Ausländerbehörde only writes to me in German",
        "starter": "nadia_z",
        "body": (
            "I keep getting German-only letters from the Ausländerbehörde and I'm A1 "
            "at best. Is this legal? Do they have to communicate in English if I ask?"
        ),
        "replies": [
            (
                "clara_j",
                "Legal, yes — German is the official language of German authorities. They can (and usually do) refuse to communicate in English. Use DeepL or ChatGPT to translate, and if it's important, pay a translator or bring a German-speaking friend to the appointment.",
            ),
            (
                "omar_h",
                "You can bring your own interpreter to appointments (friend, colleague — doesn't have to be certified for most things). For letters, most caseworkers will informally answer basic questions in English if you email them politely.",
            ),
            (
                "nadia_z",
                "OK — will just accept it as part of life here. Learning German is on my list, this is more motivation.",
            ),
        ],
    },
    {
        "title": "Losing my job while on Blue Card — what's the actual grace period?",
        "starter": "lucas_bt",
        "body": (
            "Just got laid off from my Blue Card job (11 months in). I know I have a "
            "grace period to find a new job — but how long exactly, and what do I need "
            "to actually do to preserve my status?"
        ),
        "replies": [
            (
                "ruben_c",
                "Standard grace period is 3 months from termination date. You need to notify the Ausländerbehörde immediately in writing (email is fine as long as it's documented), and start job hunting.",
            ),
            ("lucas_bt", "Do I keep working rights during those 3 months?"),
            (
                "ruben_c",
                "Yes. Your Blue Card is still valid, you can register with the Agentur für Arbeit for unemployment if you paid in long enough, and you can take any new job (not just Blue Card qualifying) during the search period.",
            ),
            (
                "anastasia_p",
                "If you find a new Blue Card qualifying role within 3 months, no transition paperwork needed — just update the Ausländerbehörde with the new contract. If you find a non-qualifying role, you'll need to switch to a different residence permit type.",
            ),
            ("lucas_bt", "I've paid in 11 months. Can I actually get unemployment benefits?"),
            (
                "mikael_j",
                "To qualify for ALG I you need 12 months of contributions in the last 30 months. You're just under. But register anyway — you get healthcare coverage during the search, and the time counts toward future eligibility.",
            ),
            (
                "daniela_o",
                "Also: register within 3 days of receiving the termination notice, or you can be penalized. Do it now if you haven't.",
            ),
            ("lucas_bt", "Already registered this morning. First appointment next week."),
            (
                "clara_j",
                "Something else important: if you don't find a job in 3 months, you can request an extension in some cases — especially if you can show active job search (CV, applications, interviews). Keep records.",
            ),
            (
                "omar_h",
                "Also make sure to keep paying your health insurance if not on unemployment. TK has an unemployed rate that's much lower than the freelance rate. Don't just stop paying.",
            ),
            (
                "lucas_bt",
                "I'm still on the company plan through end of month. Then unemployment should take over the insurance side, right?",
            ),
            (
                "mikael_j",
                "Right — if you register with the Agentur für Arbeit and get ALG I, they'll pay your health insurance. If you don't qualify for ALG I but register as job-seeking, TK can put you on the Arbeitsuchend rate which is very low.",
            ),
            ("rachel_v", "You've got this. 3 months is real time, especially in tech. What's your role and stack?"),
            (
                "lucas_bt",
                "Backend engineer, Python/Go, 6 years experience. Sending applications this week. Thanks all — this thread has been more useful than a lawyer.",
            ),
        ],
    },
    {
        "title": "Job Seeker visa — how much money do I need to show?",
        "starter": "paul_s",
        "body": (
            "Applying for the Job Seeker visa at the German consulate. The requirement "
            'says "sufficient means of subsistence." Any recent applicants know what '
            "that actually means in euros? Different sources say wildly different numbers."
        ),
        "replies": [
            (
                "luca_ferrari",
                "They typically want to see ~€1,100/month for 6 months, so around €6,600 in a blocked account (Sperrkonto) or on your Kontoauszug.",
            ),
            (
                "ruben_c",
                "The blocked account is usually the safer route — Fintiba and Expatrio are the most-used providers. Consulate sometimes accepts a regular bank statement but it's discretionary.",
            ),
            ("paul_s", "Between the two — Fintiba vs Expatrio — any preference?"),
            (
                "luca_ferrari",
                "Both fine. Fintiba is faster to open, Expatrio has slightly better refund terms if you cancel. I used Fintiba in 2024, zero issues.",
            ),
            (
                "omar_h",
                "The €1,100 figure is the government minimum but I'd budget higher — Berlin rent alone can be €800-1200. Show €10K if you can. Consulate officers appreciate obvious readiness.",
            ),
        ],
    },
    {
        "title": "Freiberufler or Gewerbe for a software consultant?",
        "starter": "mikael_j",
        "body": (
            "Software consultant here, mostly integration work for enterprise clients "
            '— technical but not always "creative." Freiberufler or Gewerbe? Getting '
            "different answers from different sources."
        ),
        "replies": [
            (
                "felix_m",
                "Freiberufler if the work is primarily intellectual/consulting. Building custom code = usually Freiberufler. Selling packaged software = Gewerbe. Grey area, but consulting typically falls on the Freiberufler side.",
            ),
            (
                "rachel_v",
                "The Finanzamt gets the final say. Register as Freiberufler with a description that emphasizes the consulting/architecture nature of your work, and they'll either accept it or reclassify you.",
            ),
            ("mikael_j", "What are the actual practical differences?"),
            (
                "rachel_v",
                "Freiberufler: no Gewerbesteuer, no IHK membership, no double-entry bookkeeping required. Gewerbe: pay Gewerbesteuer above ~€24,500 profit, mandatory IHK membership (~€100-500/yr), Bilanz required above certain thresholds.",
            ),
            (
                "daniela_o",
                "Also VAT is different — Freiberufler and Gewerbe both charge VAT (unless Kleinunternehmer), but the tax administration treats you differently in edge cases.",
            ),
            (
                "ruben_c",
                'My Steuerberater said any modern software work that involves "consulting" the client on architecture, integration, or strategy is Freiberufler. Just building to a spec = Gewerbe. Your description matters more than the actual work sometimes.',
            ),
            (
                "anastasia_p",
                'Concrete tip: on the Fragebogen zur steuerlichen Erfassung (Elster form), describe your work as "Beratung und Konzeption im Bereich Softwareentwicklung" rather than "Softwareentwicklung." That framing tends to land as Freiberufler.',
            ),
            ("mikael_j", "Thanks — that specific wording is gold."),
            (
                "omar_h",
                'If they reclassify you to Gewerbe, you can appeal. It\'s called "Einspruch" — you have one month from the decision. Was successful for a friend who framed his work more clearly on appeal.',
            ),
            (
                "clara_j",
                "One question that helps: does your work require a specific technical/professional expertise that a random person couldn't do? If yes = Freiberufler. Software architecture, consulting, engineering = yes.",
            ),
            (
                "luca_ferrari",
                'I got classified as Freiberufler for similar work. What tipped it: my client contracts described "advisory services" not "software delivery."',
            ),
            (
                "yara_e",
                "There's a Katalogberuf list in the tax code — engineers, architects, doctors, journalists, teachers, artists, etc. If you can plausibly fit into \"engineer\" you're much safer as Freiberufler.",
            ),
            (
                "nadia_z",
                "The other side: Gewerbe isn't the end of the world. Below €24,500 profit there's no Gewerbesteuer anyway, and IHK fees below certain thresholds are minimal. Don't panic if you end up there.",
            ),
            (
                "mira_k",
                "Also: Freiberufler visa applications look at your professional qualifications more than Gewerbe visa applications. If you're on a freelance visa, being classified as Freiberufler makes visa renewals cleaner.",
            ),
            (
                "mikael_j",
                "Good point — I'm on a Freiberufler visa specifically. So getting the tax classification to match is important.",
            ),
            (
                "felix_m",
                "Definitely. If Finanzamt classifies you as Gewerbe but your visa says Freiberufler, you have a real problem at renewal time.",
            ),
            (
                "rachel_v",
                "Two smaller tips: keep a copy of all client contracts and how you described the work on each. And find a Steuerberater who's dealt with software freelancers — general Steuerberater may not understand the distinction well.",
            ),
            ("mikael_j", "Any Steuerberater recommendations for English-speaking software freelancers in Berlin?"),
            (
                "rachel_v",
                "There's a thread about that here somewhere. Search \"English-speaking Steuerberater\" — a few good ones came up. Wundertax and Sorted have also been mentioned but they're software-only, not full Steuerberater.",
            ),
        ],
    },
    {
        "title": "Elster activation code — is 3 weeks normal?",
        "starter": "hannah_l",
        "body": (
            "Trying to set up Mein Elster to submit my Fragebogen zur steuerlichen "
            "Erfassung. I requested the activation code by post 3 weeks ago and it "
            "still hasn't arrived. Is this normal?"
        ),
        "replies": [
            (
                "felix_m",
                "Two things arrive separately — one is your Aktivierungs-ID by email, the other is the Aktivierungscode by post. Sometimes weeks apart. Check your Briefkasten today, they often come in the same week.",
            ),
            ("hannah_l", "Only got the letter (with the code). Never got the ID email?"),
            ("felix_m", "Check spam. Elster emails come from a weird address and get caught constantly."),
            ("hannah_l", "Found it in spam! Working now. Thanks!"),
        ],
    },
    {
        "title": "Making friends in Berlin as a newcomer — what actually works?",
        "starter": "beatriz_s",
        "body": (
            "Been here 4 months. Work from home, my German is basic, and I know exactly "
            "two people (both from work). Feeling isolated. What actually works for "
            "meeting people here as an adult who doesn't want to just party?"
        ),
        "replies": [
            (
                "lucas_bt",
                "Meetup.com is unironically the answer. Search your interests (running, chess, board games, hiking) and just show up. First few times are awkward — then you're in.",
            ),
            (
                "amelia_r",
                "Second Meetup. Also: language exchange groups (Tandem, official ones at Volkshochschulen). Even if you don't need the language practice, they're low-pressure and full of people also looking for friends.",
            ),
            (
                "rachel_v",
                'Sports clubs. Joining a running/climbing/cycling group with regular sessions builds friendships way faster than "casual" meetups because you keep seeing the same people.',
            ),
            (
                "luca_ferrari",
                "Berlin is huge and famously cold. It genuinely takes time. Don't take it personally that the first few months feel hollow — this is normal here.",
            ),
            (
                "omar_h",
                'The advice I got that helped: don\'t try to "make friends," try to have a hobby. Friends come as a byproduct of showing up to things you actually care about.',
            ),
            (
                "mira_k",
                "I do a monthly potluck with 5 friends we all met at a German course. If you're taking classes, invite the two people you like most to something. Someone has to start.",
            ),
            (
                "clara_j",
                "Related: don't over-index on other expats. Some of my best Berlin friendships are with locals I met at Kiezinitiativen (neighborhood associations) and a Berlin Bewegt sports group.",
            ),
            (
                "mikael_j",
                "I joined a Kleingartenverein and met the most eclectic mix of Berliners I've encountered. Waitlist is long but if you have any interest in gardening, put your name down now.",
            ),
            (
                "daniela_o",
                "Bumble BFF actually works here. Sounds cringey but I met two great friends through it in my first year.",
            ),
            (
                "sofia_a",
                "Ask your two work friends to introduce you to their friends. This sounds obvious but a lot of newcomers don't do it. \"Any chance I can join next time you're doing X?\" — it works.",
            ),
            (
                "ruben_c",
                "Volunteering. Refugee support, local food distribution, animal shelters. The vibe is different from other social spaces and the people you meet tend to stick around.",
            ),
            (
                "anastasia_p",
                "Sauna culture — book a slot at a Bezirksbad sauna and just be a regular. Berliners are surprisingly chatty in saunas.",
            ),
            (
                "felix_m",
                'German course is still #1 for me. Everyone in the class is in the exact same "new here" situation.',
            ),
            (
                "yara_e",
                "Church, Buddhist meditation groups, yoga studios with community events — depends on your spiritual leanings, but any recurring gathering is fertile ground.",
            ),
            (
                "beatriz_s",
                "Some really specific ideas here, thanks. Kleingartenverein and Kiezinitiative I hadn't thought of.",
            ),
            (
                "paul_s",
                "Also: get a dog. Instant conversations with other dog owners, and same routes every day means you see the same people.",
            ),
            (
                "leyla_d",
                "Third the German course. I made 3 close friends in my B1 class two years ago, still meet regularly.",
            ),
            (
                "mira_k",
                "If you're into books: Do You Read Me?! and Modern Graphics host reading events. Small, quiet, and people actually chat.",
            ),
            (
                "omar_h",
                "Berlin has a very high hobbyist scene: Betahaus, xHain (hackerspace), Fahrradkueche, various cooking swap groups. Google your specific interest + Berlin.",
            ),
            (
                "rachel_v",
                "One more: Duolingo events in Berlin can be a good starting point for language + people, even if the app itself is limited.",
            ),
            (
                "beatriz_s",
                "Signed up for a Volkshochschule German course starting January and a Meetup running group for next week. Baby steps.",
            ),
            ("lucas_bt", "That's the right move. Give it 6 months and you'll be the one giving advice on this thread."),
            ("amelia_r", "100%. Good luck!"),
        ],
    },
    {
        "title": "B1 German for permanent residence — how strict is Berlin?",
        "starter": "julienp",
        "body": (
            "Getting close to eligibility for Niederlassungserlaubnis. My German is "
            "conversational but I never took a formal B1 exam. How strictly is the "
            "Ausländerbehörde actually enforcing the language requirement in Berlin?"
        ),
        "replies": [
            (
                "ruben_c",
                'Very strictly for permanent residence. You need a formal certificate (Goethe, telc, ÖSD are all accepted). "Conversational" doesn\'t count.',
            ),
            (
                "clara_j",
                "The telc B1 is the easiest and most widely offered. Sign up 2-3 months in advance because slots fill up.",
            ),
            (
                "felix_m",
                "I did telc B1 last year — it's actually pretty gentle if you're conversational. Reading and writing are the hard parts if you've mostly learned through speaking.",
            ),
            ("julienp", "What's the writing test look like?"),
            (
                "felix_m",
                "A short email or letter (~80 words) plus reading comprehension. If you can write a coherent apology email in German you're fine.",
            ),
            (
                "omar_h",
                "Goethe B1 is considered slightly harder than telc. Companies and universities tend to trust Goethe more but for immigration purposes both are 100% equivalent.",
            ),
            (
                "rachel_v",
                'DTZ ("Deutsch-Test für Zuwanderer") is another option, sometimes offered by integration courses. Also accepted.',
            ),
            (
                "anastasia_p",
                "If you did an integration course after arrival, the B1 exam at the end often counts. Check whether your certificate is still valid.",
            ),
            (
                "mikael_j",
                "Study tip: the exam is very format-specific. Buy a \"telc B1 Prüfungstraining\" book, do 3-4 mock exams, and you'll be fine even if your German isn't perfect.",
            ),
            (
                "daniela_o",
                "I passed telc B1 with 62%. Conversational tone gets you the speaking and listening; you can bomb writing and still pass. Don't stress.",
            ),
            (
                "yara_e",
                "If you fail — which does happen with people who overestimate their level — you can retake individual parts (not the whole exam). Good to know.",
            ),
            (
                "luca_ferrari",
                "A word of warning: some Ausländerbehörden have started rejecting certificates older than 5 years. Check the date on yours before the appointment.",
            ),
            ("julienp", "Mine will be fresh (~1 year old) by then. Good to know for the future."),
            (
                "nadia_z",
                "What about lower-level German plus a language exception — I've heard of people getting through with less than B1 based on integration or hardship?",
            ),
            (
                "ruben_c",
                "Exceptions exist but are rare and require specific circumstances (age, disability, hardship). \"I've been here 5 years and never had time to learn\" doesn't count.",
            ),
            (
                "clara_j",
                "For Blue Card holders specifically: 21 months = B1 required, 33 months = A1 required. So you can trade time for less language.",
            ),
            (
                "mira_k",
                "True. If you're on Blue Card and B1 is a heavy lift, waiting another year for the 33-month rule might be easier than cramming for the exam.",
            ),
            (
                "julienp",
                "I'm on Blue Card, coming up on 24 months. I think I'd rather do the B1 than wait another 9 months.",
            ),
            (
                "felix_m",
                "Then start the telc B1 exam prep now. 4-6 weeks of focused study is plenty for a conversational speaker.",
            ),
            ("rachel_v", "DVV Volkshochschule offers exam prep courses if you want structure. Cheap and effective."),
            ("sofia_a", "Superprof or italki for a private tutor if you want 1:1 practice on speaking. €20-30/hr."),
            (
                "omar_h",
                "For anyone lurking: don't overthink B1. It's genuinely a B1 (intermediate) exam, not a fluency test. If you can order food, apologize for a mistake, and describe your last vacation, you're in the range.",
            ),
            ("julienp", "This is really encouraging. Booking a telc B1 for February."),
            ("ruben_c", "Best of luck! Report back when you pass."),
            (
                "daniela_o",
                "Also: bring your original certificate to the appointment. They don't accept photocopies without the original for verification.",
            ),
        ],
    },
    {
        "title": "English-speaking Steuerberater for freelance IT contractor?",
        "starter": "tomek_w",
        "body": (
            "Looking for an English-speaking Steuerberater in Berlin who handles "
            "freelance IT contractors. Bonus points if familiar with double-taxation "
            "for people who spent part of the year abroad. Any recommendations?"
        ),
        "replies": [
            (
                "luca_ferrari",
                'There\'s a good list on the All About Berlin site under "English-speaking Steuerberater Berlin." I use one from there — Trilingua (they also speak French). Solid for IT freelancers.',
            ),
            ("tomek_w", "Perfect, will check them out."),
        ],
    },
    {
        "title": "Immigration lawyer for a Widerspruch — complex case",
        "starter": "leyla_d",
        "body": (
            "Anyone been through a Widerspruch (appeal) after a residence permit "
            "denial? Looking for lawyer recommendations for a complex case involving "
            "a change of employer during the Fiktion period."
        ),
        "replies": [
            (
                "ruben_c",
                'Sperling & Vollmer in Kreuzberg handle this kind of case. Also see the Ausländerrecht section of the Anwaltverein directory — filter for "Fachanwalt für Migrationsrecht." Only work with a specialist for a Widerspruch; general lawyers will mess it up.',
            ),
        ],
    },
    {
        "title": "Kita spot with a brand new residence permit — is it hopeless?",
        "starter": "rohan_g",
        "body": (
            "Just got my Blue Card, family reunification for wife done, now trying to "
            "find a Kita spot for our 2-year-old. Waiting lists are 12-18 months and "
            "we start needing childcare in 3 months when my wife starts her German "
            "course. Is there any real path to a spot?"
        ),
        "replies": [
            (
                "clara_j",
                "Rechtsanspruch (legal right to a Kita spot) applies from age 1, and if the Jugendamt can't offer you one they can be sued. Some parents actually do this and win. But that's the nuclear option.",
            ),
            (
                "daniela_o",
                'Before that: register with the Kita Navigator system and apply to EVERY Kita within a 45-min commute, not just neighborhood ones. Then physically visit each. Directors often keep an informal "friendly parent" list separate from the waitlist.',
            ),
            (
                "omar_h",
                "Tageseltern (childminders) are a good bridge option. Smaller settings, sometimes shorter waits. The Jugendamt has a list.",
            ),
            (
                "mikael_j",
                "If you can prove economic hardship or that both parents need childcare for work/study, some Bezirks give priority.",
            ),
            (
                "rohan_g",
                'My wife\'s German course is required for her visa — does that count as "needing childcare for study"?',
            ),
            (
                "clara_j",
                "Yes it does. Get a letter from the language school stating the required hours and use it in your Kita applications.",
            ),
            (
                "anastasia_p",
                "We went through this. Applied to 27 Kitas, visited 12, got 2 offers within 6 months. Persistence matters more than luck.",
            ),
            (
                "yara_e",
                "One trick: apply for BILINGUAL Kitas (English-German). They often have shorter waitlists because fewer German families apply, and prioritize non-German-speaking children.",
            ),
            (
                "rachel_v",
                "Berlin International Kita, Kinderclub etc. — more expensive than standard Kita, but you're paying for the reduced wait.",
            ),
            ("rohan_g", "We can pay for private if needed. Any private Kita recommendations?"),
            (
                "luca_ferrari",
                "Klax has multiple locations, good reputation, English-friendly. Also Fröbel operates several bilingual Kitas.",
            ),
            (
                "mira_k",
                "Standard Kita is basically free with the Kitagutschein (voucher). Private Kitas the Gutschein doesn't fully cover so you pay €400-1000+ per month.",
            ),
            (
                "felix_m",
                "Get the Kitagutschein early — you can apply before you have a spot. Some Kitas won't even talk to you without it.",
            ),
            (
                "ruben_c",
                "The Gutschein is issued by the Jugendamt in your Bezirk. Apply as soon as you have Meldebescheinigung, ideally with a letter from the language school stating your wife's schedule.",
            ),
            (
                "daniela_o",
                "Also: some Kitas offer part-time / half-day spots that are easier to get than full-time. Might be a stopgap.",
            ),
            (
                "rohan_g",
                "Really appreciate all this. Sounds like: 1) get the Gutschein now, 2) apply everywhere, 3) look at bilingual/private, 4) consider Tageseltern.",
            ),
            (
                "clara_j",
                "Exactly. And keep the Rechtsanspruch letter in your back pocket. Just knowing it exists gives you standing.",
            ),
            (
                "omar_h",
                'One more: some Berlin Kitas do "kennenlernen" (getting to know) days. Attending these puts you on the director\'s radar way more than a form submission.',
            ),
            (
                "mira_k",
                "Also worth: talking to your wife's language school for their referrals — many schools have partner Kitas or informal networks with English-friendly ones.",
            ),
            (
                "rohan_g",
                "Update after 6 weeks: got the Gutschein, applied to 18 Kitas, visited 6 so far. Two are hopeful for a spring spot. Trying a Tageseltern for the March-May gap. Thanks all for helping me not panic.",
            ),
            ("clara_j", "You're doing everything right. Update again when you land a spot!"),
        ],
    },
]


def get_or_create_user(username, email, rank):
    existing = User.objects.filter(username__iexact=username).first()
    if existing:
        return existing
    return User.objects.create_user(
        username,
        email,
        PASSWORD,
        avatars=list(AVATARS),
        rank=rank,
    )


def make_parsed(text):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def create_post(thread, poster, body, posted_on):
    post = Post.objects.create(
        category=thread.category,
        thread=thread,
        poster=poster,
        poster_name=poster.username,
        original=body,
        parsed=make_parsed(body),
        posted_on=posted_on,
        updated_on=posted_on,
    )
    update_post_checksum(post)
    post.save(update_fields=["checksum"])
    return post


def create_thread(category, spec, users_by_username):
    if Thread.objects.filter(category=category, title=spec["title"]).exists():
        return None

    starter = users_by_username[spec["starter"]]
    start_time = timezone.now() - timedelta(
        days=random.randint(2, 60),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    thread = Thread(
        category=category,
        started_on=start_time,
        starter_name="-",
        starter_slug="-",
        last_post_on=start_time,
        last_poster_name="-",
        last_poster_slug="-",
        replies=0,
    )
    thread.set_title(spec["title"])
    thread.save()

    create_post(thread, starter, spec["body"], start_time)

    current_time = start_time
    for username, body in spec["replies"]:
        current_time += timedelta(minutes=random.randint(20, 20 * 60))
        create_post(thread, users_by_username[username], body, current_time)

    thread.synchronize()
    thread.save()
    return thread


def main():
    random.seed(42)

    category = Category.objects.filter(level=1).order_by("lft").first()
    if category is None:
        raise SystemExit("No public category found — create one in the Misago admin first.")

    default_rank = Rank.objects.order_by("order").first()

    users_by_username = {}
    for username, email in USERS:
        users_by_username[username] = get_or_create_user(username, email, default_rank)

    created_threads = 0
    skipped_threads = 0
    for spec in THREADS:
        thread = create_thread(category, spec, users_by_username)
        if thread is None:
            skipped_threads += 1
        else:
            created_threads += 1

    category.synchronize()
    category.save()

    print(
        f"\nUsers: {len(users_by_username)} total. "
        f"Threads: {created_threads} created, {skipped_threads} skipped (already existed) "
        f"in category '{category.name}'."
    )


main()

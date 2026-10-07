# Hladysh Ivan · AI Automation Engineer

I build systems that take repetitive manual work off people: invoices checked against a cost estimate, competitor prices collected every morning, sales calls scored against a script. Make, n8n, LLM APIs and custom scrapers, wired into the tools a business already uses.

Before automation I spent 10+ years in hospitality, from waiter to running a venue. I look at a process as an operations manager first and as an engineer second.

Kyiv, Ukraine · [Telegram @Ivan_Hladysh](https://t.me/Ivan_Hladysh) · [h2omoby@gmail.com](mailto:h2omoby@gmail.com)

---

## How I build

- **The model reads, code does the math.** LLMs parse documents and classify. Sums, limits, balances and unit conversions run in deterministic logic that gives the same answer twice.
- **Model calls are counted before launch.** One call per document instead of one per line, so processing cost does not grow with document size.
- **Duplicates stop at the door.** A document that was already processed, a post that is already in the table, a button pressed twice: none of them change the data.
- **Failures are loud.** When a source does not respond or a file cannot be parsed, a person gets a clear message and the system retries. No silent gaps.
- **A human stays where judgment is needed.** Disputed items and content drafts go to a person with approve and reject buttons. Everything between those points is automated.
- **Built to be handed over.** Access, documentation and a description of the logic stay with the client.

---

## Case studies

Each page covers who it is for, the problem, what was built and the key decision.

**🧾 [Procurement control against the cost estimate](cases/01-procurement-control.md)**<br>
`Construction` · n8n, Claude API, Telegram Bot API, Google Sheets, Google Drive<br>
The cost estimate and purchase documents arrive in Telegram. The system registers the project, reads each document, checks every line against the estimate on 4 levels and returns a decision with buttons to the manager.

**🏭 [Content pipeline for a Telegram channel](cases/02-telegram-content-factory.md)**<br>
`Content` · n8n, Apify, OpenAI, Telegram Bot API, Google Sheets<br>
The system watches source channels, collects posts with metrics, rewrites the selected ones in the brand voice and sends a draft with media for approval.

**💬 [Instagram comment analytics](cases/03-instagram-comments-analytics.md)**<br>
`Marketing` · Make, Apify, OpenAI, Google Sheets<br>
Three scenarios on one sheet: collect new comments, label sentiment, extract questions and suggestions, build regular and monthly reports.

**🏠 [Telegram rental aggregator](cases/04-rental-aggregator.md)**<br>
`Real estate` · Apify, Node.js, OpenAI, Make, Telegram Bot API<br>
A plain-language request is parsed into 23 search parameters, and listings from rental platforms arrive without duplicates.

**🎙️ [Voice bot for bar inventory](cases/05-bar-inventory-voice-bot.md)**<br>
`HoReCa` · Make, Whisper, OpenAI, Google Sheets<br>
The bartender dictates stock by voice, the system matches items, subtracts bottle weight and writes to the sheet.

**📊 [Competitor price monitoring](cases/06-competitor-price-monitoring.md)**<br>
`Retail / e-commerce` · Make, Google Sheets<br>
Daily collection of competitor listings, matching against the client's price list, report in a sheet.

**📞 [Sales call analytics](cases/07-sales-calls-analytics.md)**<br>
`Sales` · IP telephony, Whisper<br>
Transcription, scoring against the sales script, an alert to the manager on a negative call and a follow-up task.

**🧵 [Threads autoposting](cases/08-threads-autoposting.md)**<br>
`Content` · Threads API, Google Sheets<br>
Scheduled publishing from a sheet, duplicate filtering, the post id written back. The access token refreshes itself.

**🗄️ [Natural-language analytics over MS SQL Server](cases/09-nl-analytics-mssql.md)**<br>
`Retail / e-commerce` · MS SQL Server<br>
A manager asks in a plain sentence and gets the number. 100+ metrics, integrated with CRM and BAS.

**📅 [Booking bot for several specialists](cases/10-booking-bot.md)**<br>
`Services` · Make, Telegram Bot API<br>
A Telegram bot with a separate calendar per specialist, free slots calculated in code, automatic reminders.

---

## Stack

| | |
| --- | --- |
| **Orchestration** | Make, n8n, Google Apps Script |
| **AI** | LLMs via API, document and speech recognition |
| **Code** | Python, JavaScript, Node.js, written with Claude Code. I read, debug and fix it myself |
| **Data and scraping** | Apify with custom actors, REST APIs, webhooks, OAuth, MS SQL Server |
| **Integrations** | Telegram and WhatsApp Bot API, IP telephony, Google Sheets, Drive and Calendar, Threads Graph API, Meta Marketing API, Manychat, GoHighLevel, Retell AI, CRM, BAS and ERP |

---

## Contact

- **Telegram:** [@Ivan_Hladysh](https://t.me/Ivan_Hladysh)
- **Email:** [h2omoby@gmail.com](mailto:h2omoby@gmail.com)

Tell me in one sentence which process still runs by hand, and I will tell you whether it is worth automating.

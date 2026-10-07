# 🧾 Procurement control against the cost estimate

`Construction` · n8n, Claude API, Telegram Bot API, Google Sheets, Google Drive

> **Who it is for.** Construction companies and contractors where invoices and receipts are checked against the cost estimate by hand, and money leaves faster than control can keep up.

## Problem

A manager checks each supplier invoice against the estimate manually. An extra item, an inflated price, an exceeded quantity or a substituted material surfaces a month later, when the payment has already gone through. Every new project has a different estimate, so control starts from zero each time.

## What I built

One Telegram bot that receives both the cost estimate and every purchase document. The system registers the project, reads the document, checks every line against the estimate and returns a ready decision for each row to the manager.

## How it works

### 1. A new project is connected with one file

- The estimate is sent to Telegram as an Excel file, exactly as the estimating software exported it.
- The system parses it, takes the materials section and creates a separate project spreadsheet from a template.
- After parsing it reconciles the sum of items with the section total and checks the numbering for gaps. If something does not add up, it says so immediately.
- The project goes into the registry and becomes active: all following documents are booked to it.

### 2. Purchase document

- Accepts a PDF or a photo: invoice, delivery note, sales receipt, fuel station receipt.
- Extracts the supplier, number, date and every line with quantity and price excluding VAT.
- Checks whether this document was already processed. A duplicate stops right there.
- The original is archived under a readable name: date, type, number, supplier.

### 3. Four control levels per line

1. Is this material in the estimate or in the list of approved substitutes.
2. Does the purpose match: grade, class, area of use.
3. Is the quantity within the limit, counting what was already purchased.
4. Is the price within the 5% tolerance over the estimate price.

### 4. Manager decision

- Each line gets one of four statuses: pass, awaiting confirmation, manual review, block. Next to it is the reason in numbers: how much is needed, what is left, by what percent the price is higher.
- The manager sees a summary of the document in Telegram with links to the original and the project spreadsheet.
- Disputed lines arrive as a separate message with buttons. One tap, and the decision is logged with name and time, and the quantity is booked or not.

## What makes it work on real documents

- **Units of measure.** The invoice is in bags, the estimate in tonnes. Cylinders in pieces, the estimate in litres. The system converts and then validates the result against the estimate price. A typical order-of-magnitude error is corrected automatically and flagged in the log.
- **A substitutes list that grows on its own.** When the manager confirms a material substitution, it is remembered. Next time the same item passes without a question.
- **A decision is made once.** Pressing the button again changes nothing.
- **The system does not stay silent when something goes wrong.** If a document could not be processed or the estimate was read only partially, a person gets a clear message.

> 🔑 **Key decision.** Code counts the money, not the language model. The model reads the document and suggests which estimate item a line corresponds to. Limits, balances, unit conversion and price tolerance are calculated by deterministic logic. A model that adds up sums on its own will sooner or later get one wrong, and it will be the client's money.

## Scale

- One n8n workflow, four branches: new estimate, purchase document, help, decision buttons.
- Only two model calls in the whole scenario: one per estimate, one per document. All lines of a document are matched in a single call, so processing cost does not grow with the number of rows.
- A separate spreadsheet per project: estimate, cumulative ledger, invoice log, substitutes. Plus a shared project registry.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

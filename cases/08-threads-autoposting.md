# 🧵 Threads autoposting

`Content` · Threads API, Google Sheets

> **Who it is for.** Businesses and professionals who have a content plan but a person publishes it.

## Problem

The content plan sits in a spreadsheet, and someone opens the phone at nine every morning and copies the text by hand. One missed day and the plan slips.

## What I built

The spreadsheet stays the single source of truth. Publishing runs on a schedule, duplicates are cut off by a composite filter, and the id of the published post is written back to the sheet.

> 🔑 **The detail that usually gets missed.** A Threads access token lives for 60 days. The system refreshes it on its own, so it does not break two months after handover.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

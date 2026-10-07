# 🎙️ Voice bot for bar inventory

`HoReCa` · Make, Whisper, OpenAI, Google Sheets

> **Who it is for.** Bars and restaurants where inventory is done with a notepad and typed into a spreadsheet after the shift.

## Problem

A bar inventory means hundreds of items, weighing bottles and entering numbers by hand. It is slow, with mistakes in names and in weight conversion.

## What I built

Stock is dictated by voice. Whisper transcribes, the model matches what was said to the product list, bottle weight is subtracted by calculation, and the result lands in Google Sheets.

> 🔑 **Key decision.** Fuzzy name matching against a map of 277 SKUs: the bartender speaks the way they are used to, and the correct item ends up in the sheet.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

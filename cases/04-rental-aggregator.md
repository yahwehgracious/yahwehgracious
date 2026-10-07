# 🏠 Telegram rental aggregator

`Real estate` · Apify, Node.js, OpenAI, Make, Telegram Bot API

> **Who it is for.** People looking for a rental who do not want to check several sites by hand every day.

## Problem

Listings are scattered across platforms, each has its own filters, and the same apartment shows up several times.

## What I built

The user writes a request in a plain sentence. The model parses it into 23 structured parameters, custom Apify actors in Node.js collect listings from rental platforms, Make orchestrates the flow, and duplicates are cut off through a Data Store.

> 🔑 **Key decision.** Custom actors instead of off-the-shelf ones. The platforms have non-obvious API behaviour (categories, operation types, photo formats, city filter) that ready-made solutions do not cover.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

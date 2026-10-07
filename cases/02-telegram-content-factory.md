# 🏭 Content pipeline for a Telegram channel

`Content` · n8n, Apify, OpenAI, Telegram Bot API, Google Sheets

> **Who it is for.** Telegram channel owners and content teams who look for topics in other channels every day and rewrite them by hand.

## Problem

To keep a channel publishing regularly, someone scrolls through channels in the niche every day, picks the posts that performed, rewrites them in the channel's voice and looks for an image or a video. It is daily manual work, and it depends on one person.

## What I built

The system watches the sources, shows which posts performed best and prepares a draft in the channel's style. A person only chooses what to take and approves the result.

## How it works

### 1. Source monitoring

- The list of source channels lives in settings and can be changed without touching the workflow.
- The system pulls fresh posts with text, media, views and reactions.
- New posts are added to the sheet, known ones get their metrics updated.
- For each post it calculates the ratio of views to reactions, to show what actually resonated.

### 2. Draft generation

- Posts selected in the sheet are rewritten in the channel's style. The style is stored in settings and changed in one place.
- Media from the original is attached automatically: video, photo or text only.
- The draft arrives in Telegram exactly as it will look in the channel.

### 3. Approval

- Two buttons under each draft: generate another version or publish.
- All drafts are stored on a separate sheet together with the original and the source.
- A processed post is marked so it does not go into work twice.

## Edge cases covered

- **Duplicates.** A post that is already in the sheet is not added again, only its numbers are updated.
- **Collection failures.** If a source did not respond, a notification goes to Telegram and the system retries in 15 minutes.
- **Empty posts.** Posts without text or without views are filtered out before they reach the sheet.

> 🔑 **Key decision.** A human stays in the process at two points: choosing which posts to take and approving the draft. Everything between those points is done by the system. The channel does not turn into a stream of automatic text with no control.

## Scale

- One n8n workflow, two branches: monitoring and generation.
- Three draft formats: video, photo, text.
- One model call per post.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

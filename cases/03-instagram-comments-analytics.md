# 💬 Instagram comment analytics

`Marketing` · Make, Apify, OpenAI, Google Sheets

> **Who it is for.** Brands and SMM teams with many comments under their posts and nobody reading all of them.

## Problem

Comments are read selectively. Customer questions stay unanswered, negative feedback is noticed late, and nobody can say in numbers what the audience thinks overall.

## What I built

One system of three scenarios working on a shared sheet. The first collects and labels comments, the second and third build reports from them.

## How it works

### 1. Collecting and labelling comments

- The scenario pulls comments under the account's latest posts.
- It compares them with what is already in the sheet and takes only the new ones.
- Each new comment gets a sentiment: positive, negative or neutral.
- If a comment contains a question or a suggestion, they go to separate columns.
- A row is written to the sheet: post, author, text, date, sentiment, question, suggestion.

### 2. Regular report

- Number of comments, how many positive and negative, the ratio in percent.
- The three most frequent audience questions and the full list of questions.
- A short summary: what people praise and what they complain about.
- Distribution of comments by post.

### 3. Monthly report

- Overall audience mood for the month.
- Extended summaries of positive and negative feedback.
- The ten most frequent questions.

> 🔑 **Key decision.** Each comment is labelled once, at collection time. Reports are built from the ready sheet and do not re-read Instagram. So a report is generated quickly, and cost depends on the number of new comments, not on the size of the whole history.

## Scale

- Three Make scenarios, 18 modules in total.
- One spreadsheet with three sheets: comments, daily analytics, monthly report.

---

[All case studies](../README.md#case-studies) · [Telegram](https://t.me/Ivan_Hladysh)

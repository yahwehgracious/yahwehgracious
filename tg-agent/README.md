# ШІ-таргетолог

Персональний таргетолог у Telegram Mini App для власної реклами в Instagram/Facebook.

## Як влаштовано
- **Mini App** (`tg-app/index.html`) говорить із Meta API напряму з телефона: кампанії з різними цілями
  (Direct / лід-форма / Telegram / сайт), групи, бюджети, аудиторія, плейсменти, креативи (4:5 + 9:16),
  A/B/C тексти, редагування запущених оголошень, причини відхилення, звіти з розбивками, заявки з форм,
  клієнти (ручні відмітки + Google Таблиця CSV), ШІ для текстів, розбору креативу й ідей.
  Ключі Meta і ШІ зберігаються лише в Telegram CloudStorage користувача.
- **Щоранку** (`python -m targetolog daily ivan`): витрати, ціна результату, відхилені оголошення й рішення → Telegram.
  Нічого в кабінеті не змінює, рішення підтверджуються в застосунку.
- **Щопонеділка** (`python -m targetolog update ivan --out ../tg-app/index.html --notify`): бібліотека реклами конкурентів
  (власний скрапер Playwright, при збої — останні збережені дані) → скоринг → LLM-розбір із кешем → нові сценарії →
  перебудова застосунку.

Обидва запуски — GitHub Actions (`.github/workflows/targetolog.yml`). Секрети: `META_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`,
`ANTHROPIC_API_KEY` або `GEMINI_API_KEY`.

## Правила рішень (однакові в застосунку й щоранковому звіті)
- Оголошення молодші 72 год не чіпаємо.
- Вимкнути: витрачено ≥ 2 норми без результату, або ≥ 3 результати по ціні > 1,5 норми. Якщо оголошення єдине в групі — пропонуємо заміну, а не вимкнення.
- Частота > 3,2 — пора новий креатив.
- +20% бюджету: ≥ 5 результатів по ціні ≤ норми, не частіше ніж раз на 3 дні.
- Норми в `clients/<slug>/client.json` → `kpi`: `target_cpl` (переписка), `target_lead` (заявка), `target_click` (перехід).

## Локально
```
pip install -r requirements.txt && python -m playwright install chromium
python -m targetolog update ivan --skip-collect
python -m targetolog daily ivan --no-send
python -m unittest discover -s tests
```

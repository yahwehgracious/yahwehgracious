"""Telegram: лише надсилання повідомлень із кнопкою, що відкриває Mini App. Усе керування — в застосунку."""
import html
import os

from .util import http


def esc(s):
    return html.escape(str(s if s is not None else "—"))


def send(chat_id, text, app_url=None, app_text="Відкрити застосунок"):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задано")
    p = {"chat_id": chat_id, "text": text[:4096], "parse_mode": "HTML", "disable_web_page_preview": True}
    if app_url:
        p["reply_markup"] = {"inline_keyboard": [[{"text": app_text, "web_app": {"url": app_url}}]]}
    return http(f"https://api.telegram.org/bot{tok}/sendMessage", p, timeout=30)

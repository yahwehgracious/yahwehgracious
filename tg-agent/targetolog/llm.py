"""LLM-провайдери: anthropic | openai | gemini | mock. Облік токенів і вартості."""
import base64
import os
from collections import Counter

from .util import http, log

PRICES = {  # $ за 1M токенів (in, out) — орієнтир, звір з прайсами провайдерів
    "anthropic": (3.0, 15.0),
    "openai": (2.5, 10.0),
    "gemini": (0.3, 2.5),
}


class LLM:
    def __init__(self, provider, model=None):
        self.provider = provider
        self.model = model or {
            "anthropic": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
            "openai": os.environ.get("OPENAI_MODEL", "gpt-4o"),
            "gemini": os.environ.get("GEMINI_MODEL", "gemini-flash-latest"),
            "mock": "mock",
        }[provider]
        self.tokens = Counter()

    @property
    def cost(self):
        pin, pout = PRICES.get(self.provider, (0, 0))
        return round((self.tokens["in"] * pin + self.tokens["out"] * pout) / 1e6, 4)

    def json(self, system, user, max_tokens=8000, media=None):
        """Гарантований JSON: Anthropic — через forced tool use (модель не може повернути зламаний JSON),
        Gemini — responseMimeType=application/json, інші — парсинг тексту."""
        from .util import parse_json
        if self.provider == "anthropic":
            content = [{"type": "text", "text": user}]
            r = http("https://api.anthropic.com/v1/messages", {
                "model": self.model, "max_tokens": max_tokens, "system": system,
                "tools": [{"name": "result", "description": "Поверни результат",
                           "input_schema": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object"}}},
                                            "required": ["items"]}}],
                "tool_choice": {"type": "auto"},  # forced tool_choice не підтримується новими моделями
                "messages": [{"role": "user", "content": content + [{"type": "text", "text": "Обовʼязково виклич інструмент result і передай масив у полі items. Без тексту поза інструментом."}]}],
            }, {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}, timeout=600)
            self.tokens["in"] += r["usage"]["input_tokens"]
            self.tokens["out"] += r["usage"]["output_tokens"]
            if r.get("stop_reason") == "max_tokens":
                log(f"⚠ {self.model}: обрізано по max_tokens={max_tokens}")
            block = next((b for b in r["content"] if b["type"] == "tool_use"), None)
            if block:
                return block["input"].get("items", [])
            return parse_json("".join(b.get("text", "") for b in r["content"]))  # модель відповіла текстом
        if self.provider == "gemini":
            return parse_json(self(system, user, max_tokens=max_tokens, media=media, json_mode=True))
        return parse_json(self(system, user, max_tokens=max_tokens, media=media))

    def __call__(self, system, user, max_tokens=4000, media=None, json_mode=False):
        """media: [(mime, bytes)] — тільки для gemini/anthropic (зображення)."""
        if self.provider == "anthropic":
            content = []
            for mime, data in media or []:
                if mime.startswith("image/"):
                    content.append({"type": "image", "source": {"type": "base64", "media_type": mime,
                                                                  "data": base64.b64encode(data).decode()}})
            content.append({"type": "text", "text": user})
            r = http("https://api.anthropic.com/v1/messages", {
                "model": self.model, "max_tokens": max_tokens, "system": system,
                "messages": [{"role": "user", "content": content}],
            }, {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}, timeout=300)
            self.tokens["in"] += r["usage"]["input_tokens"]
            self.tokens["out"] += r["usage"]["output_tokens"]
            return "".join(b.get("text", "") for b in r["content"])

        if self.provider == "openai":
            r = http("https://api.openai.com/v1/chat/completions", {
                "model": self.model, "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            }, {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}, timeout=300)
            self.tokens["in"] += r["usage"]["prompt_tokens"]
            self.tokens["out"] += r["usage"]["completion_tokens"]
            return r["choices"][0]["message"]["content"]

        if self.provider == "gemini":
            parts = [{"inline_data": {"mime_type": m, "data": base64.b64encode(d).decode()}} for m, d in media or []]
            parts.append({"text": user})
            r = http(f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
                     f"?key={os.environ['GEMINI_API_KEY']}", {
                         "systemInstruction": {"parts": [{"text": system}]},
                         "contents": [{"role": "user", "parts": parts}],
                         "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.4,
                                              **({"responseMimeType": "application/json"} if json_mode else {})},
                     }, timeout=300)
            u = r.get("usageMetadata", {})
            self.tokens["in"] += u.get("promptTokenCount", 0)
            self.tokens["out"] += u.get("candidatesTokenCount", 0)
            return "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])

        raise ValueError(f"provider {self.provider}")


def make(name, model=None):
    if not name or name == "mock":
        return None
    keyvar = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}[name]
    if not os.environ.get(keyvar):
        log(f"⚠ {keyvar} не задано — {name} вимкнено, працює mock")
        return None
    return LLM(name, model)

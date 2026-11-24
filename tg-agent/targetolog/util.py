import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", file=sys.stderr, flush=True)


def load_env(path=ROOT / ".env"):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class HttpError(RuntimeError):
    def __init__(self, code, url, body):
        super().__init__(f"HTTP {code} {url.split('?')[0]}: {body[:400]}")
        self.code, self.body = code, body


def http(url, payload=None, headers=None, method=None, timeout=120, retries=3, raw=False, form=None):
    """JSON по HTTP з ретраями на 429/5xx. form= — application/x-www-form-urlencoded."""
    hdr = dict(headers or {})
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        hdr.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif payload is not None:
        data = json.dumps(payload).encode()
        hdr.setdefault("Content-Type", "application/json")
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=hdr, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                return body if raw else json.loads(body.decode() or "null")
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            raise HttpError(e.code, url, body) from None
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            raise


def text_hash(text):
    norm = re.sub(r"[^\w]+", " ", (text or "").lower()).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:16]


def ts(v):
    """unix | ISO | None -> aware datetime."""
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc)
    s = str(v)
    if s.isdigit():
        return datetime.fromtimestamp(int(s), tz=timezone.utc)
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_json(text):
    """Дістає JSON з відповіді LLM (з ```json``` або без). При помилці зберігає сиру відповідь у /tmp для дебагу."""
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    t = m.group(1) if m else text
    starts = [i for i in (t.find("{"), t.find("[")) if i >= 0]
    t = t[min(starts):] if starts else t
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        try:
            return json.loads(t, strict=False)  # сирі переноси рядків усередині строк
        except json.JSONDecodeError:
            Path("/tmp/llm_bad.json").write_text(text, encoding="utf-8")
            raise


def now_utc():
    return datetime.now(timezone.utc)

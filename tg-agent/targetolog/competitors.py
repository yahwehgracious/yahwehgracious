"""Конкуренти, яких ти сам додав у застосунку.

Застосунок зберігає їх мітками «ai_comp ig=<username>» / «ai_comp fb=<page_id>» у кабінеті Meta,
бо GitHub не має доступу до Telegram CloudStorage. Тут ми їх читаємо й перетворюємо на запити до бібліотеки реклами:
- fb=<id> — сторінка в бібліотеці реклами напряму (точно);
- ig=<username> — беремо назву акаунта через Instagram Business Discovery і шукаємо оголошення,
  де рекламодавець має ту саму назву (бібліотека реклами не шукає за Instagram)."""
import json
import os
import re
import urllib.parse
from pathlib import Path

from .util import http, log


def norm(s):
    return re.sub(r"[^0-9a-zа-яіїєґ]", "", (s or "").lower())


def _get(path, token, v, **params):
    params["access_token"] = token
    return http(f"https://graph.facebook.com/{v}/{path}?{urllib.parse.urlencode(params)}", timeout=60, retries=1)


def read_labels(cfg):
    token = os.environ.get(cfg["meta"].get("token_env", "META_ACCESS_TOKEN"), "")
    if not token:
        return None
    v, A = cfg["meta"].get("api_version", "v24.0"), f"act_{cfg['meta']['ad_account_id']}"
    try:
        labels = _get(f"{A}/adlabels", token, v, fields="name", limit=200).get("data", [])
    except Exception as e:  # noqa: BLE001
        log(f"⚠ Мітки конкурентів не прочитались: {e}")
        return None
    out = []
    for lab in labels:
        m = re.match(r"^ai_comp (ig|fb)=([^\s|]+)(?:\|ig=(\S+))?$", lab.get("name", ""))
        if m:
            out.append({"kind": m[1], "value": m[2], **({"ig": m[3]} if m[3] else {})})
    return out


def resolve(cfg, items):
    """Кожен конкурент → {label, page_id | term, names} для скрапера й фільтра."""
    token = os.environ.get(cfg["meta"].get("token_env", "META_ACCESS_TOKEN"), "")
    v, ig = cfg["meta"].get("api_version", "v24.0"), (cfg.get("launch") or {}).get("instagram_user_id")
    known = cfg.get("known_pages") or {}
    by_id = {pid: u for u, pid in known.items()}
    out, seen = [], set()
    for it in items:
        pid = it["value"] if it["kind"] == "fb" else known.get(it["value"])
        if pid:  # одна сторінка = один конкурент, навіть якщо в кабінеті лишились мітки і з ніком, і з ID
            if pid in seen:
                continue
            seen.add(pid)
            u = it.get("ig") or (it["value"] if it["kind"] == "ig" else by_id.get(pid))
            out.append({"label": "@" + u if u else pid, "page_id": pid, "names": set()})
            continue
        if it["value"] in seen:
            continue
        seen.add(it["value"])
        u, name = it["value"], None
        if token and ig:
            try:
                bd = _get(ig, token, v, fields=f"business_discovery.username({u}){{username,name}}").get("business_discovery", {})
                name = bd.get("name")
            except Exception as e:  # noqa: BLE001
                log(f"   @{u}: назву не отримав ({str(e)[:120]}), шукаю за ніком")
        names = {norm(x) for x in (u, name) if x and len(norm(x)) >= 3}
        out.append({"label": "@" + u, "term": name or u.replace("_", " ").replace(".", " "), "names": names})
    return out


def keep(ad, comps):
    if any(c.get("page_id") == ad["page_id"] for c in comps):
        return True
    p = norm(ad["page_name"])
    return bool(p) and any(n == p or (len(n) >= 5 and (n in p or p in n)) for c in comps for n in c["names"])


def state_path(cfg):
    return Path(cfg["_dir"]) / "competitors.json"


def save_state(cfg, comps, pages):
    state_path(cfg).write_text(json.dumps({"competitors": [c["label"] for c in comps], "pages": sorted(pages)},
                                          ensure_ascii=False, indent=1), encoding="utf-8")


def load_state(cfg):
    p = state_path(cfg)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

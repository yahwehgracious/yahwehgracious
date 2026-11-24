"""Щотижневе оновлення: конкуренти → скоринг → розбір ШІ → нові ідеї → перебудова Mini App.

Усе про власну рекламу застосунок бере з Meta наживо, тому тут лише те, що потребує сервера:
скрапінг бібліотеки реклами й LLM-розбір із кешем у SQLite."""
import json
import os
from datetime import datetime
from pathlib import Path

from . import analyze as an
from . import brief as br
from . import competitors as cmp
from . import llm, miniapp, scoring, sources, telegram
from .db import DB
from .util import ROOT, log, now_utc

DEFAULTS = {
    "country": "UA",
    "scoring": {"min_days": 14, "days_cap": 90, "top_n": 12, "max_per_page": 3},
    "analysis": {"provider": "anthropic", "video_provider": "gemini", "batch_size": 6, "video": True},
    "brief": {"provider": "anthropic", "concepts": 6, "every_days": 7},
}


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_client(slug):
    d = ROOT / "clients" / slug
    cfg = _merge(DEFAULTS, json.loads((d / "client.json").read_text(encoding="utf-8")))
    cfg["_dir"], cfg["slug"] = str(d), slug
    return cfg, DB(d / "data.sqlite")


_ALIVE = {}


def _pick(pref, heavy=False):
    """Бажаний провайдер; якщо ключа нема або він не відповідає (нема балансу, ліміт) — наступний. None = без LLM."""
    for name in dict.fromkeys([pref, "anthropic", "gemini"]):
        # важке (ідеї/бриф) — Opus, масове (розбір конкурентів) — Sonnet
        model = os.environ.get("ANTHROPIC_MODEL_HEAVY", "claude-opus-5-5") if heavy and name == "anthropic" else None
        m = llm.make(name, model) if name else None
        if not m:
            continue
        if m.model not in _ALIVE:
            try:
                m("Відповідай одним словом.", "ок?", max_tokens=5)
                _ALIVE[m.model if m else name] = None
            except Exception as e:  # noqa: BLE001
                _ALIVE[m.model if m else name] = str(e)[:160]
                log(f"⚠ {name} не відповідає: {_ALIVE[m.model if m else name]}")
        if _ALIVE[m.model if m else name] is None:
            return m
    return None


def _short(err):
    """Людською мовою замість простирадла JSON."""
    e = str(err)
    if "429" in e:
        return "ліміт запитів вичерпано (безкоштовний ключ або квота)"
    if "credit balance" in e or "billing" in e.lower():
        return "нема балансу"
    if "401" in e or "403" in e or "invalid" in e.lower():
        return "ключ не підходить"
    return e[:80]


def run(slug, now=None, force_brief=False, skip_collect=False, out=None, notify=False):
    cfg, db = load_client(slug)
    now = now or now_utc()
    day = now.date().isoformat()
    out_dir = Path(cfg["_dir"]) / "out"
    out_dir.mkdir(exist_ok=True)

    n_ads = None
    manual = cmp.read_labels(cfg)  # None — нема токена Meta (локальні тести): працюємо по-старому
    if manual is not None and not skip_collect:
        comps = cmp.resolve(cfg, manual)
        pages = set()
        if comps:
            c2 = {**cfg, "competitor_page_ids": [c["page_id"] for c in comps if c.get("page_id")],
                  "search_terms": [c["term"] for c in comps if c.get("term")], "source": {**cfg["source"], "fallback": None}}
            try:
                ads, src = sources.collect(c2)
                ads = [a for a in ads if cmp.keep(a, comps)]
                db.upsert_ads(ads, day)
                pages = {a["page_id"] for a in ads}
                n_ads = len(ads)
                log(f"01 Ad Library: {n_ads} оголошень твоїх конкурентів ({', '.join(c['label'] for c in comps)})")
            except Exception as e:  # noqa: BLE001
                log(f"⚠ Бібліотека реклами не відповіла: {e}")
                pages = set((cmp.load_state(cfg) or {}).get("pages", []))
        cmp.save_state(cfg, comps, pages)
    elif manual is None and not skip_collect and cmp.load_state(cfg) is None:
        ads, src = sources.collect(cfg)  # старий режим (без ручного списку й без токена) — лише для локальних тестів
        db.upsert_ads(ads, day)
        n_ads = len(ads)
        log(f"01 Ad Library ({src}): {n_ads} оголошень, знімок {day}")
    state = cmp.load_state(cfg)
    if state is not None:  # ручний режим: лише твої конкуренти, без фільтрів за словами
        cfg["_pages"] = set(state["pages"])
        cfg.pop("relevance_rx", None)
        cfg.pop("exclude_rx", None)
        cfg["scoring"] = {**cfg["scoring"], "min_days": cfg["scoring"].get("manual_min_days", 7), "max_per_page": 5, "top_n": 40}

    winners, stats = scoring.score_creatives(db, now, cfg)
    log(f"02 Скоринг: {stats['creatives']} креативів → {stats['winners']} ≥{cfg['scoring']['min_days']} дн → топ {len(winners)}")

    main_llm = _pick(cfg["analysis"]["provider"])
    video_llm = llm.make(cfg["analysis"].get("video_provider"))
    analyses = an.analyze(db, winners, cfg, main_llm, video_llm)
    pats = an.patterns(winners, analyses, stats["fresh"])

    dead = "; ".join(f"{k}: {_short(v)}" for k, v in _ALIVE.items() if v)
    missing = [k for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY") if not os.environ.get(k)]
    if missing:
        dead = (dead + "; " if dead else "") + "не задано секрет " + ", ".join(missing)
    ai_note = (("ШІ: " + main_llm.model) if main_llm else "⚠ Жоден ключ ШІ не працює, розбір шаблонний") + (f" ({dead})" if dead else "")
    if main_llm and an.LAST_ERROR[0]:
        ai_note = f"⚠ ШІ не відповів: {_short(an.LAST_ERROR[0])}"
    concepts, fresh, brief_err = [], False, None
    last = db.q("SELECT created FROM briefs ORDER BY id DESC LIMIT 1")
    due = force_brief or not last or (now - datetime.fromisoformat(last[0]["created"])).days >= cfg["brief"]["every_days"]
    brief_llm = _pick(cfg["brief"]["provider"], heavy=True) if due else None
    if brief_llm:  # без LLM шаблонний бриф гірший за останній справжній — лишаємо старий
        try:
            concepts = br.novelty_check(br.make_brief(brief_llm, winners, analyses, pats, cfg, cfg["brief"]["concepts"]), winners)
            db.x("INSERT INTO briefs (created, data) VALUES (?,?)", now.isoformat(), json.dumps(concepts, ensure_ascii=False))
            (out_dir / f"brief_{day}.md").write_text(br.render_md(concepts), encoding="utf-8")
            fresh = True
            log(f"04 Бриф: {len(concepts)} нових ідей")
        except Exception as e:  # noqa: BLE001 — нема балансу/ліміт: застосунок усе одно оновиться
            brief_err = str(e)[:200]
            log(f"⚠ Бриф не згенеровано: {brief_err}")
    if not concepts:
        last = db.q("SELECT data FROM briefs ORDER BY id DESC LIMIT 1")
        concepts = json.loads(last[0]["data"]) if last else []

    html = miniapp.build(cfg, now, stats, winners, analyses, concepts)
    (out_dir / "miniapp").mkdir(exist_ok=True)
    (out_dir / "miniapp" / "index.html").write_text(html, encoding="utf-8")
    if out:
        Path(out).write_text(html, encoding="utf-8")
    log(f"Застосунок зібрано: {len(winners)} конкурентів, {len(concepts)} ідей")

    if notify and (cfg.get("telegram") or {}).get("chat_id"):
        t = cfg["telegram"]
        who = ", ".join((state or {}).get("competitors", []))
        if manual is None and not os.environ.get(cfg["meta"].get("token_env", "META_ACCESS_TOKEN")):
            warn = "⚠ Нема секрету META_ACCESS_TOKEN на GitHub: не бачу конкурентів, яких ти додав у застосунку.\n"
        elif manual is None:
            warn = "⚠ Meta не віддала список конкурентів (мітки в кабінеті). Перевір ключ META_ACCESS_TOKEN.\n"
        elif not manual:
            warn = "Конкурентів ще не додано: застосунок → Ідеї → Конкуренти.\n"
        else:
            warn = ""
        txt = (f"🔍 <b>Оновив конкурентів та ідеї</b>\n" + warn
               + (f"Конкуренти: {telegram.esc(who)}\n" if who else "")
               + (f"Знайшов {n_ads} їхніх оголошень. " if n_ads is not None else "")
               + f"У застосунку: {len(winners)} оголошень, що крутяться довше тижня.\n"
               + (f"✨ {len(concepts)} нових сценаріїв для зйомки." if fresh else "Нових сценаріїв цього разу нема, лишив попередні."
                  + (f" Причина: {brief_err}" if brief_err else ""))
               + f"\n{telegram.esc(ai_note)}")
        telegram.send(t["chat_id"], txt, app_url=t.get("miniapp_url"), app_text="💡 Відкрити ідеї")
    return {"winners": winners, "stats": stats, "concepts": concepts, "analyses": analyses, "fresh": fresh}

"""Щотижневе оновлення: конкуренти → скоринг → розбір ШІ → нові ідеї → перебудова Mini App.

Усе про власну рекламу застосунок бере з Meta наживо, тому тут лише те, що потребує сервера:
скрапінг бібліотеки реклами й LLM-розбір із кешем у SQLite."""
import json
from datetime import datetime
from pathlib import Path

from . import analyze as an
from . import brief as br
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


def _pick(pref):
    """Бажаний провайдер, а якщо його ключа нема — інший доступний. None = без LLM."""
    for name in dict.fromkeys([pref, "anthropic", "gemini"]):
        m = llm.make(name) if name else None
        if m:
            return m
    return None


def run(slug, now=None, force_brief=False, skip_collect=False, out=None, notify=False):
    cfg, db = load_client(slug)
    now = now or now_utc()
    day = now.date().isoformat()
    out_dir = Path(cfg["_dir"]) / "out"
    out_dir.mkdir(exist_ok=True)

    n_ads = None
    if not skip_collect:
        ads, src = sources.collect(cfg)
        db.upsert_ads(ads, day)
        n_ads = len(ads)
        log(f"01 Ad Library ({src}): {n_ads} оголошень, знімок {day}")

    winners, stats = scoring.score_creatives(db, now, cfg)
    log(f"02 Скоринг: {stats['creatives']} креативів → {stats['winners']} ≥{cfg['scoring']['min_days']} дн → топ {len(winners)}")

    main_llm = _pick(cfg["analysis"]["provider"])
    video_llm = llm.make(cfg["analysis"].get("video_provider"))
    analyses = an.analyze(db, winners, cfg, main_llm, video_llm)
    pats = an.patterns(winners, analyses, stats["fresh"])

    ai_note = ("ШІ: " + main_llm.model) if main_llm else "⚠ Ключ ШІ не знайдено (секрет GEMINI_API_KEY), розбір шаблонний"
    if main_llm and an.LAST_ERROR[0]:
        ai_note = f"⚠ ШІ не відповів: {an.LAST_ERROR[0]}"
    concepts, fresh, brief_err = [], False, None
    last = db.q("SELECT created FROM briefs ORDER BY id DESC LIMIT 1")
    due = force_brief or not last or (now - datetime.fromisoformat(last[0]["created"])).days >= cfg["brief"]["every_days"]
    brief_llm = _pick(cfg["brief"]["provider"]) if due else None
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
        txt = (f"🔍 <b>Оновив конкурентів та ідеї</b>\n"
               + (f"Переглянув {n_ads} оголошень. " if n_ads else "")
               + f"Окупаються (крутяться 2+ тижні): {stats['winners']}.\n"
               + (f"✨ {len(concepts)} нових сценаріїв для зйомки." if fresh else "Нових сценаріїв цього разу нема, лишив попередні."
                  + (f" Причина: {brief_err}" if brief_err else ""))
               + f"\n{telegram.esc(ai_note)}")
        telegram.send(t["chat_id"], txt, app_url=t.get("miniapp_url"), app_text="💡 Відкрити ідеї")
    return {"winners": winners, "stats": stats, "concepts": concepts, "analyses": analyses, "fresh": fresh}

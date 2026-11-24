"""
Скоринг креативів конкурентів. «Днів у ротації» сам по собі слабкий сигнал (забуті оголошення теж живуть довго),
тому складений бал:
  score = 0.25·days + 0.15·variants + 0.15·reuse + 0.1·survived_refresh + 0.35·impressions_rank   (0..1)
impressions_rank — позиція на сторінці конкурента в Ad Library, відсортованій за показами (є тільки з власного
скрапера). Якщо рангу нема — його вага перерозподіляється на решту компонент.
"""
import re
import math
from collections import defaultdict
from datetime import datetime

from .util import ts


def _norm_log(x, cap):
    return min(1.0, math.log1p(max(0, x)) / math.log1p(cap))


def score_creatives(db, now, cfg):
    sc = cfg.get("scoring", {})
    min_days = sc.get("min_days", 14)
    days_cap = sc.get("days_cap", 90)
    w = sc.get("weights", {"days": 0.25, "variants": 0.15, "reuse": 0.15, "refresh": 0.1, "rank": 0.35})

    ads = db.q("SELECT * FROM ads")
    snaps = db.q("SELECT day, ad_id, is_active FROM snapshots")
    days_list = sorted({s["day"] for s in snaps})
    last_day = days_list[-1] if days_list else None
    active_now = {s["ad_id"] for s in snaps if s["day"] == last_day and s["is_active"]}
    present = defaultdict(set)  # day -> ad_ids
    for s in snaps:
        if s["is_active"]:
            present[s["day"]].add(s["ad_id"])

    # «оновлення пачки» сторінки = день, коли зникло ≥2 її оголошень
    page_of = {a["ad_id"]: a["page_id"] for a in ads}
    refresh_days = defaultdict(list)
    for prev, cur in zip(days_list, days_list[1:]):
        gone = defaultdict(int)
        for ad_id in present[prev] - present[cur]:
            gone[page_of.get(ad_id)] += 1
        for pid, n in gone.items():
            if n >= 2:
                refresh_days[pid].append((prev, cur))

    groups = defaultdict(list)
    for a in ads:
        groups[(a["page_id"], a["creative_hash"])].append(a)

    out = []
    for (pid, h), items in groups.items():
        live = [a for a in items if a["ad_id"] in active_now]
        if not live:
            continue
        starts = sorted(ts(a["start_date"]) for a in items if a["start_date"])
        days = (now - starts[0]).days
        variants = max(len(live), max(a["collation_count"] or 1 for a in live))
        start_weeks = {(s.isocalendar()[0], s.isocalendar()[1]) for s in starts}
        reuse = 1.0 if len(start_weeks) >= 2 and (starts[-1] - starts[0]).days >= 7 else 0.0
        survived = 0.0
        ids = {a["ad_id"] for a in items}
        for prev, cur in refresh_days.get(pid, []):
            if ids & present[prev] and ids & present[cur]:
                survived = 1.0
                break
        parts = {"days": _norm_log(days, days_cap), "variants": _norm_log(variants - 1, 9),
                 "reuse": reuse, "refresh": survived}
        ranked = [a for a in live if a.get("rank") is not None and a.get("rank_total")]
        if ranked:  # найкраща позиція серед копій креативу; топ сторінки = 1.0
            parts["rank"] = max(1 - a["rank"] / max(1, a["rank_total"] - 1) for a in ranked)
        wsum = sum(w[k] for k in parts)
        s = sum(w[k] * v for k, v in parts.items()) / wsum
        rep = max(live, key=lambda a: (bool(a["video_url"]), len(a["text"] or "")))
        out.append({
            "creative_hash": h, "page_id": pid, "page_name": rep["page_name"],
            "ad_id": rep["ad_id"], "ad_ids": sorted(ids), "days": days, "variants": variants,
            "reuse": bool(reuse), "survived_refresh": bool(survived),
            "score": round(s, 3), "impr_rank": min((a["rank"] for a in ranked), default=None), "text": rep["text"], "title": rep["title"], "cta": rep["cta"],
            "format": rep["format"], "video_url": rep["video_url"], "image_url": rep["image_url"],
            "link": rep["link"], "snapshot_url": f"https://www.facebook.com/ads/library/?id={rep['ad_id']}",
            "text_source": "body" if rep["text"] else ("title" if rep["title"] else "none"),
        })
    out.sort(key=lambda x: x["score"], reverse=True)
    rx = cfg.get("relevance_rx")
    if rx:  # пошук за словами тягне чуже («AI-лампа», «автоматизація лінії»): лишаємо тільки свою нішу
        r = re.compile(rx, re.I)
        out = [c for c in out if r.search(f"{c['text'] or ''} {c['title'] or ''}")]
    xr = cfg.get("exclude_rx")
    if xr:  # курси, інтенсиви, школи: продають навчання, а не послугу — це не конкуренти
        r = re.compile(xr, re.I)
        out = [c for c in out if not r.search(f"{c['page_name'] or ''} {c['text'] or ''} {c['title'] or ''}")]
    winners = [c for c in out if c["days"] >= min_days]
    per_page, top, seen = defaultdict(int), [], set()
    for c in winners:
        key = " ".join((c["text"] or c["title"] or "").lower().split())[:90]
        if key and key in seen:  # той самий текст з іншою картинкою — одна ідея, не дублюємо
            continue
        seen.add(key)
        if per_page[c["page_id"]] < sc.get("max_per_page", 3):
            top.append(c)
            per_page[c["page_id"]] += 1
        if len(top) >= sc.get("top_n", 12):
            break
    stats = {
        "ads_total": len(ads), "active": len(active_now), "creatives": len(out),
        "winners": len(winners), "advertisers": len({a["page_id"] for a in ads}),
        "snapshot_days": len(days_list), "max_days": max((c["days"] for c in out), default=0),
        "fresh": [c for c in out if c["days"] < min_days],
    }
    return top, stats

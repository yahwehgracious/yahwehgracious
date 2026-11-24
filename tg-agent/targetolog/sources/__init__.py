"""
Джерела Ad Library. Усе зводиться до однієї схеми (normalize):
ad_id, page_id, page_name, text, title, cta, link, format, video_url, image_url,
platforms, collation_count, collation_id, start_date, end_date, is_active, creative_hash, raw
"""
import json
import os
import urllib.parse
from pathlib import Path

from ..util import http, log, text_hash, ts


def _g(d, *keys, default=None):
    """Перше непорожнє значення з кількох варіантів ключа (snake/camel у різних акторів)."""
    for k in keys:
        cur = d
        for part in k.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
            if cur is None:
                break
        if cur not in (None, "", []):
            return cur
    return default


def normalize(a):
    s = _g(a, "snapshot", default={}) or {}
    body = _g(s, "body", default="")
    if isinstance(body, dict):
        body = body.get("text") or ""
    bodies = _g(a, "ad_creative_bodies", default=[])
    text = body or (bodies[0] if bodies else "")
    titles = _g(a, "ad_creative_link_titles", default=[])
    title = _g(s, "title", "link_title") or _g(a, "ad_creative_link_title") or (titles[0] if titles else "") or ""
    cards = _g(s, "cards", default=[]) or []
    if not text and cards:
        text = " | ".join(filter(None, (c.get("body") or c.get("title") for c in cards)))

    videos = _g(s, "videos", default=[]) or []
    if not videos and cards:
        videos = [c for c in cards if c.get("video_hd_url") or c.get("video_sd_url")]
    images = _g(s, "images", default=[]) or []
    video_url = (videos[0].get("video_hd_url") or videos[0].get("video_sd_url") or videos[0].get("videoHdUrl") or "") if videos else ""
    image_url = ""
    if images:
        image_url = images[0].get("original_image_url") or images[0].get("resized_image_url") or ""
    elif videos:
        image_url = videos[0].get("video_preview_image_url") or ""
    elif cards:
        image_url = cards[0].get("original_image_url") or cards[0].get("resized_image_url") or ""

    fmt = (_g(s, "display_format", "displayFormat") or "").upper()
    is_template = "{{product." in (text or "") or "{{product." in title
    if is_template:
        fmt, title, text = "CATALOG", "[динамічний каталог]", ""
    elif fmt in ("", "DCO", "DPA"):
        # DCO (динамічний креатив) — реальний формат визначаємо за медіа в картках
        kind = "VIDEO" if video_url else "CAROUSEL" if fmt == "" and len(cards) > 1 else "IMAGE" if image_url else "UNKNOWN"
        fmt = f"DCO·{kind}" if fmt == "DCO" else kind
    title = title.strip(" |")
    parts = [x.strip() for x in title.split(" | ") if x.strip()]
    if len(parts) >= 2 and len(set(parts)) == 1:
        title = parts[0]

    ad_id = str(_g(a, "ad_archive_id", "adArchiveID", "adArchiveId", "id"))
    start = ts(_g(a, "start_date", "startDate", "ad_delivery_start_time", "startDateFormatted"))
    end = ts(_g(a, "end_date", "endDate", "ad_delivery_stop_time"))
    is_active = _g(a, "is_active", "isActive")
    if is_active is None:
        is_active = end is None
    platforms = _g(a, "publisher_platform", "publisherPlatform", "publisher_platforms", default=[]) or []
    cta = _g(s, "cta_text", "ctaText", default="") or ""
    key_text = text or title or ad_id
    return {
        "ad_id": ad_id,
        "page_id": str(_g(a, "page_id", "pageID", "pageId", "snapshot.page_id", default="")),
        "page_name": _g(a, "page_name", "pageName", "snapshot.page_name", default="?"),
        "text": (text or "").strip(),
        "title": title,
        "cta": cta,
        "link": _g(s, "link_url", "linkUrl", default="") or "",
        "format": fmt,
        "video_url": video_url,
        "image_url": image_url,
        "platforms": platforms if isinstance(platforms, list) else [platforms],
        "collation_count": int(_g(a, "collation_count", "collationCount", default=1) or 1),
        "collation_id": str(_g(a, "collation_id", "collationID", "collationId", default="") or ""),
        "start_date": start.isoformat() if start else None,
        "end_date": end.isoformat() if end else None,
        "is_active": bool(is_active),
        "rank": a.get("_rank"), "rank_total": a.get("_rank_total"),
        "creative_hash": text_hash(f"{key_text}|{video_url.split('?')[0][-40:] if video_url else image_url.split('?')[0][-40:]}"),
        "raw": a,
    }


def library_url(cfg, term=None, page_id=None):
    p = {"active_status": "active", "ad_type": "all", "country": cfg.get("country", "UA"), "media_type": "all"}
    if term:
        p.update(q=term, search_type="keyword_unordered")
    if page_id:
        p.update(view_all_page_id=page_id, search_type="page")
        p["sort_data[mode]"], p["sort_data[direction]"] = "total_impressions", "desc"
    return "https://www.facebook.com/ads/library/?" + urllib.parse.urlencode(p)


def fetch_file(cfg):
    path = Path(cfg["_dir"]) / cfg["source"]["file"]
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_apify(cfg):
    """
    Apify run-sync. Формат input залежить від актора — звір з вкладкою Input.
    curious_coder~facebook-ads-library-scraper: {"urls":[{"url":..}], "count":N}
    apify~facebook-ads-scraper:                {"startUrls":[{"url":..}], "resultsLimit":N}
    """
    src = cfg["source"]
    token = os.environ.get("APIFY_TOKEN") or os.environ.get(src.get("token_env", "")) or ""
    if not token:
        raise RuntimeError("APIFY_TOKEN не задано")
    actor = src.get("actor", "curious_coder~facebook-ads-library-scraper")
    urls = [{"url": library_url(cfg, page_id=p)} for p in cfg.get("competitor_page_ids", [])]
    urls += [{"url": library_url(cfg, term=t)} for t in cfg.get("search_terms", [])]
    n = src.get("max_items", 500)
    payload = {"startUrls": urls, "resultsLimit": n} if actor.startswith("apify~") else {"urls": urls, "count": n}
    payload.update(src.get("extra_input", {}))
    log(f"Apify {actor}: {len(urls)} URL, ліміт {n}")
    items = http(f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?token={token}",
                 payload, timeout=330, retries=1)
    return items or []


def fetch_scrapecreators(cfg):
    """ScrapeCreators Facebook Ad Library. Ендпоінти й параметри звір з їхньою документацією."""
    key = os.environ.get("SCRAPECREATORS_API_KEY") or ""
    if not key:
        raise RuntimeError("SCRAPECREATORS_API_KEY не задано")
    base = "https://api.scrapecreators.com/v1/facebook/adLibrary"
    out = []
    for pid in cfg.get("competitor_page_ids", []):
        cursor = None
        for _ in range(cfg["source"].get("max_pages", 5)):
            q = {"pageId": pid, "country": cfg.get("country", "UA"), "status": "ACTIVE"}
            if cursor:
                q["cursor"] = cursor
            r = http(f"{base}/company/ads?" + urllib.parse.urlencode(q), headers={"x-api-key": key})
            out += r.get("results") or r.get("ads") or []
            cursor = r.get("cursor")
            if not cursor:
                break
    return out


def fetch_playwright(cfg):
    from .fb_scraper import fetch_playwright as f  # імпорт тут: playwright потрібен тільки цьому джерелу
    return f(cfg)


FETCHERS = {"file": fetch_file, "playwright": fetch_playwright, "apify": fetch_apify,
            "scrapecreators": fetch_scrapecreators}


def collect(cfg):
    """Основне джерело + фолбек. Валідація: якщо >40% без тексту — попередження."""
    kinds = [cfg["source"]["kind"]] + ([cfg["source"]["fallback"]] if cfg["source"].get("fallback") else [])
    last_err = None
    for kind in kinds:
        try:
            raw = FETCHERS[kind](cfg)
            ads = [normalize(a) for a in raw]
            ads = [a for a in ads if a["ad_id"] and a["ad_id"] != "None" and a["start_date"]]
            if not ads:
                raise RuntimeError(f"{kind}: 0 оголошень")
            no_text = sum(1 for a in ads if not a["text"]) / len(ads)
            if no_text > 0.4 and kind != "file":
                log(f"⚠ {kind}: {no_text:.0%} оголошень без тексту — перевір актор/схему")
            return ads, kind
        except Exception as e:  # noqa: BLE001 — фолбек на будь-яку помилку джерела
            last_err = e
            log(f"Джерело {kind} впало: {e}")
    raise RuntimeError(f"Усі джерела впали: {last_err}")

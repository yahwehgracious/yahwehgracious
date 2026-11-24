"""
Власний скрапер Meta Ad Library на Playwright — замість Apify.

Як працює:
  1. Відкриває публічну сторінку Ad Library (без логіну — логін ніколи не використовуємо, ризик бану акаунта).
  2. Перші результати Meta вшиває в HTML (<script type="application/json">), наступні довантажує при скролі
     через POST /api/graphql/. Перехоплюємо обидва джерела.
  3. Не прив'язуємось до шляху в JSON: рекурсивно шукаємо будь-який обʼєкт з `ad_archive_id` + `snapshot`.
     Тому зміна вкладеності у відповіді Meta скрапер не ламає — ламає тільки зміна самих назв полів.
  4. Скролимо, поки приходять нові оголошення або до max_items / max_scrolls.

Вихід — сирі обʼєкти у тому ж форматі, що й у Apify-актора curious_coder (snake_case), їх читає sources.normalize.

Встановлення: pip install playwright && playwright install chromium
"""
import json
import random
import re
import time

from ..util import log

AD_KEYS = ("ad_archive_id", "adArchiveID")


def _strip(text):
    # Meta віддає JSON з префіксом проти JSON-hijacking і інколи кілька JSON-ів рядками
    text = re.sub(r"^\s*for\s*\(;;\);", "", text)
    out = []
    for chunk in text.splitlines() or [text]:
        chunk = chunk.strip()
        if chunk.startswith(("{", "[")):
            try:
                out.append(json.loads(chunk))
            except ValueError:
                pass
    if not out:
        try:
            out.append(json.loads(text))
        except ValueError:
            pass
    return out


def walk_ads(obj, found):
    """Збирає обʼєкти-оголошення в порядку появи (порядок = ранг за показами на сторінці конкурента).
    found: dict ad_id -> obj (dict зберігає порядок вставки)."""
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            ad_id = next((cur[k] for k in AD_KEYS if cur.get(k)), None)
            if ad_id and isinstance(cur.get("snapshot"), dict):
                prev = found.get(str(ad_id))
                if not prev:
                    found[str(ad_id)] = cur
                elif len(json.dumps(cur)) > len(json.dumps(prev)):  # повніша версія, позицію не змінюємо
                    found[str(ad_id)] = cur
                continue
            stack.extend(reversed(list(cur.values())))
        elif isinstance(cur, list):
            stack.extend(reversed(cur))
    return found


def extract_from_html(html, found):
    for m in re.finditer(r'<script type="application/json"[^>]*>(.*?)</script>', html, re.S):
        if "ad_archive_id" not in m.group(1):
            continue
        for obj in _strip(m.group(1)):
            walk_ads(obj, found)
    return found


class AdLibraryScraper:
    def __init__(self, headless=True, proxy=None, locale="uk-UA", min_delay=1.5, max_delay=3.5, base_url=None):
        self.headless, self.proxy, self.locale = headless, proxy, locale
        self.min_delay, self.max_delay = min_delay, max_delay
        self.base_url = base_url  # для тестів на локальному сервері
        self._pw = self._browser = self._ctx = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        args = {"headless": self.headless, "args": ["--disable-blink-features=AutomationControlled"]}
        if self.proxy:
            args["proxy"] = {"server": self.proxy}
        self._browser = self._pw.chromium.launch(**args)
        self._ctx = self._browser.new_context(
            locale=self.locale, viewport={"width": 1366, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"))
        # картинки й відео не вантажимо — швидше і менше трафіку; URL медіа все одно є в JSON
        self._ctx.route(re.compile(r".*\.(png|jpe?g|webp|gif|mp4|woff2?)(\?.*)?$"), lambda r: r.abort())
        return self

    def __exit__(self, *exc):
        for x in (self._ctx, self._browser):
            try:
                x and x.close()
            except Exception:  # noqa: BLE001
                pass
        if self._pw:
            self._pw.stop()

    def _pause(self, k=1.0):
        time.sleep(random.uniform(self.min_delay, self.max_delay) * k)

    def scrape_url(self, url, max_items=300, max_scrolls=40):
        found = {}
        page = self._ctx.new_page()

        def on_response(resp):
            if "/api/graphql" not in resp.url:
                return
            try:
                body = resp.text()
            except Exception:  # noqa: BLE001 — відповідь могла закритись
                return
            if "ad_archive_id" in body:
                for obj in _strip(body):
                    walk_ads(obj, found)

        page.on("response", on_response)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            self._pause()
            self._dismiss_dialogs(page)
            extract_from_html(page.content(), found)
            if "/login" in page.url:
                raise RuntimeError("Meta показала логін-стіну — зменш частоту/зміни IP")
            stale = 0
            for i in range(max_scrolls):
                before = len(found)
                page.mouse.wheel(0, random.randint(2500, 4000))
                self._pause(0.8)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:  # noqa: BLE001
                    pass
                if len(found) >= max_items:
                    break
                stale = stale + 1 if len(found) == before else 0
                if stale >= 3:  # тричі нічого нового — кінець списку
                    break
            log(f"   {len(found)} оголошень · {url.split('?')[1][:90]}")
        finally:
            page.close()
        ads = list(found.values())[:max_items]
        # Сторінка конкурента сортується за показами (sort_data[mode]=total_impressions) —
        # позиція в списку = ранг обсягу показів серед його активних оголошень. Найсильніший доступний сигнал.
        by_page = "view_all_page_id=" in url
        for i, a in enumerate(ads):
            a["_rank"], a["_rank_total"], a["_rank_source"] = (i, len(ads), "page_impressions") if by_page else (None, None, None)
        return ads

    @staticmethod
    def _dismiss_dialogs(page):
        # cookie-банер (ЄС/частина IP) і «увійдіть» — закриваємо без логіну, обираємо мінімум cookies
        for label in ("Decline optional cookies", "Відхилити необовʼязкові файли cookie", "Відхилити необов'язкові файли cookie",
                      "Only allow essential cookies", "Закрити", "Close"):
            try:
                btn = page.get_by_role("button", name=label)
                if btn.count():
                    btn.first.click(timeout=2000)
                    time.sleep(0.5)
            except Exception:  # noqa: BLE001
                pass


def fetch_playwright(cfg):
    from . import library_url
    src = cfg["source"]
    urls = [library_url(cfg, page_id=p) for p in cfg.get("competitor_page_ids", [])]
    urls += [library_url(cfg, term=t) for t in cfg.get("search_terms", [])]
    if src.get("base_url"):  # тест: підміна домену
        urls = [u.replace("https://www.facebook.com", src["base_url"]) for u in urls]
    per_url = src.get("max_items_per_url", 200)
    out = {}
    with AdLibraryScraper(headless=src.get("headless", True), proxy=src.get("proxy"),
                          min_delay=src.get("min_delay", 1.5), max_delay=src.get("max_delay", 3.5)) as s:
        for n, url in enumerate(urls):
            for attempt in range(2):
                try:
                    for ad in s.scrape_url(url, max_items=per_url, max_scrolls=src.get("max_scrolls", 40)):
                        k = str(ad.get("ad_archive_id") or ad.get("adArchiveID"))
                        if k not in out or (ad.get("_rank") is not None and out[k].get("_rank") is None):
                            out[k] = ad  # ранг зі сторінки конкурента важливіший за позицію в пошуку
                    break
                except Exception as e:  # noqa: BLE001
                    log(f"   спроба {attempt + 1} впала: {e}")
                    time.sleep(10 * (attempt + 1))
            if n < len(urls) - 1:
                time.sleep(random.uniform(*src.get("between_urls_s", [4, 9])))
    log(f"Playwright: {len(out)} унікальних оголошень з {len(urls)} запитів")
    return list(out.values())

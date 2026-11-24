import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from targetolog import brief, scoring, sources  # noqa: E402
from targetolog.db import DB  # noqa: E402
from targetolog.pipeline import DEFAULTS, _merge  # noqa: E402

NOW = datetime(2026, 11, 23, 7, tzinfo=timezone.utc)

APIFY_ITEM = {  # форма виходу curious_coder/facebook-ads-library-scraper
    "ad_archive_id": "111", "page_id": "p1", "page_name": "ЖК Тест", "is_active": True,
    "start_date": int((NOW - timedelta(days=40)).timestamp()), "end_date": None, "collation_count": 4,
    "collation_id": "c1", "publisher_platform": ["FACEBOOK", "INSTAGRAM"],
    "snapshot": {"body": {"text": "Розстрочка 0% на 24 місяці. Готові квартири біля метро."}, "title": "ЖК Тест",
                 "cta_text": "Дізнатися більше", "display_format": "VIDEO", "link_url": "https://x.ua",
                 "videos": [{"video_hd_url": "https://v/1.mp4", "video_preview_image_url": "https://i/1.jpg"}]},
}
OFFICIAL_ITEM = {  # camelCase-форма (apify/facebook-ads-scraper)
    "adArchiveID": "222", "pageID": "p2", "pageName": "Blago", "isActive": True,
    "startDate": (NOW - timedelta(days=5)).isoformat(), "collationCount": 1, "publisherPlatform": ["INSTAGRAM"],
    "snapshot": {"body": {"text": "Старт продажів"}, "displayFormat": "IMAGE", "images": [{"original_image_url": "https://i/2.jpg"}]},
}


class T(unittest.TestCase):
    def cfg(self):
        return _merge(DEFAULTS, {"kpi": {"target_cpl": 18}})

    def test_normalize_both_formats(self):
        a, b = sources.normalize(APIFY_ITEM), sources.normalize(OFFICIAL_ITEM)
        self.assertEqual((a["ad_id"], a["format"], a["collation_count"]), ("111", "VIDEO", 4))
        self.assertTrue(a["video_url"].endswith("1.mp4"))
        self.assertEqual((b["ad_id"], b["page_name"], b["format"]), ("222", "Blago", "IMAGE"))
        self.assertTrue(b["image_url"])

    def test_scoring_reuse_and_refresh(self):
        db = DB(":memory:")
        x = sources.normalize(APIFY_ITEM)
        y = dict(x, ad_id="112", start_date=(NOW - timedelta(days=10)).isoformat())   # той самий креатив, перезапуск
        z = sources.normalize(dict(APIFY_ITEM, ad_archive_id="113", snapshot={"body": {"text": "інше"}}))
        w = sources.normalize(dict(APIFY_ITEM, ad_archive_id="114", snapshot={"body": {"text": "ще інше"}}))
        db.upsert_ads([x, y, z, w], "2026-11-20")
        db.upsert_ads([x, y], "2026-11-23")  # z і w зникли → «оновлення пачки», x пережив
        top, st = scoring.score_creatives(db, NOW, self.cfg())
        self.assertEqual(len(top), 1)
        self.assertTrue(top[0]["reuse"])
        self.assertTrue(top[0]["survived_refresh"])
        self.assertGreaterEqual(top[0]["variants"], 4)


    def test_novelty(self):
        refs = [{"text": "Розстрочка 0% на 24 місяці без банку для всіх покупців"}]
        c = brief.novelty_check([{"primary_text": "Наша розстрочка 0% на 24 місяці без банку", "hooks": []}], refs)
        self.assertTrue(c[0]["_copy_risk"])


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_adlibrary import ad, serve, wrap  # noqa: E402
from targetolog.sources import fb_scraper, normalize  # noqa: E402

try:
    import playwright  # noqa: F401
    HAS_PW = True
except ImportError:
    HAS_PW = False


class T(unittest.TestCase):
    def test_walk_and_strip(self):
        import json
        found = {}
        for obj in fb_scraper._strip("for (;;);" + json.dumps(wrap([ad(1), ad(2)]))):
            fb_scraper.walk_ads(obj, found)
        self.assertEqual(set(found), {"5001", "5002"})
        n = normalize(found["5001"])
        self.assertEqual((n["format"], n["collation_count"]), ("VIDEO", 2))

    @unittest.skipUnless(HAS_PW, "playwright не встановлено")
    def test_browser_scroll_and_intercept(self):
        srv = serve()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        cfg = {"country": "UA", "competitor_page_ids": ["p1"], "search_terms": [],
               "source": {"kind": "playwright", "base_url": base, "min_delay": 0.2, "max_delay": 0.4,
                          "between_urls_s": [0, 0], "max_scrolls": 10}}
        ads = fb_scraper.fetch_playwright(cfg)
        srv.shutdown()
        self.assertEqual(len(ads), 2 + 3 * 5)  # 2 з HTML + 3 сторінки по 5 з graphql
        self.assertEqual([a["_rank"] for a in ads], list(range(17)))           # порядок збережено
        self.assertEqual([a["ad_archive_id"] for a in ads[:3]], ["5000", "5001", "5010"])


if __name__ == "__main__":
    unittest.main()


class Real(unittest.TestCase):
    """Структура, знята з живої Ad Library (див. fixtures/real_adlibrary_sample.json)."""

    def test_real_structure(self):
        import json
        raw = json.loads((Path(__file__).parent / "fixtures/real_adlibrary_sample.json").read_text(encoding="utf-8"))
        a, cat, v = [normalize(x) for x in raw]
        self.assertEqual(a["format"], "DCO·VIDEO")
        self.assertTrue(a["video_url"].endswith("c.mp4"))
        self.assertTrue(a["is_active"])                   # end_date заповнений, але оголошення активне
        self.assertEqual((a["rank"], a["rank_total"]), (0, 200))
        self.assertEqual((cat["format"], cat["text"]), ("CATALOG", ""))
        self.assertEqual(v["format"], "VIDEO")

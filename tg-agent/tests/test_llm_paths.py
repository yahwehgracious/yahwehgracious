"""Smoke-тест LLM-гілок з фейковою моделлю: парсинг JSON розбору, брифу і відео-аналізу."""
import json
import sys
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from targetolog import analyze, llm, pipeline  # noqa: E402


class FakeLLM:
    def __init__(self, name):
        self.model, self.tokens, self.cost = f"fake-{name}", Counter(), 0.0

    def __call__(self, system, user, max_tokens=0, media=None):
        if media:
            return '```json\n{"hook":{"type":"демонстрація результату/обʼєкта","text":"дрон над ЖК"},"offer":{"type":"розстрочка","details":"0% 24 міс"},"angle":"розстрочка без банку","confidence":"high"}\n```'
        if "Розбери креативи" in user:
            ids = [l.split("id=")[1].split(" ")[0] for l in user.splitlines() if l.startswith("id=")]
            return json.dumps([{"id": i, "hook": {"type": "питання", "text": "?"}, "offer": {"type": "розстрочка"},
                                "angle": "єОселя", "why_works": "тест", "confidence": "medium"} for i in ids])
        return json.dumps([{"concept": f"C{i}", "persona": p, "angle": a, "format": f, "hooks": ["h1"],
                            "script": [{"t": "0-3с", "frame": "дрон", "on_screen": "x", "voice": "y"}],
                            "primary_text": "текст", "headline": "заг", "lead_form": {"type": "Instant Form", "questions": ["q"]},
                            "success": "ok"} for i, (p, a, f) in enumerate([("сімʼя", "єОселя", "Reels"), ("інвестор", "оренда", "статика")])])


def _json(self, system, user, max_tokens=0, media=None):
    from targetolog.util import parse_json
    return parse_json(self(system, user, media=media))


FakeLLM.json = _json


class T(unittest.TestCase):
    def test_full_run_with_fake_llm(self):
        import shutil
        src, tmp = pipeline.ROOT / "clients/ivan", pipeline.ROOT / "clients/_t_llm"
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.copytree(src, tmp, ignore=shutil.ignore_patterns("data.sqlite", "out"))
        cfg = json.loads((tmp / "client.json").read_text(encoding="utf-8"))
        cfg["source"] = {"kind": "file", "file": cfg["source"]["file"]}
        (tmp / "client.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        try:
            with mock.patch.object(llm, "make", lambda name: FakeLLM(name) if name else None), \
                 mock.patch.object(analyze, "_download", lambda url, limit_mb=20: b"\x00" * 100):
                r = pipeline.run("_t_llm", now=datetime(2026, 11, 24, 7, tzinfo=timezone.utc), force_brief=True)
            self.assertEqual(len(r["concepts"]), 6)  # 3 пачки по 2
            self.assertTrue(r["fresh"])
            self.assertTrue(all(a.get("confidence") in ("medium", "high", "low") for a in r["analyses"].values()))
            html = (tmp / "out/miniapp/index.html").read_text(encoding="utf-8")
            self.assertIn('"concept": "C0"', html)
            self.assertNotIn("__DATA__", html)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()

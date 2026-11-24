import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from targetolog import daily  # noqa: E402

NOW = datetime(2026, 11, 24, 7, tzinfo=timezone.utc)
OLD, NEW = "2026-11-10T10:00:00+0000", "2026-11-23T20:00:00+0000"
KPI = {"target_cpl": 60, "target_lead": 150, "target_click": 8}
SETS = [{"id": "S1", "name": "Direct", "effective_status": "ACTIVE", "optimization_goal": "CONVERSATIONS", "daily_budget": "13500", "created_time": OLD},
        {"id": "S2", "name": "Форма", "effective_status": "ACTIVE", "optimization_goal": "LEAD_GENERATION", "daily_budget": "10000", "created_time": OLD}]


def ad(i, s, created=OLD, st="ACTIVE"):
    return {"id": i, "name": i, "adset_id": s, "effective_status": st, "created_time": created}


class T(unittest.TestCase):
    def test_rules(self):
        ads = [ad("a", "S1"), ad("b", "S1"), ad("new", "S1", NEW), ad("only", "S2")]
        ins = {"a": {"spend": 200, "conv": 0, "freq": 1}, "b": {"spend": 300, "conv": 10, "freq": 3.6},
               "new": {"spend": 500, "conv": 0, "freq": 1}, "only": {"spend": 400, "lead": 0, "freq": 1}}
        sins = {"S1": {"spend": 300, "conv": 10}, "S2": {"spend": 400, "lead": 0}}
        r = {(x["kind"], x["name"]) for x in daily.evaluate(ads, SETS, ins, sins, KPI, NOW)}
        self.assertIn(("pause", "a"), r)          # 200 ₴ і 0 переписок
        self.assertIn(("fatigue", "b"), r)        # частота 3.6
        self.assertIn(("scale", "Direct"), r)     # 10 переписок по 30 при нормі 60
        self.assertIn(("replace", "only"), r)     # єдине в групі — не вимикаємо
        self.assertFalse(any(n == "new" for _, n in r))  # молодше 72 год не чіпаємо

    def test_lead_norm_and_message(self):
        ads = [ad("x", "S2"), ad("y", "S2"), ad("bad", "S2", st="DISAPPROVED")]
        ads[2]["ad_review_feedback"] = {"global": {"PERSONAL_ATTRIBUTES": "Особисті характеристики"}}
        ins = {"x": {"spend": 800, "lead": 3, "freq": 1}, "y": {"spend": 100, "lead": 1, "freq": 1}}
        rec = daily.evaluate(ads, SETS, ins, {}, KPI, NOW)
        self.assertEqual([(x["kind"], x["name"]) for x in rec], [("pause", "x")])  # 267 ₴ за заявку > 150 × 1.5
        w = {"spend": 900, "conv": 0, "lead": 4, "link": 0}
        txt = daily.message("acc", w, w, ads, rec, KPI)
        self.assertIn("4 заявки", txt)
        self.assertIn("Особисті характеристики", txt)

    def test_norms_label(self):
        self.assertEqual(daily.norms_from_labels([{"name": "інше"}, {"name": "ai_norms conv=112 lead=150 link=13"}]),
                         {"target_cpl": 112.0, "target_lead": 150.0, "target_click": 13.0})

    def test_plural(self):
        self.assertEqual([daily.pl(n, daily.RES["conv"]) for n in (1, 3, 5, 11, 22, 25)],
                         ["переписка", "переписки", "переписок", "переписок", "переписки", "переписок"])


if __name__ == "__main__":
    unittest.main()

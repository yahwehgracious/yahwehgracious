"""SQLite-архів клієнта: знімки Ad Library (історія показу конкурентів), кеш LLM-розборів, ідеї."""
import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS ads (
  ad_id TEXT PRIMARY KEY,
  page_id TEXT, page_name TEXT,
  text TEXT, title TEXT, cta TEXT, link TEXT,
  format TEXT, video_url TEXT, image_url TEXT,
  platforms TEXT, collation_count INTEGER, collation_id TEXT,
  start_date TEXT, end_date TEXT,
  creative_hash TEXT,
  first_seen TEXT, last_seen TEXT,
  raw TEXT,
  rank INTEGER, rank_total INTEGER
);
CREATE INDEX IF NOT EXISTS ads_hash ON ads(creative_hash);
CREATE INDEX IF NOT EXISTS ads_page ON ads(page_id);

CREATE TABLE IF NOT EXISTS snapshots (
  day TEXT, ad_id TEXT, is_active INTEGER,
  PRIMARY KEY(day, ad_id)
);

CREATE TABLE IF NOT EXISTS analyses (
  creative_hash TEXT PRIMARY KEY,
  model TEXT, created TEXT, data TEXT
);

CREATE TABLE IF NOT EXISTS briefs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, data TEXT
);
"""


class DB:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.c = sqlite3.connect(path)
        self.c.row_factory = sqlite3.Row
        self.c.executescript(SCHEMA)
        cols = {r[1] for r in self.c.execute("PRAGMA table_info(ads)")}
        for col in ("rank", "rank_total"):  # міграція старих баз
            if col not in cols:
                self.c.execute(f"ALTER TABLE ads ADD COLUMN {col} INTEGER")

    def q(self, sql, *args):
        return [dict(r) for r in self.c.execute(sql, args).fetchall()]

    def x(self, sql, *args):
        cur = self.c.execute(sql, args)
        self.c.commit()
        return cur

    # --- Ad Library
    def upsert_ads(self, ads, day):
        for a in ads:
            row = self.c.execute("SELECT first_seen FROM ads WHERE ad_id=?", (a["ad_id"],)).fetchone()
            first = row["first_seen"] if row else day
            self.c.execute("""INSERT OR REPLACE INTO ads (ad_id, page_id, page_name, text, title, cta, link, format,
                video_url, image_url, platforms, collation_count, collation_id, start_date, end_date, creative_hash,
                first_seen, last_seen, raw, rank, rank_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                a["ad_id"], a["page_id"], a["page_name"], a["text"], a["title"], a["cta"], a["link"],
                a["format"], a["video_url"], a["image_url"], json.dumps(a["platforms"]),
                a["collation_count"], a["collation_id"], a["start_date"], a["end_date"],
                a["creative_hash"], first, day, json.dumps(a.get("raw"), ensure_ascii=False)[:20000],
                a.get("rank"), a.get("rank_total")))
            self.c.execute("INSERT OR REPLACE INTO snapshots VALUES (?,?,?)", (day, a["ad_id"], int(a["is_active"])))
        self.c.commit()

    def snapshot_days(self):
        return [r["day"] for r in self.q("SELECT DISTINCT day FROM snapshots ORDER BY day")]

    # --- кеш аналізу
    def get_analysis(self, h):
        r = self.q("SELECT data FROM analyses WHERE creative_hash=?", h)
        return json.loads(r[0]["data"]) if r else None

    def put_analysis(self, h, model, data, created):
        self.x("INSERT OR REPLACE INTO analyses VALUES (?,?,?,?)", h, model, created, json.dumps(data, ensure_ascii=False))


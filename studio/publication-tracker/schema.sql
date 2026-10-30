-- Brandstudio publication tracker: a separate, additive database.
-- Discovery is not revision verification. Never remove historical posts on fetch errors.
CREATE TABLE IF NOT EXISTS publication_posts (
  platform TEXT NOT NULL CHECK (platform IN ('instagram','facebook','linkedin','x')),
  source_id TEXT NOT NULL,
  permalink TEXT NOT NULL,
  caption TEXT NOT NULL DEFAULT '',
  published_at TEXT,
  group_id TEXT,
  product_id TEXT,
  match_status TEXT NOT NULL DEFAULT 'needs_review',
  match_score REAL NOT NULL DEFAULT 0,
  evidence TEXT NOT NULL,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  PRIMARY KEY (platform, source_id)
);
CREATE INDEX IF NOT EXISTS publication_group_idx ON publication_posts(group_id);
CREATE INDEX IF NOT EXISTS publication_date_idx ON publication_posts(platform,published_at DESC);
CREATE TABLE IF NOT EXISTS publication_runs (
  id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  summary_json TEXT NOT NULL DEFAULT '{}'
);

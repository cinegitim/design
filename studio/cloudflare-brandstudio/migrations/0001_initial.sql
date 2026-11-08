-- Staging-only schema; no private drafts are ever seeded by the public site.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS system_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
INSERT INTO system_meta(key, value)
VALUES ('schema_version', '1')
ON CONFLICT(key) DO NOTHING;

CREATE TABLE IF NOT EXISTS products (
  id TEXT NOT NULL PRIMARY KEY
    CHECK (length(id) BETWEEN 1 AND 100 AND id NOT GLOB '*[^a-z0-9-]*'),
  brand TEXT NOT NULL CHECK (brand = 'asyada-egitim'),
  category TEXT NOT NULL CHECK (category = 'instagram-carousel'),
  title TEXT NOT NULL,
  visibility TEXT NOT NULL DEFAULT 'private' CHECK (visibility IN ('private','public')),
  current_version INTEGER NOT NULL DEFAULT 1 CHECK (current_version >= 1),
  source_commit TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS product_versions (
  product_id TEXT NOT NULL,
  version INTEGER NOT NULL CHECK (version >= 1),
  edit_state_json TEXT NOT NULL CHECK (json_valid(edit_state_json)),
  source_sha256 TEXT NOT NULL CHECK (length(source_sha256) = 64),
  status TEXT NOT NULL CHECK (status IN ('draft','review','approved')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (product_id, version),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

CREATE TRIGGER IF NOT EXISTS immutable_versions_update
BEFORE UPDATE ON product_versions
BEGIN SELECT RAISE(ABORT, 'Versions are append only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_versions_delete
BEFORE DELETE ON product_versions
BEGIN SELECT RAISE(ABORT, 'Versions cannot be deleted'); END;

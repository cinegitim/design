-- Brandstudio D1 secondary revision archive (non-authoritative; live editor uses Durable Objects).
CREATE TABLE IF NOT EXISTS editor_revision_backups (product TEXT NOT NULL, revision TEXT NOT NULL, body TEXT NOT NULL CHECK(json_valid(body)), saved_at TEXT NOT NULL, PRIMARY KEY(product,revision));
CREATE INDEX IF NOT EXISTS idx_editor_revision_backups_product_time ON editor_revision_backups(product,saved_at);

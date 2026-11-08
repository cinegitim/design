import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / "migrations/0001_initial.sql"


class StagingSchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SQL.read_text("utf-8"))
        self.db.execute(
            "INSERT INTO products(id,brand,category,title,source_commit) VALUES(?,?,?,?,?)",
            ("example", "asyada-egitim", "instagram-carousel", "Test", "a"*40),
        )

    def tearDown(self):
        self.db.close()

    def test_empty_schema_and_version(self):
        self.assertEqual(
            self.db.execute("SELECT value FROM system_meta WHERE key = 'schema_version'").fetchone()[0], "1"
        )
        self.assertEqual(self.db.execute("SELECT count(*) FROM product_versions").fetchone()[0], 0)

    def test_append_only_and_foreign_keys(self):
        self.db.execute(
            "INSERT INTO product_versions(product_id,version,edit_state_json,source_sha256,status)"
            " VALUES(?,?,?,?,?)", ("example", 1, '{"tokens":{}}', "b"*64, "draft")
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE product_versions SET status='approved' WHERE product_id='example'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM product_versions WHERE product_id='example'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO product_versions(product_id,version,edit_state_json,source_sha256,status)"
                " VALUES(?,?,?,?,?)", ("missing", 1, "{}", "b"*64, "draft")
            )

    def test_no_duplicate_version(self):
        record = ("example", 1, "{}", "b"*64, "draft")
        stmt = ("INSERT INTO product_versions(product_id,version,edit_state_json,source_sha256,status)"
                " VALUES(?,?,?,?,?)")
        self.db.execute(stmt, record)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(stmt, record)

    def test_default_visibility_is_private(self):
        self.assertEqual(
            self.db.execute("SELECT visibility FROM products WHERE id='example'").fetchone()[0], "private"
        )


if __name__ == "__main__":
    unittest.main()

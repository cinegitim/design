"""Tests for the post-build deduplicator; no real image/render/network needed."""
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("normalize_historical_carousel_build", TOOLS / "normalize_historical_carousel_build.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class HistoricalNormalizerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.slug = "carousel-01-v2"
        self.old = "instagram/carousel-01-v2/assets/photo-1.png"
        self.new = "instagram/_shared/assets/test-image.png"
        self.page = "instagram/carousel-01-v2/source/01.html"
        self.payload = b"synthetic original bytes and metadata"
        file = self.root / "docs" / self.old
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(self.payload)
        page = self.root / "docs" / self.page
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text('<img src="../assets/photo-1.png">', encoding="utf-8")
        self.group = {
            "name": "test",
            "shared": self.new,
            "sha256": hashlib.sha256(self.payload).hexdigest(),
            "bytes": len(self.payload),
            "old": (self.old,),
            "pages": (self.page,),
        }

    def run_normalize(self, apply=False):
        return module.normalize(self.root, self.slug, groups=(self.group,), apply=apply)

    def test_dry_run_does_not_modify(self):
        before = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        result = self.run_normalize()
        after = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["status"], "DRY_RUN")

    def test_apply_preserves_original_and_source_link(self):
        self.run_normalize(apply=True)
        self.assertFalse((self.root / "docs" / self.old).exists())
        self.assertEqual((self.root / "docs" / self.new).read_bytes(), self.payload)
        self.assertIn('../../_shared/assets/test-image.png', (self.root / "docs" / self.page).read_text())

    def test_idempotent_after_apply(self):
        self.run_normalize(apply=True)
        result = self.run_normalize(apply=True)
        self.assertFalse(result["changed_anything"])
        self.assertEqual(result["original_paths_to_unpublish"], 0)

    def test_unknown_bytes_fail_closed(self):
        (self.root / "docs" / self.old).write_bytes(b"unexpected updated design")
        with self.assertRaisesRegex(ValueError, "Unexpected bytes"):
            self.run_normalize(apply=True)
        self.assertFalse((self.root / "docs" / self.new).exists())

    def test_missing_source_reference_fail_closed(self):
        (self.root / "docs" / self.page).write_text("<p>unexpected generated layout</p>")
        with self.assertRaisesRegex(ValueError, "Wrong image references"):
            self.run_normalize(apply=True)
        self.assertTrue((self.root / "docs" / self.old).exists())

    def test_invalid_slug(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            module.normalize(self.root, "unrelated-producer", groups=(self.group,), apply=True)


if __name__ == "__main__":
    unittest.main()

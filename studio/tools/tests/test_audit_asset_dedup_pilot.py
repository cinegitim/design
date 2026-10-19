"""Standalone stdlib tests for the read-only Brandstudio PNG dedup pilot."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util


HERE = Path(__file__).resolve()
SCRIPT = HERE.parents[1] / "audit_asset_dedup_pilot.py"
SPEC = importlib.util.spec_from_file_location("audit_asset_dedup_pilot", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class DedupPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in module.TARGETS:
            path = self.root / "docs" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"identical fake image bytes")
        for item, url in (
            ("instagram/carousel-01-v2/source/03.html", "../assets/photo-3.png"),
            ("instagram/carousel-01-v3/source/03.html", "../assets/photo-3.png"),
            ("instagram/carousel-02/source/03.html", "../assets/photo-3.png"),
            ("instagram/discovery-01/source/02.html", "../assets/study-worlds.png"),
        ):
            path = self.root / "docs" / item
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'<img src="{url}">', encoding="utf-8")

    def test_identical_and_reference_mapping(self):
        result = module.inspect(self.root)
        self.assertEqual(result["status"], "READ_ONLY")
        self.assertEqual(len(result["exact_site_references"]), 4)
        self.assertEqual(result["bytes_one_copy"], len(b"identical fake image bytes"))
        self.assertEqual(result["theoretical_bytes_saved_if_three_urls_removed"], 3 * len(b"identical fake image bytes"))
        self.assertFalse(result["may_delete_original_paths"])

    def test_byte_difference_blocks_migration(self):
        (self.root / "docs" / module.TARGETS[2]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "no longer byte-identical"):
            module.inspect(self.root)

    def test_missing_file_blocks_migration(self):
        (self.root / "docs" / module.TARGETS[1]).unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            module.inspect(self.root)

    def test_read_only_guarantee(self):
        before = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        module.inspect(self.root)
        after = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_absolute_url_and_external_ignored(self):
        self.assertEqual(module.resolve_site_url("instagram/a/source.html", "/design/instagram/x.png"), "instagram/x.png")
        self.assertIsNone(module.resolve_site_url("instagram/a/source.html", "https://elsewhere.test/photo-3.png"))
        self.assertIsNone(module.resolve_site_url("instagram/a/source.html", "/outside/photo-3.png"))


if __name__ == "__main__":
    unittest.main()

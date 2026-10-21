"""Standalone tests: historical PNG duplicate baseline and safe 4-to-1 migration."""
import tempfile
import unittest
from pathlib import Path
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


    def migrate_fixture(self):
        """Mimic identical Git blob relocation and rewritten historic layouts."""
        import hashlib
        shared = self.root / "docs" / module.SHARED
        shared.parent.mkdir(parents=True, exist_ok=True)
        original = (self.root / "docs" / module.TARGETS[0]).read_bytes()
        shared.write_bytes(original)
        for name in module.TARGETS:
            (self.root / "docs" / name).unlink()
        for page in module.HISTORICAL_SOURCE_PAGES:
            (self.root / "docs" / page).write_text(
                '<img src="../../_shared/assets/study-worlds-22dde98f.png">',
                encoding="utf-8",
            )
        return hashlib.sha256(original).hexdigest(), len(original)

    def test_after_migration_verifies_hash_and_links(self):
        sha, n = self.migrate_fixture()
        result = module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)
        self.assertEqual(result["status"], "PASS_AFTER_MIGRATION")
        self.assertEqual(len(result["source_pages"]), 4)
        self.assertEqual(result["png_asset_bytes_saved"], 3 * n)
        self.assertTrue(result["old_image_deep_links_intentionally_retired"])

    def test_after_migration_refuses_stale_source_url(self):
        sha, n = self.migrate_fixture()
        stale = self.root / "docs" / module.HISTORICAL_SOURCE_PAGES[2]
        stale.write_text('<img src="../assets/photo-3.png">', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale HTML/CSS image reference"):
            module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)

    def test_after_migration_refuses_unexpected_republished_copy(self):
        sha, n = self.migrate_fixture()
        old = self.root / "docs" / module.TARGETS[1]
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_bytes(b"identical fake image bytes")
        with self.assertRaisesRegex(ValueError, "Original duplicate still published"):
            module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)

    def test_after_migration_refuses_modified_canonical_bytes(self):
        sha, n = self.migrate_fixture()
        (self.root / "docs" / module.SHARED).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Shared image byte count or SHA256"):
            module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)

    def test_after_migration_refuses_missing_image_reference(self):
        sha, n = self.migrate_fixture()
        page = self.root / "docs" / module.HISTORICAL_SOURCE_PAGES[0]
        page.write_text("<body>no referenced image</body>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Expected one shared image reference"):
            module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)

    def test_after_verifier_read_only(self):
        sha, n = self.migrate_fixture()
        before = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        module.verify_migrated(self.root, expected_sha256=sha, expected_bytes=n)
        after = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        self.assertEqual(before, after)



    def create_additional_fixture(self):
        """Construct an isolated two-copy image fixture with no external dependencies."""
        import hashlib
        shared = "instagram/_shared/assets/synthetic.png"
        old = ("instagram/test-a/assets/image.png", "instagram/test-b/assets/image.png")
        page = "instagram/test-a/source/01.html"
        payload = b"unchanged synthetic PNG"
        target = self.root / "docs" / shared
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        sample = self.root / "docs" / page
        sample.parent.mkdir(parents=True, exist_ok=True)
        sample.write_text('<img src="../../_shared/assets/synthetic.png">', encoding="utf-8")
        group = {
            "shared": shared,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "old": old,
            "pages": (page,),
        }
        return group

    def test_additional_cluster_passes_and_is_read_only(self):
        group = self.create_additional_fixture()
        before = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        result = module.verify_additional_clusters(self.root, (group,))
        after = {p.as_posix(): p.read_bytes() for p in (self.root / "docs").rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["png_asset_bytes_saved"], group["bytes"])
        self.assertEqual(len(result["source_pages"]), 1)

    def test_additional_cluster_rejects_mutated_shared_bytes(self):
        group = self.create_additional_fixture()
        (self.root / "docs" / group["shared"]).write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "SHA256 or length"):
            module.verify_additional_clusters(self.root, (group,))

    def test_additional_cluster_rejects_old_duplicate(self):
        group = self.create_additional_fixture()
        path = self.root / "docs" / group["old"][0]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"old")
        with self.assertRaisesRegex(ValueError, "still present"):
            module.verify_additional_clusters(self.root, (group,))

    def test_additional_cluster_rejects_stale_source_reference(self):
        group = self.create_additional_fixture()
        old = self.root / "docs" / group["pages"][0]
        old.write_text('<img src="../../test-a/assets/image.png">', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale PNG reference"):
            module.verify_additional_clusters(self.root, (group,))

    def test_additional_cluster_rejects_missing_expected_ref(self):
        group = self.create_additional_fixture()
        (self.root / "docs" / group["pages"][0]).write_text("<p>missing shared image</p>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Incorrect per-page shared image references"):
            module.verify_additional_clusters(self.root, (group,))



if __name__ == "__main__":
    unittest.main()

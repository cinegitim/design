import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_pages import build, MAX_BYTES

class StaticExportTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.root = Path(self.t.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        (self.docs / "index.html").write_text("Brandstudio",encoding="utf-8")
        (self.docs / "visual-editor").mkdir()
        (self.docs / "visual-editor/index.html").write_text("Editor",encoding="utf-8")
        self.dest = self.root / "dist"

    def tearDown(self): self.t.cleanup()

    def test_copy_preserves_original_bytes_and_routes(self):
        r = build(self.docs,self.dest)
        self.assertTrue(r["fully_independent"])
        self.assertEqual(r["files_on_cloudflare"],2)
        self.assertEqual((self.dest / "visual-editor/index.html").read_text(),"Editor")

    def test_large_archives_are_explicit_deferred_dependencies(self):
        with (self.docs / "release.zip").open("wb") as f: f.truncate(MAX_BYTES+1)
        r = build(self.docs,self.dest)
        self.assertFalse(r["fully_independent"])
        self.assertEqual(len(r["external_archives"]),1)
        self.assertFalse((self.dest / "release.zip").exists())
        self.assertIn("https://cinegitim.github.io/design/release.zip 302",
                      (self.dest / "_redirects").read_text())

    def test_oversize_nonzip_fails(self):
        with (self.docs / "logo.svg").open("wb") as f: f.truncate(MAX_BYTES+1)
        with self.assertRaises(ValueError):
            build(self.docs,self.dest,dry_run=True)

    def test_prevents_self_copy(self):
        with self.assertRaises(ValueError):
            build(self.docs,self.docs / "dist")


    def test_catalog_is_regenerated_from_new_future_assets_at_deploy(self):
        import json
        from build_pages import design_catalog
        catalog_dir = self.docs / "visual-editor/browser"
        catalog_dir.mkdir(parents=True)
        (catalog_dir / "catalog.json").write_text("[]", encoding="utf-8")
        future = self.docs / "instagram/future-example/source"
        future.mkdir(parents=True)
        (future / "01.html").write_text('<div class="slide"></div>', encoding="utf-8")
        self.docs.joinpath("cin-egitim/rollup").mkdir(parents=True)
        self.docs.joinpath("cin-egitim/rollup/new-banner.html").write_text("banner", encoding="utf-8")
        build(self.docs,self.dest)
        published=json.loads((self.dest / "visual-editor/browser/catalog.json").read_text(encoding="utf-8"))
        self.assertTrue(any(p["id"]=="instagram-future-example" for p in published))
        self.assertTrue(any(p["id"]=="cin-egitim-rollup-new-banner" for p in published))
        self.assertGreaterEqual(len(published),2)

    def test_catalog_excludes_comparison_pages_and_internal_assets(self):
        from build_pages import design_catalog
        paths = ["docs/cin-egitim/typography-round-01/direction-a.html",
                 "docs/cin-egitim/typography-round-01/direction-b.html",
                 "docs/instagram/carousel-01-v3/source/01.html",
                 "docs/instagram/carousel-01-v3/assets/background.png",
                 "docs/instagram/carousel-01-v3/01-cover.png",
                 "docs/instagram/creative-breakout/source-originals/raw.png",
                 "docs/instagram/creative-breakout/composited/A-cover.png"]
        listed = design_catalog(paths)
        names = [x["id"] for x in listed]
        self.assertIn("carousel-01-v3", names)
        self.assertIn("asset-instagram-creative-breakout", names)
        self.assertFalse(any("typography" in x for x in names))
        self.assertFalse(any("background" in p for x in listed for p in x["pages"]))
        self.assertFalse(any("source-originals" in p for x in listed for p in x["pages"]))

if __name__ == "__main__": unittest.main()

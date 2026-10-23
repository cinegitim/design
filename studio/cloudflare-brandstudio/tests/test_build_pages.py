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

if __name__ == "__main__": unittest.main()

"""Static Pages must never pretend that a public website can save locally."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class PagesEntryTests(unittest.TestCase):
    def test_public_editor_is_explicit_local_only(self):
        html = (ROOT / "docs/visual-editor/index.html").read_text(encoding="utf-8")
        self.assertIn("Tarayıcı editörü yalnızca tarayıcıya", html)
        self.assertIn("http://127.0.0.1:8765/", html)
        self.assertIn("encodeURIComponent(product)", html)
        self.assertNotIn("api.github.com/repos", html)
        self.assertNotIn('method:"POST"', html)

    def test_brand_page_links_are_per_product_and_optional(self):
        html = (ROOT / "docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        self.assertIn("Visual Editor ile düzenle", html)
        self.assertIn("brand=asyada-egitim", html)
        self.assertIn("category=instagram-carousel", html)
        self.assertIn("MutationObserver", html)
        self.assertIn(".visual-product[hidden]{display:none!important}", html)

    def test_studio_navigation(self):
        self.assertIn('href="visual-editor/"', (ROOT / "docs/index.html").read_text(encoding="utf-8"))
        self.assertIn('href="../visual-editor/"', (ROOT / "docs/instagram/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

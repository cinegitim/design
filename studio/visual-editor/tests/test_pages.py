"""Static Pages must never pretend that a public website can save locally."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class PagesEntryTests(unittest.TestCase):
    def test_public_editor_opens_browser_only(self):
        html = (ROOT / "docs/visual-editor/index.html").read_text(encoding="utf-8")
        self.assertIn("Tarayıcı editörüne geç", html)
        self.assertNotIn("http://127.0.0.1:8765/", html)
        self.assertNotIn("open-editor", html)
        self.assertIn("location.replace(target.href)", html)
        self.assertIn("target.searchParams.set('product',product)", html)
        self.assertNotIn("api.github.com/repos", html)
        self.assertNotIn('method:"POST"', html)

    def test_brand_page_links_are_per_product_and_optional(self):
        html = (ROOT / "docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        self.assertIn("Visual Editor ile düzenle", html)
        self.assertIn("../../visual-editor/browser/?product=", html)
        self.assertNotIn("category=instagram-carousel&product=", html)
        self.assertIn("MutationObserver", html)
        self.assertIn(".visual-product[hidden]{display:none!important}", html)

    def test_studio_navigation(self):
        self.assertIn('href="visual-editor/"', (ROOT / "docs/index.html").read_text(encoding="utf-8"))
        self.assertIn('href="../visual-editor/browser/"', (ROOT / "docs/instagram/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

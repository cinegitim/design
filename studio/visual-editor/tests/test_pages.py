"""Static Pages must never pretend that a public website can save locally."""
import unittest
import json
import re
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


    def test_every_carousel_card_opens_its_exact_published_source_version(self):
        page = (ROOT / "docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        catalog = json.loads((ROOT / "docs/visual-editor/browser/catalog.json").read_text(encoding="utf-8"))
        by_id = {p["id"]: p for p in catalog}
        carousel_cards = []
        for tile in re.finditer(r'<a class="tile" ([^>]+)>(.*?)</a>', page, re.DOTALL):
            attrs, contents = tile.groups()
            if '<span class="category">Karusel</span>' not in contents:
                continue
            href = re.search(r'href="([^"]+)"', attrs)
            product = re.search(r'data-editor-product="([^"]+)"', attrs)
            self.assertIsNotNone(href, "Carousel must link to its real gallery")
            self.assertIsNotNone(product, "Carousel must declare its exact editor product ID")
            href, product = href.group(1), product.group(1)
            self.assertIn(product, by_id, "Editor link must resolve to a published source")
            prefix = href.removeprefix("../../").rstrip("/") + "/"
            self.assertTrue(any(source.startswith(prefix+"source/") or source.startswith(prefix+"editable/")
                                for source in by_id[product]["pages"]),
                            f"{product} does not correspond to gallery at {href}")
            carousel_cards.append((href, product))
        self.assertEqual(len(carousel_cards), 5)
        self.assertEqual(len(set(p for _, p in carousel_cards)), len(carousel_cards))
        self.assertIn(('../../instagram/rotani-sec-tokyo-seoul-001/v3/',
                       'instagram-rotani-sec-tokyo-seoul-001-v3'), carousel_cards)
        self.assertIn(('../../instagram/tsinghua-atlas-2027/v2/',
                       'instagram-tsinghua-atlas-2027-v2'), carousel_cards)
        self.assertIn("const product=tile.dataset.editorProduct", page)
        self.assertNotIn("const product=m[1]", page)

    def test_studio_navigation(self):
        self.assertIn('href="visual-editor/"', (ROOT / "docs/index.html").read_text(encoding="utf-8"))
        self.assertIn('href="../visual-editor/browser/"', (ROOT / "docs/instagram/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

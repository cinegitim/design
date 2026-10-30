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
        self.assertIn("function card(g,posts)", html)
        self.assertIn("tile.href=url", html)
        self.assertIn("el('a','quick-action edit')", html)
        self.assertIn("el('a','quick-action '+icon)", html)
        self.assertIn("editor.setAttribute('aria-label'", html)
        self.assertIn("proof.setAttribute('aria-label'", html)
        self.assertIn("../../visual-editor/browser/?product=", html)
        self.assertIn("for(const platform of Object.keys(names))", html)
        self.assertNotIn("visual-editor-action", html)
        self.assertNotIn("instagram-proof-link", html)
        self.assertNotIn("MutationObserver", html)

    def test_all_carousel_families_have_one_default_version_and_accessible_actions(self):
        page = (ROOT / "docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        config = json.loads((ROOT / "docs/visual-editor/browser/product-groups.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / "docs/visual-editor/browser/catalog.json").read_text(encoding="utf-8"))
        by_id = {p["id"]: p for p in catalog}
        groups = [g for g in config["groups"] if g["brand"] == "asyada-egitim"
                  and g.get("categoryPath", [None, None])[1] == "Karuseller"]
        self.assertEqual(len(groups), 13)
        self.assertEqual(len({g["id"] for g in groups}), 13)
        for group in groups:
            default_id = group["defaultId"]
            self.assertIn(default_id, by_id, f"{group['id']} has no matching source")
            self.assertTrue(by_id[default_id]["pages"])
            self.assertIn(default_id, [v["id"] for v in group["versions"]])
            self.assertIn("const id=g.defaultId||g.currentId", page)
        published = next(g for g in groups if g["id"] == "instagram-carousel-01")
        self.assertEqual(published["defaultId"], "instagram-carousel-01-v2")
        self.assertEqual(published["publishedVersionId"], "instagram-carousel-01-v2")
        self.assertEqual(published["currentId"], "carousel-01-v3")
        self.assertTrue(all(source.startswith("instagram/carousel-01-v2/source/")
                            for source in by_id[published["defaultId"]]["pages"]))
        self.assertIn("'instagram-carousel-01': {v:'../../instagram/carousel-01-v2/'", page)
        self.assertIn("wrap.append(actions)", page)
        self.assertIn("tile.href='logos-and-covers/'", page)

    def test_studio_navigation(self):
        self.assertIn('href="visual-editor/"', (ROOT / "docs/index.html").read_text(encoding="utf-8"))
        self.assertIn('href="../visual-editor/browser/"', (ROOT / "docs/instagram/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

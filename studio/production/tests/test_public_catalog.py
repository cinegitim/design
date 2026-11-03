"""Tests for Brandstudio's read-only system hub and source-of-truth snapshots."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "studio" / "production"))
from public_catalog import build_public_catalog, render_json  # noqa: E402


class PublicCatalogTests(unittest.TestCase):
    def setUp(self):
        self.data = build_public_catalog(ROOT)

    def test_all_categories_visible_without_inventing_approved_styles(self):
        routes = json.loads((ROOT / "studio/production/routes.json").read_text())
        self.assertEqual({x["id"] for x in self.data["categories"]}, set(routes["categories"]))
        self.assertEqual(len(self.data["categories"]), 6)
        self.assertEqual(sum(c["style_count"] for c in self.data["categories"]), 1)
        self.assertEqual(self.data["styles"][0]["status"], "review-only")
        self.assertFalse(self.data["styles"][0]["production_approved"])

    def test_executor_and_llm_family_are_different_decision_axes(self):
        routes = json.loads((ROOT / "studio/production/routes.json").read_text())
        self.assertEqual(
            {x["id"] for x in self.data["executors"]},
            {x["id"] for x in routes["profiles"]}
        )
        ids = {x["id"] for x in self.data["model_families"]}
        self.assertTrue({"gpt", "gemini", "claude", "glm", "qwen"}.issubset(ids))
        self.assertTrue(all(x["status"] == "advisory" for x in self.data["model_families"]))
        self.assertTrue(all(x["capabilities_verified"] is False for x in self.data["model_families"]))

    def test_model_guidance_cannot_override_brand_or_publish(self):
        for profile in self.data["model_families"]:
            self.assertIn("code", profile["emphasis"])
            self.assertIn("image", profile["emphasis"])
            self.assertNotIn("auto_publish", profile)
        self.assertEqual(self.data["workflow"]["github_version"], "pr-required")
        self.assertEqual(self.data["workflow"]["visual_editor_versions"], "cloud-drafts")
        self.assertEqual(self.data["workflow"]["social_proof"], "platform-evidence-required")

    def test_generated_json_is_in_sync_with_canonical_registry(self):
        expected = render_json(self.data)
        actual = (ROOT / "docs/system/catalog.json").read_text(encoding="utf-8")
        self.assertEqual(expected, actual)
        self.assertEqual(self.data["brand_identity"]["font"], "Jost")

    def test_ui_provides_real_navigation_and_honest_generation_brief(self):
        page = (ROOT / "docs/system/index.html").read_text(encoding="utf-8")
        code = (ROOT / "docs/system/app.js").read_text(encoding="utf-8")
        root = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        brand = (ROOT / "docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        for expected in ('id="library"', 'id="production"', 'id="pipeline"',
                         'id="category-picker"', 'id="style-picker"',
                         'id="preset-picker"', 'id="executor-picker"',
                         'id="model-picker"', 'id="copy-brief"'):
            self.assertIn(expected, page)
        self.assertIn('fetch("catalog.json"', code)
        self.assertIn('github.status', code)
        self.assertIn('not-submitted', code)
        self.assertIn('system/', root)
        self.assertIn('../../system/', brand)

if __name__ == "__main__":
    unittest.main()

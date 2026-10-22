"""Read-only deterministic routing tests. Run: python3 -m unittest discover -s studio/production/tests -v"""
import json
import sys
import unittest
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
ROOT = PRODUCTION.parents[1]
sys.path.insert(0, str(PRODUCTION))
from router import plan  # noqa: E402

CONFIG = json.loads((PRODUCTION / "routes.json").read_text(encoding="utf-8"))


class RouterTests(unittest.TestCase):
    def route(self, **kw):
        defaults = dict(
            root=ROOT, config=CONFIG, executor="codex",
            brand="asyada-egitim", category="instagram-carousel",
            capabilities=set(),
        )
        defaults.update(kw)
        return plan(**defaults)

    def test_full_codex_route(self):
        result = self.route(capabilities={"filesystem", "terminal"})
        self.assertEqual(result["route"]["id"], "codex-code-v1")
        self.assertEqual(result["mode"], "read-only-dry-run")
        self.assertFalse(result["telemetry"]["collected"])

    def test_antigravity_and_opencode(self):
        for executor, route in (
            ("antigravity", "antigravity-agent-v1"),
            ("opencode", "opencode-code-v1"),
        ):
            with self.subTest(executor=executor):
                self.assertEqual(
                    self.route(executor=executor, capabilities={"filesystem", "terminal"})["route"]["id"],
                    route,
                )

    def test_high_chat_and_default_chat_have_distinct_routes(self):
        high = self.route(executor="chatgpt-chat",
                          capabilities={"github-read"}, requested_effort="high")
        self.assertEqual(high["route"]["id"], "chatgpt-high-connected-v1")
        self.assertFalse(high["runtime"]["effort_verified"])
        self.assertIn("studio/production/chatgpt/EXECUTION.md", high["load"])
        default = self.route(executor="chatgpt-chat", capabilities={"github-read"})
        self.assertEqual(default["route"]["id"], "chatgpt-connected-v1")

    def test_carousel_always_uses_editable_source_pipeline(self):
        for executor, capabilities in (
            ("chatgpt-chat", {"github-read", "image-generation"}),
            ("chatgpt-chat", {"image-generation"}),
            ("chatgpt-work", {"github-read"}),
            ("codex", {"filesystem", "terminal"}),
            ("opencode", {"filesystem", "terminal"}),
        ):
            with self.subTest(executor=executor, capabilities=capabilities):
                result = self.route(executor=executor, capabilities=capabilities)
                policy = result["production_policy"]
                self.assertEqual(policy["primary_method"], "editable-html-css-svg")
                self.assertEqual(policy["render_method"], "actual-browser-exact-pixels")
                self.assertEqual(policy["canonical_branding"], "complete-manifest-listed-svg-composite")
                self.assertIn("isolated", policy["image_generation"])
                self.assertEqual(policy["full_slide_image_only"], "explicit-user-experimental-opt-in")
                self.assertTrue(policy["reuse_existing_brand_recipes"])
                self.assertIn("rendered-slide-png", policy["required_deliverables"])

    def test_old_carousel_and_approval_sources_still_exist(self):
        self.assertTrue((ROOT / "brands/asyada-egitim/applications/instagram-carousel-01-v3/build.py").is_file())
        self.assertTrue((ROOT / "brands/asyada-egitim/assets/lockups/canonical-lockups.json").is_file())
        self.assertTrue((ROOT / ".opencode/skills/brand-studio/SKILL.md").is_file())

    def test_chat_effort_cannot_be_passed_to_codex(self):
        with self.assertRaises(ValueError):
            self.route(executor="codex", requested_effort="high")

    def test_missing_capability_falls_back(self):
        result = self.route(executor="opencode", capabilities={"filesystem"})
        self.assertEqual(result["route"]["id"], "generic-limited-v1")
        self.assertTrue(result["warnings"])

    def test_normal_chat_image_only_when_available(self):
        result = self.route(executor="chatgpt-chat", capabilities={"image-generation"})
        self.assertEqual(result["route"]["id"], "chat-image-v1")
        self.assertEqual(result["route"]["strategy"], "native-raster-layer-only")
        self.assertTrue(any("not a complete" in w for w in result["warnings"]))
        result = self.route(executor="chatgpt-chat", capabilities={"image-generation"}, category="print-catalog")
        self.assertEqual(result["route"]["id"], "generic-limited-v1")

    def test_verified_vs_reported_model(self):
        reported = self.route(model_id="example-model")
        self.assertIsNone(reported["runtime"]["model_verified"])
        verified = self.route(model_id="example-model", model_verified=True)
        self.assertEqual(verified["runtime"]["model_verified"], "example-model")
        with self.assertRaises(ValueError):
            self.route(model_verified=True)

    def test_unknown_category_or_brand_rejected(self):
        with self.assertRaises(ValueError):
            self.route(category="unknown")
        with self.assertRaises(ValueError):
            self.route(brand="../other")
        with self.assertRaises(ValueError):
            self.route(brand="not-a-real-brand")

    def test_new_identity_without_metadata_enters_intake(self):
        result = self.route(
            brand="new-safe-brand", category="new-identity",
            capabilities={"filesystem", "terminal"},
        )
        self.assertEqual(result["route"]["id"], "codex-code-v1")
        self.assertNotIn("brands/new-safe-brand/brand.json", result["load"])
        self.assertTrue(any("scaffolding" in w for w in result["warnings"]))

    def test_existing_identity_is_explicit(self):
        r = self.route()
        self.assertIn("brands/asyada-egitim/brand.json", r["load"])
        self.assertNotIn("brands/asya-egitim/brand.json", r["load"])


if __name__ == "__main__":
    unittest.main()

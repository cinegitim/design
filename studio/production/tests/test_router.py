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

    def test_missing_capability_falls_back(self):
        result = self.route(executor="opencode", capabilities={"filesystem"})
        self.assertEqual(result["route"]["id"], "generic-limited-v1")
        self.assertTrue(result["warnings"])

    def test_normal_chat_image_only_when_available(self):
        result = self.route(executor="chatgpt-chat", capabilities={"image-generation"})
        self.assertEqual(result["route"]["id"], "chat-image-v1")
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

    def test_existing_identity_is_explicit(self):
        r = self.route()
        self.assertIn("brands/asyada-egitim/brand.json", r["load"])
        self.assertNotIn("brands/asya-egitim/brand.json", r["load"])


if __name__ == "__main__":
    unittest.main()

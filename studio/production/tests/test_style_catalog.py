"""Style selection contract; no art generation, no model calls, no writes."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
ROOT = PRODUCTION.parents[1]
sys.path.insert(0, str(PRODUCTION))

from router import plan  # noqa: E402
from style_catalog import list_styles, resolve_style  # noqa: E402

CONFIG = json.loads((PRODUCTION / "routes.json").read_text(encoding="utf-8"))
BRAND = "asyada-egitim"
CATEGORY = "instagram-carousel"


class StyleCatalogTests(unittest.TestCase):
    def test_exact_brand_category_registry(self):
        items = list_styles(root=ROOT, brand=BRAND, category=CATEGORY)
        self.assertEqual([s["style_id"] for s in items], ["editorial-campaign"])
        self.assertEqual(items[0]["status"], "review-only")
        self.assertEqual(len(items[0]["preset_ids"]), 4)
        self.assertEqual(list_styles(root=ROOT, brand=BRAND, category="social-post"), [])

    def test_default_preset_and_exact_family(self):
        s = resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                          style_id="editorial-campaign")
        self.assertEqual(s["style_id"], "editorial-campaign")
        self.assertEqual(s["preset_id"], "institutional-paper")
        self.assertEqual(s["variation"]["color_mode"], "paper-dominant")
        self.assertFalse(s["approved"])
        self.assertIn("editorial-campaign/style.json", s["definition_path"])

    def test_four_presets_one_style_not_four_styles(self):
        family = set()
        variations = []
        for preset in ("institutional-paper", "campaign-dynamic",
                       "photo-editorial", "ink-accent"):
            s = resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                              style_id="editorial-campaign", preset_id=preset)
            family.add(s["style_id"])
            variations.append(tuple(sorted(s["variation"].items())))
        self.assertEqual(family, {"editorial-campaign"})
        self.assertEqual(len(set(variations)), 4)

    def test_override_only_whitelisted_axes_and_values(self):
        s = resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                          style_id="editorial-campaign",
                          preset_id="institutional-paper",
                          variation_overrides={"layout_rhythm": "dynamic"})
        self.assertEqual(s["variation"]["layout_rhythm"], "dynamic")
        self.assertEqual(s["variation"]["color_mode"], "paper-dominant")
        self.assertEqual(s["overrides"], {"layout_rhythm": "dynamic"})
        for overrides in ({"layout_rhythm": "anything"}, {"logo_geometry": "new"},
                          {"color_mode": "#ff00ff"}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                              style_id="editorial-campaign", variation_overrides=overrides)

    def test_invalid_or_cross_brand_style_rejected(self):
        for brand, category, style in (
            ("asya-egitim", CATEGORY, "editorial-campaign"),
            (BRAND, "social-post", "editorial-campaign"),
            (BRAND, CATEGORY, "../editorial-campaign"),
            (BRAND, CATEGORY, "not-a-real-style"),
        ):
            with self.subTest(brand=brand, category=category, style=style):
                with self.assertRaises(ValueError):
                    resolve_style(root=ROOT, brand=brand, category=category, style_id=style)
        with self.assertRaises(ValueError):
            resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                          preset_id="institutional-paper")
        with self.assertRaises(ValueError):
            resolve_style(root=ROOT, brand=BRAND, category=CATEGORY,
                          style_id="editorial-campaign", preset_id="unknown")

    def test_editorial_visual_quality_and_combined_logo_gates(self):
        spec_path = ROOT / "brands/asyada-egitim/styles/instagram-carousel/editorial-campaign/style.json"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        policy = spec["preview_quality_contract"]
        identity = policy["identity_gate"]
        layout = policy["density_and_layout_gate"]
        self.assertTrue(identity["composite_logo_required"])
        self.assertTrue(identity["reject_seal_only_for_carousel"])
        self.assertTrue(identity["reject_retypeset_brand_name"])
        self.assertTrue(identity["reject_missing_or_unverified_lockup"])
        self.assertTrue(identity["manifest_sha256_required"])
        self.assertTrue(identity["minimum_width_enforce_from_canonical_manifest"])
        self.assertEqual(len(identity["allowed_approved_lockups"]), 4)
        self.assertTrue(layout["no_fixed_repeated_footer"])
        self.assertTrue(layout["prohibit_auto_approval"])
        self.assertGreaterEqual(len(policy["reference_instagram_posts"]), 3)

    def test_style_optional_and_route_remains_unchanged(self):
        kwargs = dict(root=ROOT, config=CONFIG, executor="chatgpt-chat",
                      brand=BRAND, category=CATEGORY, capabilities={"github-read"})
        base = plan(**kwargs)
        selected = plan(**kwargs, style_id="editorial-campaign",
                        preset_id="photo-editorial",
                        variation_overrides={"color_mode": "paper-red-balanced"})
        self.assertIsNone(base["style"])
        self.assertEqual(base["route"]["id"], selected["route"]["id"])
        self.assertEqual(selected["style"]["variation"]["color_mode"],
                         "paper-red-balanced")
        self.assertIn(selected["style"]["definition_path"], selected["load"])
        self.assertNotIn("brands/asya-egitim/brand.json", selected["load"])

    def test_manifest_scope_validation_does_not_allow_forgery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = ROOT / "brands" / BRAND / "styles" / CATEGORY / "editorial-campaign" / "style.json"
            x = json.loads(src.read_text(encoding="utf-8"))
            x["brand"] = "asya-egitim"
            dst = root / "brands" / BRAND / "styles" / CATEGORY / "editorial-campaign" / "style.json"
            dst.parent.mkdir(parents=True)
            dst.write_text(json.dumps(x), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scope mismatch"):
                resolve_style(root=root, brand=BRAND, category=CATEGORY,
                              style_id="editorial-campaign")


if __name__ == "__main__":
    unittest.main()

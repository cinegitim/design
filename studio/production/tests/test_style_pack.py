"""Cross-agent Brandstudio portable style contract: no model and no publishing."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "studio" / "production"
sys.path.insert(0, str(P))
from style_pack import build_style_pack, verify_style_pack  # noqa: E402

BRAND = "asyada-egitim"
CAT = "instagram-carousel"
STYLE = "editorial-campaign"


class StylePackTests(unittest.TestCase):
    def pack(self, **kw):
        options = {"brand": BRAND, "category": CAT, "style_id": STYLE, **kw}
        return build_style_pack(root=ROOT, **options)

    def test_identical_contract_across_two_agents(self):
        first = self.pack(preset_id="institutional-paper", executor="opencode")
        second = self.pack(preset_id="institutional-paper", executor="chatgpt-work")
        self.assertEqual(first, second)
        self.assertEqual(first["contract_version"], 1)
        self.assertEqual(first["style"]["status"], "review-only")
        self.assertFalse(first["style"]["production_approved"])
        self.assertEqual(first["identity"]["lockup_id"], "H-02/dark")
        self.assertEqual(first["identity"]["seal_id"], "V-01")
        self.assertEqual(first["typography"]["body_family"], "Jost")
        self.assertEqual(first["palette"]["paper"], "#F7F3E9")
        self.assertEqual(first["palette"]["ink"], "#1D2027")
        self.assertEqual(first["palette"]["red"], "#BD2120")
        self.assertTrue(verify_style_pack(first, root=ROOT))

    def test_style_overrides_preserve_identity_but_change_composition(self):
        a = self.pack(preset_id="institutional-paper")
        b = self.pack(preset_id="campaign-dynamic",
                      variation_overrides={"photo_density": "high"})
        self.assertEqual(a["identity"], b["identity"])
        self.assertEqual(a["palette"], b["palette"])
        self.assertEqual(a["typography"], b["typography"])
        self.assertNotEqual(a["style"]["variation"], b["style"]["variation"])
        self.assertTrue(verify_style_pack(b, root=ROOT))

    def test_only_approved_manifest_lockups_and_no_retired_d04(self):
        a = self.pack(lockup_id="P-01/light")
        self.assertEqual(a["identity"]["lockup_id"], "P-01/light")
        self.assertTrue(verify_style_pack(a, root=ROOT))
        for bad in ("D-04/dark", "C-03", "new-logo", "V-01"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.pack(lockup_id=bad)

    def test_detects_tampered_color_font_logo_and_style(self):
        original = self.pack()
        edits = [
            ("palette", "red", "#ff00ff"),
            ("typography", "body_family", "Arial"),
            ("identity", "lockup_sha256", "0" * 64),
            ("identity", "lockup_id", "D-04/dark"),
            ("style", "preset_id", "unknown"),
        ]
        for key, subkey, value in edits:
            with self.subTest(field=subkey), self.assertRaises(ValueError):
                fake = copy.deepcopy(original)
                fake[key][subkey] = value
                verify_style_pack(fake, root=ROOT)

    def test_detects_modified_canonical_svg_file_bytes(self):
        original = self.pack()
        with tempfile.TemporaryDirectory() as tmp:
            import shutil
            dst = Path(tmp)
            for path in (original["identity"]["lockup_path"],
                         original["identity"]["seal_path"],
                         original["style"]["definition_path"],
                         "brands/asyada-egitim/brand.json",
                         "brands/asyada-egitim/assets/lockups/canonical-lockups.json"):
                full = dst / path
                full.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, full)
            self.assertTrue(verify_style_pack(original, root=dst))
            (dst / original["identity"]["lockup_path"]).write_text("<svg/>")
            with self.assertRaises(ValueError):
                verify_style_pack(original, root=dst)

    def test_identity_lockups_are_not_declared_approved_style(self):
        item = self.pack()
        self.assertTrue(item["identity"]["canonical_approved"])
        self.assertFalse(item["style"]["production_approved"])
        self.assertEqual(item["status"], "review-only")
        self.assertNotIn("D-04", json.dumps(item))

    def test_build_rejects_unknown_style_and_variation(self):
        for bad in ({"style_id": "unregistered"}, {"preset_id": "wrong"},
                    {"variation_overrides": {"color_mode": "pink"}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.pack(**bad)


if __name__ == "__main__":
    unittest.main()

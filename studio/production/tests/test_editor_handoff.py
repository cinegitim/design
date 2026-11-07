"""Pure local verification of the Visual Editor agent-neutral style handoff."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "studio" / "production"))
from editor_handoff import HandoffError, verify_brief  # noqa: E402
from style_pack import build_style_pack  # noqa: E402

INSTRUCTION = (
    "Use the exact canonical style pack and SVGs; create a separate GitHub branch and PR; "
    "verify all brand and render gates. Do not infer creative or social approval."
)

def fixture():
    pack = build_style_pack(root=ROOT, brand="asyada-egitim", category="instagram-carousel",
                            style_id="editorial-campaign", preset_id="institutional-paper")
    path = ROOT / pack["sources"]["style_definition"]
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    selected = {
        "schema": 1, "brand": pack["brand"], "category": pack["category"],
        "style_id": pack["style"]["id"],
        "style_version": pack["style"]["version"],
        "style_source_blob_sha": blob,
        "preset_id": pack["style"]["preset_id"],
        "lockup_id": pack["identity"]["lockup_id"],
        "lockup_sha256": pack["identity"]["lockup_sha256"],
        "seal_sha256": pack["identity"]["seal_sha256"],
        "approval_status": pack["style"]["status"],
        "font_family": pack["typography"]["body_family"],
        "palette": pack["palette"],
        "variation": pack["style"]["variation"],
        "overrides": pack["style"]["overrides"],
        "source_path": pack["sources"]["style_definition"]
    }
    return {
        "schema": 1, "origin": "brandstudio-visual-editor",
        "repository": "cinegitim/design",
        "product": "instagram-kaist-tech-track-2027-001-v2",
        "editor_cloud_version": "v2", "selection": selected,
        "github": {"status": "not-submitted", "branch": None, "commit": None, "pr": None},
        "approval": {"creative": "pending", "social_published": False},
        "instruction": INSTRUCTION
    }


class HandoffTests(unittest.TestCase):
    def test_real_canonical_pack_is_the_same_for_all_executors(self):
        brief = fixture()
        a = verify_brief(brief, ROOT)
        b = verify_brief(brief, ROOT)
        self.assertEqual(a, b)
        self.assertEqual(a["style_pack"]["identity"]["lockup_id"], "H-02/dark")
        self.assertEqual(a["style_pack"]["typography"]["body_family"], "Jost")
        self.assertFalse(a["review"]["style_approved"])
        self.assertFalse(a["review"]["social_published"])
        self.assertEqual(a["github"]["status"], "not-submitted")

    def test_invalid_style_logo_font_color_hash_and_approval_rejected(self):
        cases = [
            ("selection", "style_source_blob_sha", "0" * 40),
            ("selection", "lockup_sha256", "0" * 64),
            ("selection", "seal_sha256", "0" * 64),
            ("selection", "lockup_id", "D-04/dark"),
            ("selection", "font_family", "Arial"),
            ("selection", "approval_status", "approved"),
            ("selection", "style_version", "999"),
            ("selection", "source_path", "../untrusted/style.json"),
            ("approval", "creative", "approved"),
            ("github", "status", "merged"),
            ("selection", "preset_id", "made-up"),
        ]
        for field, key, value in cases:
            with self.subTest(field=field, key=key):
                item = copy.deepcopy(fixture())
                item[field][key] = value
                with self.assertRaises((HandoffError, ValueError, KeyError)):
                    verify_brief(item, ROOT)
        item = fixture()
        item["selection"]["palette"]["red"] = "#abcdef"
        with self.assertRaises(HandoffError):
            verify_brief(item, ROOT)
        item = fixture()
        item["selection"]["variation"]["color_mode"] = "unknown"
        with self.assertRaises(ValueError):
            verify_brief(item, ROOT)

    def test_bad_product_cloud_version_and_unexpected_fields_rejected(self):
        for key, value in [("product", "../bad"), ("editor_cloud_version", "v99"),
                           ("repository", "evil/repo"), ("origin", "fake-editor")]:
            with self.subTest(key=key):
                item = fixture()
                item[key] = value
                with self.assertRaises(HandoffError):
                    verify_brief(item, ROOT)
        item = fixture()
        item["selection"]["unknown"] = "hijack"
        with self.assertRaises(HandoffError):
            verify_brief(item, ROOT)

    def test_public_cli_produces_pure_json_without_writing_any_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "production-brief.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "studio/production/editor_handoff.py"),
                 "--brief", str(source), "--root", str(ROOT)],
                capture_output=True, text=True, timeout=20
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["result"], "verified-style-contract")
            self.assertEqual(result["product"], fixture()["product"])
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()),
                             ["production-brief.json"])

    def test_cli_rejects_forged_approval(self):
        item = fixture()
        item["approval"]["social_published"] = True
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "production-brief.json"
            src.write_text(json.dumps(item), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "studio/production/editor_handoff.py"),
                 "--brief", str(src)], capture_output=True, text=True, timeout=20
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("cannot approve", completed.stderr)


if __name__ == "__main__":
    unittest.main()

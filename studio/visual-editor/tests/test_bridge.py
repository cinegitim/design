import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "studio" / "visual-editor"))
from bridge import BridgeError, approved_logo, run, slug, validate_output


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.repo = root / "repo"
        self.home = root / "companion"
        self.output = root / "prompt-output"
        (self.repo / "brands/asyada-egitim/assets/lockups").mkdir(parents=True)
        logo = self.repo / "brands/asyada-egitim/assets/lockups/p-01-primary-stacked-light.svg"
        logo.write_text("<svg>exact fixture</svg>", encoding="utf-8")
        expected = hashlib.sha256(logo.read_bytes()).hexdigest()
        (self.repo / "brands/asyada-egitim/assets/lockups/canonical-lockups.json").write_text(json.dumps({"records": [{"id": "P-01/light", "path": "brands/asyada-egitim/assets/lockups/p-01-primary-stacked-light.svg", "hash": expected}]}))
        (self.home / "app").mkdir(parents=True)
        (self.home / "app/manage.py").write_text("# companion marker\n")
        (self.output / "source").mkdir(parents=True)
        (self.output / "slides").mkdir(parents=True)
        (self.output / "source/style.css").write_text(".slide{}")
        (self.output / "source/01.html").write_text('<main class="slide">hello</main>')
        (self.output / "slides/01.png").write_bytes(b"example placeholder")
        self.kwargs = dict(repo=self.repo, editor_home=self.home, output=self.output,
                           product="first-carousel", brand="asyada-egitim",
                           category="instagram-carousel", style="editorial-campaign", logo_id="P-01/light")

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_never_writes(self):
        result = run(**self.kwargs, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["logo_id"], "P-01/light")
        self.assertFalse((self.home / "products").exists())

    def test_sibling_brand_and_bad_slug(self):
        with self.assertRaises(BridgeError):
            run(**{**self.kwargs, "brand": "asya-egitim"}, dry_run=True)
        for bad in ("../foo", "UPPER", "a/b", ""):
            with self.assertRaises(BridgeError):
                slug(bad)

    def test_logo_mismatch_blocks_registration(self):
        logo = self.repo / "brands/asyada-egitim/assets/lockups/p-01-primary-stacked-light.svg"
        logo.write_text("tampered")
        with self.assertRaisesRegex(BridgeError, "mismatch"):
            run(**self.kwargs, dry_run=True)

    def test_existing_product_not_overwritten(self):
        dest = self.home / "products/instagram-carousel/first-carousel"
        dest.mkdir(parents=True)
        with self.assertRaisesRegex(BridgeError, "already registered"):
            run(**self.kwargs, dry_run=True)

    def test_requires_actual_render_folder(self):
        (self.output / "slides/01.png").unlink()
        with self.assertRaisesRegex(BridgeError, "Missing actual rendered"):
            validate_output(self.output)

    def test_refuses_unsupported_logo(self):
        with self.assertRaisesRegex(BridgeError, "Unknown canonical"):
            run(**{**self.kwargs, "logo_id": "D-04/light"}, dry_run=True)


if __name__ == "__main__":
    unittest.main()

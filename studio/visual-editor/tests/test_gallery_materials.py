"""All active design detail pages retain artwork first and secondary evidence in drawers."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "docs/instagram/brandstudio-page.js"
CATALOGUE = ROOT / "docs/visual-editor/browser/product-groups.json"
TSINGHUA = ROOT / "docs/instagram/tsinghua-atlas-2027/v2/index.html"


class ProductMaterialDrawers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf8")
        cls.catalogue = json.loads(CATALOGUE.read_text(encoding="utf8"))

    def test_shared_browser_code_syntax(self):
        if not shutil.which("node"):
            self.skipTest("Node not available")
        result = subprocess.run(["node", "--check", str(SCRIPT)], capture_output=True, text=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_gallery_has_four_semantic_drawers_after_the_actual_artwork(self):
        s = self.source
        for text in ("Önizlemeler", "Sürüm geçmişi", "Üretim belgeleri", "Kaynaklar ve indirmeler"):
            self.assertIn(text, s)
        self.assertIn('document.createElement("details")', s)
        self.assertIn('document.createElement("summary")', s)
        self.assertIn('if(key==="preview")detail.open=true', s)
        self.assertIn('main.insertAdjacentElement("afterend",section)', s)
        self.assertIn('document.querySelectorAll("main a[href]")', s)
        self.assertIn('document.querySelectorAll("header nav.links, header .links")', s)
        self.assertIn('document.querySelectorAll("main > .files,main > .resources")', s)
        self.assertIn('node.tagName==="LI"', s)
        self.assertIn('li.appendChild(a)', s)
        self.assertIn('a.querySelector("img,picture,svg,canvas")', s)
        self.assertIn('sec.querySelector("h2,h3")', s)
        self.assertIn('dataset.bsResourceOrganized', s)
        self.assertIn("document.querySelector('.bs-support')", s.replace('"', "'"))

    def test_tsinghua_keeps_artwork_and_all_original_resources(self):
        html = TSINGHUA.read_text(encoding="utf8")
        self.assertIn('data-product-id="instagram-tsinghua-atlas-2027-v2"', html)
        self.assertEqual(len(re.findall(r'<article class="card">', html)), 7)
        for index in range(1, 8):
            self.assertIn(f'png/{index:02d}.png', html)
            self.assertIn(f'source/{index:02d}.svg', html)
            self.assertIn(f'source/{index:02d}.html', html)
        for resource in ("mobile-preview.html", "mobile-324-contact-sheet.png",
                         "contact-sheet.png", "feed-cover-preview.html", "revision-comparison.html",
                         "factual-source-report.md", "quality-review.md",
                         "caption-and-credits.md", "package/tsinghua-atlas-2027-v2.zip",
                         "../index.html#v1"):
            self.assertIn(resource, html)
        self.assertIn("Tsinghua Atlası 2027 · V2", html)
        self.assertIn("1080 × 1350", html)
        self.assertNotIn("Yedi slaytlık yeni düzen:", html)

    def test_all_linked_editable_product_galleries_share_the_same_component(self):
        entries = []
        for folder in (ROOT / "docs/instagram", ROOT / "docs/social-covers"):
            for p in folder.rglob("index.html"):
                content = p.read_text(encoding="utf8")
                if "brandstudio-page.js" not in content:
                    continue
                matches = re.findall(
                    r'<script src="([^"]*brandstudio-page\.js)" data-product-id="([^"]+)"></script>',
                    content,
                )
                self.assertEqual(len(matches), 1, str(p))
                src, product_id = matches[0]
                self.assertTrue((p.parent / src).resolve().is_file(), str(p))
                entries.append((p, product_id))
        self.assertGreaterEqual(len(entries), 15)
        known = {v["id"] for g in self.catalogue["groups"] for v in g["versions"]}
        self.assertEqual([str(p) for p, pid in entries if pid not in known], [])
        self.assertFalse(any("archive" in str(p) for p, _ in entries))

    def test_technical_sections_can_collapse_without_losing_interactive_slides(self):
        html = (ROOT / "docs/instagram/rotani-sec-tokyo-seoul-001/v2/index.html").read_text(encoding="utf8")
        for phrase in ("Mobil okunabilirlik", "Revizyon karşılaştırması",
                       "Kaynak, doğrulama ve atıf"):
            self.assertIn(phrase, html)
        self.assertIn("mobiles=document.querySelector('#mobiles')", html)
        self.assertIn('brandstudio-page.js', html)
        self.assertIn("organizeResources()", self.source)

if __name__ == "__main__":
    unittest.main()

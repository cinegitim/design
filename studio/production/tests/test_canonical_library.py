"""Regression gates for the canonical Brandstudio taxonomy / public site projection."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"studio/production/catalog"))
from build_library import build, load, output_text, SOURCE, EDITOR, OUTPUT  # noqa: E402

PATHS=[
 SOURCE,EDITOR,OUTPUT,
 "docs/visual-editor/browser/product-groups.json",
 "docs/visual-editor/browser/style-registry.json",
]


class CanonicalLibraryTests(unittest.TestCase):
    def test_exact_checked_in_projection_and_editor_mirror(self):
        catalog=build(ROOT)
        self.assertEqual(output_text(catalog),(ROOT/OUTPUT).read_text(encoding="utf-8"))
        self.assertEqual((ROOT/SOURCE).read_bytes(),(ROOT/EDITOR).read_bytes())
        self.assertEqual(len(catalog["products"]),18)
        self.assertEqual(sum(len(x["versions"]) for x in catalog["products"]),31)
        self.assertEqual(len(catalog["styles"]),3)
        self.assertEqual(catalog["retiredCount"],2)
        self.assertEqual(
            {x["brand"] for x in catalog["products"]},
            {"asyada-egitim","cin-egitim"}
        )
        self.assertEqual(
            len([x for x in catalog["products"] if x["brand"]=="asyada-egitim"]),17
        )
        for p in catalog["products"]:
            for l in p["styleLinks"]:
                self.assertNotEqual(l["status"],"approved")
                if l["status"]=="proposed":
                    self.assertEqual(l["scope"],"future-design")
                    self.assertIsNone(l["versionId"])
        self.assertEqual(
            sum(l["status"]=="verified" for p in catalog["products"] for l in p["styleLinks"]),
            0
        )

    def test_shared_style_spans_multiple_content_groups_without_copying_sources(self):
        catalog=build(ROOT)
        data=[p for p in catalog["products"] if any(
            l["styleId"]=="data-atlas" for l in p["styleLinks"]
        )]
        self.assertEqual(len(data),4)
        self.assertEqual({p["subCategory"] for p in data},
                         {"Üniversite Tanıtımları","Şehir ve Öğrenci Yaşamı",
                          "Başvuru ve Burs Rehberleri"})
        self.assertEqual(len({x["groupId"] for x in catalog["products"]}),18)
        allversions=[v["id"] for p in catalog["products"] for v in p["versions"]]
        self.assertEqual(len(set(allversions)),31)
        self.assertTrue(all("sourcePath" in s and "sourceBlobSha" in s
                            for s in catalog["styles"]))

    def _temp(self):
        directory=TemporaryDirectory()
        temporary=Path(directory.name)
        for rel in PATHS:
            target=temporary/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/rel,target)
        return directory,temporary

    def test_check_is_read_only_and_fails_closed_on_projection_drift(self):
        with TemporaryDirectory() as temp:
            pass
        env,tmp=self._temp()
        try:
            script=ROOT/"studio/production/catalog/build_library.py"
            ok=subprocess.run([sys.executable,str(script),"--root",str(tmp),"--check"],
                              capture_output=True,text=True,timeout=20)
            self.assertEqual(ok.returncode,0,ok.stderr)
            marker=tmp/OUTPUT
            marker.write_text('{"fake":true}\n',encoding="utf-8")
            failed=subprocess.run([sys.executable,str(script),"--root",str(tmp),"--check"],
                                  capture_output=True,text=True,timeout=20)
            self.assertNotEqual(failed.returncode,0)
            self.assertIn("Stale projections",failed.stderr)
            self.assertEqual(marker.read_text(),'{\"fake\":true}\n',
                             "Read-only check must never overwrite tampered data")
        finally:
            env.cleanup()

    def test_forged_approval_cross_brand_preset_and_missing_family_rejected(self):
        for tweak in ("approval","foreign-style","bad-preset","missing-family","wrong-format",
                      "false-version"):
            with self.subTest(tweak=tweak):
                env,tmp=self._temp()
                try:
                    nav=load(tmp,SOURCE)
                    if tweak=="approval":
                        nav["items"][0]["suggestion"]["status"]="approved"
                    elif tweak=="foreign-style":
                        next(x for x in nav["items"] if x["groupId"]=="cin-egitim-rollup")["suggestion"]={
                            "styleId":"data-atlas","presetId":"metrics-overview",
                            "status":"proposed","scope":"future-design"}
                    elif tweak=="bad-preset":
                        nav["items"][0]["suggestion"]["presetId"]="invented"
                    elif tweak=="missing-family":
                        nav["items"]=nav["items"][:-1]
                    elif tweak=="wrong-format":
                        nav["items"][0]["mainCategory"]="Roll-up"
                    else:
                        nav["confirmedVersions"].append({
                            "groupId":"instagram-tsinghua-atlas-2027",
                            "versionId":"made-up-v3","styleId":"data-atlas",
                            "presetId":"metrics-overview","status":"verified",
                            "evidence":"https://github.com/cinegitim/design/pull/227"})
                    (tmp/SOURCE).write_text(json.dumps(nav,ensure_ascii=False,indent=2)+"\n",
                                            encoding="utf-8")
                    with self.assertRaises((ValueError,KeyError)):
                        build(tmp)
                finally:
                    env.cleanup()

    def test_main_website_is_connected_to_shared_data_source(self):
        site=(ROOT/"docs/library/index.html").read_text(encoding="utf-8")
        js=(ROOT/"docs/library/app.js").read_text(encoding="utf-8")
        home=(ROOT/"docs/index.html").read_text(encoding="utf-8")
        workspace=(ROOT/"docs/workspaces/asyada-egitim/index.html").read_text(encoding="utf-8")
        system=(ROOT/"docs/system/index.html").read_text(encoding="utf-8")
        for key in ('id="mode-content"','id="mode-style"','id="main"','id="sub"',
                    'id="style"','id="preset"','id="results"'):
            self.assertIn(key,site)
        self.assertIn('fetch("catalog.json"',js)
        self.assertIn("filteredProducts",js)
        self.assertIn("styleLinks",js)
        self.assertIn("function associationForRow(row)",js)
        self.assertIn('node("details","versions-details")',js)
        self.assertIn("row.p.styleLinks.find",js)
        self.assertIn("for(const v of p.versions)",js)
        self.assertIn('id="category-tree"',site)
        self.assertIn('id="active-filters"',site)
        self.assertIn('id="advanced-filters"',site)
        self.assertIn('id="active-heading"',site)
        self.assertIn('id="style-rail"',site)
        self.assertIn("function renderCategories()",js)
        self.assertIn("function renderActiveFilters()",js)
        self.assertIn("function renderStyleCards()",js)
        self.assertIn("function entries(products)",js)
        self.assertIn("function filteredProducts()",js)
        self.assertIn('node("article","product-card")',js)
        self.assertNotIn('Nasıl gezinmek istersin?',site)

        self.assertIn('href="library/"',home)
        self.assertIn('../library/?brand=asyada-egitim',system)
        self.assertIn('../../library/?brand=asyada-egitim&view=style',workspace)
        self.assertIn("fetch('../../library/catalog.json'",workspace)
        self.assertIn("pubUrl",workspace)
        self.assertIn("BrandstudioPublicationBridge",workspace)


if __name__=="__main__":
    unittest.main()

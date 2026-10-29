"""Non-destructive audit guards for the exhaustive production inventory."""
import json
import pathlib
import re
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "docs" / "inventory" / "snapshot.json"
CATALOG = ROOT / "docs" / "inventory" / "catalog.js"
VIEWER = ROOT / "docs" / "inventory" / "index.html"


class ExhaustiveProductionInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf8"))

    def test_snapshot_is_complete_and_every_pinned_file_still_exists(self):
        s = self.snapshot
        self.assertEqual(s["schema"], 1)
        self.assertRegex(s["tree_sha"], r"^[a-f0-9]{40}$")
        self.assertEqual(s["file_count"], len(s["files"]))
        self.assertEqual(s["file_count"], 3500)
        paths = [f[0] for f in s["files"]]
        self.assertEqual(len(paths), len(set(paths)))
        for path, sha, size in s["files"]:
            with self.subTest(path=path):
                self.assertRegex(sha, r"^[a-f0-9]{40}$")
                self.assertIsInstance(size, int)
                self.assertGreaterEqual(size, 0)
                self.assertFalse(path.startswith("/"))
                self.assertNotIn("..", pathlib.PurePosixPath(path).parts)
                self.assertTrue((ROOT / path).is_file(), path)

    def test_audited_tree_is_an_exact_git_snapshot_if_available(self):
        if not shutil.which("git"):
            self.skipTest("git unavailable")
        sha = self.snapshot["tree_sha"]
        result = subprocess.run(
            ["git", "ls-tree", "-rz", "--long", sha],
            cwd=ROOT, capture_output=True, timeout=30,
        )
        if result.returncode != 0:
            self.skipTest("Source commit unavailable in shallow CI checkout")
        actual = {}
        for part in result.stdout.split(b"\x00"):
            if not part:
                continue
            match = re.fullmatch(rb"100(?:644|755) blob ([0-9a-f]{40})\s+(\d+)\t(.+)", part)
            if match:
                path = match.group(3).decode("utf8")
                actual[path] = [match.group(1).decode("ascii"), int(match.group(2))]
        pinned = {path: [blob, size] for path, blob, size in self.snapshot["files"]}
        self.assertEqual(actual, pinned)

    def test_catalog_covers_every_file_exactly_once(self):
        if not shutil.which("node"):
            self.skipTest("Node is not installed")
        script = r"""
const fs=require('fs'),vm=require('vm');
const scope={};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),scope);
const I=scope.BrandstudioInventory,raw=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const inv=I.build(I.snapshotToTree(raw),{sha:raw.tree_sha});
if(inv.filesCount!==raw.file_count)throw Error('Unclassified files');
if(inv.groups.reduce((n,g)=>n+g.files.length,0)!==raw.file_count)throw Error('Group coverage mismatch');
if(!inv.groups.every(g=>g.id&&g.files.length))throw Error('Empty or unnamed group');
if(!inv.groups.some(g=>g.review==='candidate'))throw Error('No review candidates');
if(!inv.groups.some(g=>g.review==='protected'&&g.id==='brands/asyada-egitim/assets'))throw Error('Canonical brand assets not protected');
if(!inv.groups.some(g=>g.category==='social'))throw Error('Instagram production records missing');
console.log(JSON.stringify({files:inv.filesCount,groups:inv.groupsCount,summary:inv.summary}));
"""
        output = subprocess.run(
            ["node", "-e", script, str(CATALOG), str(SNAPSHOT)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(output.returncode, 0, output.stderr or output.stdout)
        summary = json.loads(output.stdout)
        self.assertEqual(summary["files"], 3500)

    def test_inventory_is_machine_readable_without_unrequested_ui(self):
        self.assertFalse(VIEWER.exists(), "The additional inventory interface must not return")
        module = CATALOG.read_text(encoding="utf8")
        self.assertIn("snapshot.json", module)
        self.assertIn("function classify(p)", module)
        self.assertNotIn("DELETE FROM", module)
        self.assertNotIn("git rm", module)
        editor = (ROOT / "docs/visual-editor/browser/catalog.js").read_text(encoding="utf8")
        self.assertIn("function fromPaths(paths)", editor)
        self.assertIn("function groupRecords(raw,config)", editor)
        self.assertIn("product-groups.json", editor)
        self.assertIn("socialPublication", editor)
        source = (ROOT / "docs/visual-editor/browser/product-groups.json").read_text(encoding="utf8")
        self.assertEqual(len(json.loads(source)["groups"]), 15)
        archive = json.loads((ROOT / "docs/archive/retired-collections.json").read_text(encoding="utf8"))
        self.assertEqual(sum(x["fileCount"] for x in archive["collections"]), archive["filesTotal"])
        self.assertEqual(archive["transferState"], "archive-branch-verified-source-paths-preserved")


if __name__ == "__main__":
    unittest.main()

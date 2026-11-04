"""Fast stdlib-only rejection tests for Brandstudio finished-product packages."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "finalized_audit.py"
spec = importlib.util.spec_from_file_location("finalized_audit", SOURCE)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)

PRODUCT = "instagram-kaist-tech-track-2027-001-v2"
UUID = "12345678-90ab-cdef-1234-567890abcdef"
REV = "1234567890ab"
PREFIX = f"studio/production/finalized/{PRODUCT}/{REV}/"
STATE = {"colors": {"paper": "#f7f3e9", "ink": "#1d2027", "red": "#bd2120"},
         "edits": {}, "groups": {}}

def write(root, rel, obj):
    file = root / rel
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(obj) if isinstance(obj, (dict, list)) else obj, encoding="utf-8")

def fixture(root):
    write(root, PREFIX + "manifest.json", {
        "schema": 1, "kind": "brandstudio-product-finalization", "product": PRODUCT,
        "revision": UUID, "selectedVersion": 2, "versions": [1, 2],
        "review": {"creative": "pending", "socialPublished": False, "sourceAuditRequired": True},
        "source": {"repository": "cinegitim/design", "baseCommit": "a" * 40,
                   "paths": ["docs/instagram/kaist/v2/source/01.html"]},
        "files": {"renderedSlides": 4, "versionStates": 2, "history": "history.json"}})
    write(root, PREFIX + "history.json", {"schema": 1, "product": PRODUCT, "history": []})
    for v in [1, 2]:
        base = PREFIX + f"versions/v{v:02d}/"
        write(root, base + "editor-state.json", {
            "schema": 1, "kind": "brandstudio-saved-editor-version",
            "product": PRODUCT, "version": v, "state": STATE})
        write(root, base + "slides/01.html",
              '<!doctype html><html><body><div class="slide">KAIST</div></body></html>')
        write(root, base + "slides/01.css", ".slide {color: red;}")
    return PREFIX + "versions/v02/slides/01.html"

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.changed = [fixture(self.root)]

    def tearDown(self):
        self.tmp.cleanup()

    def run_audit(self, render=False):
        return auditor.audit(self.root, self.changed, check_source=False, cover=render)

    def test_one_product_and_only_final_candidate(self):
        self.changed += ["docs/example.html"]
        with mock.patch.object(auditor, "render_cover") as chrome:
            result = self.run_audit(render=True)
        self.assertEqual(result["packages"], 1)
        self.assertEqual(result["coverRenders"], 1)
        self.assertEqual(result["results"][0]["versions"], 2)
        chrome.assert_called_once()
        self.assertTrue(chrome.call_args.args[0].endswith("v02/slides/01.html"))

    def test_no_finalized_changes_does_no_work(self):
        self.changed = ["docs/instagram/example.html"]
        self.assertEqual(self.run_audit()["packages"], 0)

    def test_missing_slide_blocks_delivery(self):
        (self.root / PREFIX / "versions/v01/slides/01.css").unlink()
        with self.assertRaises(auditor.Reject):
            self.run_audit()

    def test_unexpected_file_blocks_delivery(self):
        write(self.root, PREFIX + "unverified.txt", "bad")
        with self.assertRaises(auditor.Reject):
            self.run_audit()

    def test_publication_cannot_be_silently_approved(self):
        file = self.root / PREFIX / "manifest.json"
        obj = json.loads(file.read_text())
        obj["review"]["socialPublished"] = True
        write(self.root, PREFIX + "manifest.json", obj)
        with self.assertRaises(auditor.Reject):
            self.run_audit()

    def test_version_selection_must_exist(self):
        file = self.root / PREFIX / "manifest.json"
        obj = json.loads(file.read_text())
        obj["selectedVersion"] = 3
        write(self.root, PREFIX + "manifest.json", obj)
        with self.assertRaises(auditor.Reject):
            self.run_audit()

    def test_product_prefix_fails_closed_on_traversal(self):
        with self.assertRaises(auditor.Reject):
            auditor.group_changes(["studio/production/finalized/../../secret/manifest.json"])

    def test_multiple_files_same_product_only_one_audit(self):
        self.changed += [PREFIX + "history.json", PREFIX + "versions/v02/editor-state.json"]
        self.assertEqual(self.run_audit()["packages"], 1)

    def test_symlinks_fail_closed(self):
        target = self.root / PREFIX / "outside"
        target.symlink_to(self.root / PREFIX / "manifest.json")
        with self.assertRaises(auditor.Reject):
            self.run_audit()

if __name__ == "__main__":
    unittest.main()

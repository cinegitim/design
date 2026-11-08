"""Brandstudio v3 P1 semantic validator safety tests."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P))
F = P / "tests" / "fixtures" / "contracts"

def fixture(name):
    return json.loads((F / name).read_text(encoding="utf-8"))

class ContractValidationTests(unittest.TestCase):
    def test_valid_fixture_bundle(self):
        from contracts.validation import validate_bundle
        validate_bundle(fixture("task-valid.json"), fixture("capability-opencode.json"),
                        fixture("receipt-valid.json"), fixture("manifest-prepared.json"), root=P.parents[1])

    def test_reject_private_brief_url_and_raw_secret_without_echo(self):
        from contracts.validation import validate_document
        for value in ("https://example.org?token=superprivate", "my private prompt password=superprivate", "repo:docs/file?token=superprivate"):
            doc = fixture("task-valid.json")
            doc["brief_ref"] = value
            with self.subTest(value=value), self.assertRaises(ValueError) as ctx:
                validate_document("task", doc, root=P.parents[1])
            self.assertNotIn("superprivate", str(ctx.exception))

    def test_reject_absolute_dotdot_symlink_and_foreign_brand_paths(self):
        from contracts.validation import validate_document
        for value in ("/tmp/file", "docs/../.env", "docs//bad", "docs/instagram/../../secrets", "docs/instagram/asya-egitim/v1"):
            doc = fixture("task-valid.json")
            doc["output_ref"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_document("task", doc, root=P.parents[1])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "brands" / "asyada-egitim").mkdir(parents=True)
            (root / "brands" / "asyada-egitim" / "brand.json").write_text("{}")
            (root / "studio" / "production").mkdir(parents=True)
            (root / "studio" / "production" / "routes.json").write_text(
                (P / "routes.json").read_text(encoding="utf-8"))
            (root / "docs").mkdir()
            (root / "docs" / "out").symlink_to(root / "brands", target_is_directory=True)
            doc = fixture("task-valid.json")
            doc["output_ref"] = "docs/out/asyada-egitim"
            with self.assertRaises(ValueError):
                validate_document("task", doc, root=root)

    def test_reject_unregistered_existing_brand(self):
        from contracts.validation import validate_document
        doc = fixture("task-valid.json")
        doc["brand_slug"] = "nonexistent-brand"
        with self.assertRaises(ValueError):
            validate_document("task", doc, root=P.parents[1])

    def test_reject_cross_record_task_mismatch(self):
        from contracts.validation import validate_bundle
        receipt = fixture("receipt-valid.json")
        receipt["task_id"] = "brandstudio-different-task"
        with self.assertRaises(ValueError):
            validate_bundle(fixture("task-valid.json"), fixture("capability-opencode.json"),
                            receipt, fixture("manifest-prepared.json"), root=P.parents[1])

    def test_parallel_requires_explicit_approval(self):
        from contracts.validation import validate_document
        doc = fixture("task-valid.json")
        doc["max_parallel"] = 2
        with self.assertRaises(ValueError):
            validate_document("task", doc, root=P.parents[1])
        doc["approval"]["parallel_approved"] = True
        validate_document("task", doc, root=P.parents[1])

    def test_unknown_schema_version_rejected(self):
        from contracts.validation import validate_document
        doc = fixture("task-valid.json")
        doc["schema_version"] = 3
        with self.assertRaises(ValueError):
            validate_document("task", doc, root=P.parents[1])

    def test_manifest_files_must_stay_in_output_subtree(self):
        from contracts.validation import validate_bundle
        doc = fixture("manifest-prepared.json")
        doc["renders"][0]["path"] = "docs/instagram/another-family/slide.png"
        with self.assertRaises(ValueError):
            validate_bundle(fixture("task-valid.json"), None, None, doc, root=P.parents[1])


    def test_reject_retired_asyada_lockup_in_manifest(self):
        from contracts.validation import validate_bundle
        doc = fixture("manifest-prepared.json")
        doc["lockup"]["canonical_id"] = "C-03/light"
        with self.assertRaises(ValueError):
            validate_bundle(fixture("task-valid.json"), None, None, doc, root=P.parents[1])

    def test_reject_unsafe_handoff_branch_names(self):
        from contracts.validation import validate_document
        for branch in ("feature/../main", "feature//main", "main..bad", "feature/main.lock"):
            receipt = fixture("receipt-valid.json")
            receipt["branch"] = branch
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                validate_document("task-receipt", receipt, root=P.parents[1])

if __name__ == "__main__":
    unittest.main()

"""Production Recorder v1: offline, stdlib-only, no provider/network calls."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Args

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION / "recording"))
import recorder as rec  # noqa: E402

SHA = "a4e2b9b48ab61bb0f3444dfbec20e58b213a8bb5"


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.private = self.root / ".brandstudio-private" / "run.json"

    def new(self, **updates):
        values = dict(file=str(self.private), brand="asyada-egitim",
                      category="instagram-carousel", executor="chatgpt-chat",
                      route="chatgpt-connected-v1", source_commit=SHA,
                      strategy_version="v1", effort=None, brief_file=None)
        values.update(updates)
        return rec.init(Args(**values))

    def test_init_keeps_unknown_usage_null(self):
        doc = self.new()
        self.assertEqual(doc["origin"]["source_commit"], SHA)
        self.assertIsNone(doc["metrics"]["input_tokens"])
        self.assertIsNone(doc["runtime"]["model_observed_id"])
        self.assertTrue(self.private.is_file())
        self.assertEqual(rec.read_private(self.private)["run_id"], doc["run_id"])

    def test_high_is_requested_not_model_verified(self):
        doc = self.new(effort="high", route="chatgpt-high-connected-v1")
        safe = rec.public_summary(doc)
        self.assertEqual(safe["runtime"]["effort_requested"], "high")
        self.assertIsNone(safe["runtime"]["model_id"])
        self.assertEqual(safe["runtime"]["model_verification"], "unavailable")

    def test_reject_forged_source_commit(self):
        with self.assertRaises(ValueError):
            self.new(source_commit="main")

    def test_reject_chat_effort_on_codex(self):
        with self.assertRaises(ValueError):
            self.new(executor="codex", effort="high")

    def test_private_storage_only(self):
        with self.assertRaises(ValueError):
            self.new(file=str(self.root / "public.json"))

    def test_no_overwrite_existing_run(self):
        self.new()
        with self.assertRaises(ValueError):
            self.new()

    def test_observed_metrics_require_explicit_source(self):
        doc = self.new()
        rec.metrics(Args(file=str(self.private), source="visible-ui",
                         input_tokens=20, output_tokens=0, cache_tokens=None))
        stored = rec.read_private(self.private)
        self.assertEqual(stored["metrics"]["input_tokens"], 20)
        self.assertEqual(stored["metrics"]["output_tokens"], 0)
        self.assertEqual(stored["metrics"]["source"], "visible-ui")

    def test_negative_metrics_rejected_without_mutating_file(self):
        self.new()
        original = self.private.read_bytes()
        with self.assertRaises(ValueError):
            rec.metrics(Args(file=str(self.private), source="visible-ui",
                             input_tokens=-2, output_tokens=None, cache_tokens=None))
        self.assertEqual(self.private.read_bytes(), original)

    def test_approved_repo_file_is_hashed(self):
        self.new()
        path = self.root / "docs" / "instagram" / "test.svg"
        path.parent.mkdir(parents=True)
        path.write_text("<svg/>", encoding="utf-8")
        rec.artifact(Args(file=str(self.private), root=str(self.root),
                          path="docs/instagram/test.svg"))
        doc = rec.read_private(self.private)
        self.assertEqual(doc["artifacts"][0]["sha256"],
                         hashlib.sha256(b"<svg/>").hexdigest())
        self.assertEqual(doc["artifacts"][0]["evidence"], "locally-hashed-file")

    def test_traversal_and_hidden_files_rejected(self):
        self.new()
        for bad in ("../secrets", "docs/../../secrets", ".env", "/etc/passwd",
                    "docs/.secret", "other/test.svg"):
            with self.subTest(path=bad), self.assertRaises(ValueError):
                rec.artifact(Args(file=str(self.private), root=str(self.root), path=bad))

    def test_symlink_to_external_content_rejected(self):
        self.new()
        out = self.root / "outside"
        out.write_text("sensitive")
        link = self.root / "docs" / "link"
        link.parent.mkdir()
        link.symlink_to(out)
        with self.assertRaises(ValueError):
            rec.artifact(Args(file=str(self.private), root=str(self.root), path="docs/link"))

    def test_cannot_complete_without_artifact(self):
        self.new()
        with self.assertRaises(ValueError):
            rec.finish(Args(file=str(self.private), status="finished"))
        self.assertEqual(rec.read_private(self.private)["status"], "in_progress")

    def test_finished_run_is_immutable(self):
        self.new()
        rec.finish(Args(file=str(self.private), status="planned"))
        with self.assertRaises(ValueError):
            rec.event(Args(file=str(self.private), kind="tool-called"))

    def test_observed_model_source_is_reported_not_verified(self):
        self.new()
        rec.model(Args(file=str(self.private), model_id="model_from_host",
                       source="host-metadata"))
        safe = rec.public_summary(rec.read_private(self.private))
        self.assertEqual(safe["runtime"]["model_id"], "model_from_host")
        self.assertEqual(safe["runtime"]["model_verification"],
                         "reported-with-host-metadata")

    def test_ci_success_requires_exact_checked_head(self):
        self.new()
        before = self.private.read_bytes()
        with self.assertRaises(ValueError):
            rec.delivery(Args(file=str(self.private), pr_number=123,
                              head_sha=SHA, checked_head_sha=None,
                              ci_status="success", merged_commit=None))
        self.assertEqual(self.private.read_bytes(), before)

    def test_attested_gitHub_delivery_not_independent_verification(self):
        self.new()
        rec.delivery(Args(file=str(self.private), pr_number=119, head_sha=SHA,
                          checked_head_sha=SHA, ci_status="success",
                          merged_commit=None))
        safe = rec.public_summary(rec.read_private(self.private))
        self.assertEqual(safe["delivery"]["pr_number"], 119)
        self.assertEqual(safe["delivery"]["checked_head_sha"], SHA)
        self.assertIn("not-independently-verified", safe["delivery"]["attestation"])

    def test_finished_run_with_real_artifact(self):
        self.new()
        asset = self.root / "docs" / "proof.svg"
        asset.parent.mkdir()
        asset.write_text("<svg/>")
        rec.artifact(Args(file=str(self.private), root=str(self.root),
                          path="docs/proof.svg"))
        rec.finish(Args(file=str(self.private), status="finished"))
        self.assertEqual(rec.read_private(self.private)["status"], "finished")
        self.assertIsInstance(rec.read_private(self.private)["time"]["wall_seconds"], int)

    def test_public_export_omits_raw_data(self):
        doc = self.new()
        doc["private_note"] = "NOT_FOR_PUBLICATION"
        doc["task"]["raw_brief"] = "PERSONAL_BRIEF_TEXT"
        safe = rec.public_summary(doc)
        serialized = json.dumps(safe)
        self.assertNotIn("NOT_FOR_PUBLICATION", serialized)
        self.assertNotIn("PERSONAL_BRIEF_TEXT", serialized)
        self.assertNotIn("raw_brief", serialized)
        self.assertIsNone(safe["usage"]["input_tokens"])

    def test_public_export_filters_nested_extra_fields(self):
        doc = self.new()
        doc["metrics"]["private_api_key"] = "NEVER_PUBLISH_METRICS_SECRET"
        doc["delivery"]["comment"] = "NEVER_PUBLISH_DELIVERY_SECRET"
        doc["artifacts"].append({
            "path": "docs/output.svg",
            "sha256": hashlib.sha256(b"demo").hexdigest(),
            "evidence": "locally-hashed-file",
            "private_note": "NEVER_PUBLISH_ARTIFACT_SECRET",
        })
        safe = json.dumps(rec.public_summary(doc))
        self.assertNotIn("NEVER_PUBLISH_", safe)

    def test_private_symlink_parent_rejected(self):
        safe = self.root / "real-private"
        safe.mkdir()
        link = self.root / ".brandstudio-private"
        link.symlink_to(safe)
        with self.assertRaises(ValueError):
            self.new()

    def test_event_counts_only_not_freeform_logs(self):
        self.new()
        rec.event(Args(file=str(self.private), kind="repo-read"))
        rec.event(Args(file=str(self.private), kind="repo-read"))
        safe = rec.public_summary(rec.read_private(self.private))
        self.assertEqual(safe["event_counts"], {"repo-read": 2})
        self.assertNotIn("events", safe)


if __name__ == "__main__":
    unittest.main()

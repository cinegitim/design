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

    def test_event_counts_only_not_freeform_logs(self):
        self.new()
        rec.event(Args(file=str(self.private), kind="repo-read"))
        rec.event(Args(file=str(self.private), kind="repo-read"))
        safe = rec.public_summary(rec.read_private(self.private))
        self.assertEqual(safe["event_counts"], {"repo-read": 2})
        self.assertNotIn("events", safe)


if __name__ == "__main__":
    unittest.main()

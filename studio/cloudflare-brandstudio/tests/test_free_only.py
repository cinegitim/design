import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from check_free_only import FreeOnlyViolation, check


class ZeroCostGuardTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name) / "app"
        copytree(ROOT, self.root, ignore=lambda d, names:
                 [n for n in names if n in {"dist", "__pycache__"}])
    def tearDown(self):
        self.d.cleanup()

    def test_current_config_passes(self):
        self.assertEqual(check(self.root)["result"], "PASS")

    def test_r2_binding_is_rejected(self):
        p = self.root / "wrangler.jsonc"
        j = json.loads(p.read_text())
        j["r2_buckets"] = [{"binding": "R2", "bucket_name": "test"}]
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(FreeOnlyViolation, "bindings"):
            check(self.root)

    def test_allowing_editor_writes_is_rejected(self):
        p = self.root / "free-only-policy.json"
        j = json.loads(p.read_text())
        j["editor"]["write_api_enabled"] = True
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(FreeOnlyViolation, "write routes"):
            check(self.root)

    def test_lifting_quota_caps_is_rejected(self):
        p = self.root / "free-only-policy.json"
        j = json.loads(p.read_text())
        j["deployment"]["max_output_bytes"] = 4_000_000_000
        p.write_text(json.dumps(j))
        with self.assertRaisesRegex(FreeOnlyViolation, "output cap"):
            check(self.root)

    def test_paid_service_code_is_rejected(self):
        p = self.root / "src/worker.mjs"
        p.write_text(p.read_text() + "\nconst s=env.R2;\n")
        with self.assertRaisesRegex(FreeOnlyViolation, "Paid service"):
            check(self.root)

if __name__ == "__main__":
    unittest.main()

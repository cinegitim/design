"""Advisory routing must never claim execution or new access."""
import copy
import json
import sys
import unittest
from pathlib import Path
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P))
F = P / "tests" / "fixtures" / "contracts"
ROOT = P.parents[1]
CONFIG = json.loads((P / "routes.json").read_text(encoding="utf-8"))
def fixture(name):
    return json.loads((F / name).read_text(encoding="utf-8"))

class AdvisoryTests(unittest.TestCase):
    def test_opencode_work_same_task_different_routes(self):
        from advisory import propose
        task = fixture("task-valid.json")
        a = propose(task=task, report=fixture("capability-opencode.json"), root=ROOT, config=CONFIG)
        work = fixture("capability-work.json")
        work["capabilities"]["filesystem"] = {"status":"observed","evidence_source":"host-tool-inventory"}
        b = propose(task=task, report=work, root=ROOT, config=CONFIG)
        self.assertTrue(a["eligible"]);self.assertTrue(b["eligible"])
        self.assertEqual(a["candidate"]["route"]["id"],"opencode-code-v1")
        self.assertEqual(b["candidate"]["route"]["id"],"work-connected-v1")
        self.assertEqual(a["task_id"],b["task_id"])
        self.assertEqual(task["approval"]["creative"],"pending")

    def test_missing_capability_and_no_evidence_blocks(self):
        from advisory import propose
        report=fixture("capability-opencode.json")
        report["capabilities"]["filesystem"]["evidence_source"] = None
        result=propose(task=fixture("task-valid.json"), report=report, root=ROOT, config=CONFIG)
        self.assertFalse(result["eligible"])
        self.assertTrue(result["blockers"])

    def test_executor_not_allowed_blocks(self):
        from advisory import propose
        report=fixture("capability-opencode.json")
        report["executor"]="antigravity"
        self.assertFalse(propose(task=fixture("task-valid.json"), report=report, root=ROOT, config=CONFIG)["eligible"])

    def test_generic_limited_is_never_ready(self):
        from advisory import propose
        report=fixture("capability-work.json")
        self.assertFalse(propose(task=fixture("task-valid.json"), report=report, root=ROOT, config=CONFIG)["eligible"])

    def test_no_hidden_model_spend_or_task_mutation(self):
        from advisory import propose
        task=fixture("task-valid.json")
        original=copy.deepcopy(task)
        result=propose(task=task, report=fixture("capability-opencode.json"), root=ROOT, config=CONFIG)
        self.assertEqual(task,original)
        self.assertEqual(result["mode"],"v3-advisory")
        self.assertEqual(result["candidate"]["mode"],"read-only-dry-run")
        self.assertFalse(result["candidate"]["telemetry"]["collected"])
        self.assertEqual(result["candidate"]["route"]["status"],"candidate-not-benchmarked")

    def test_legacy_router_output_unchanged(self):
        from advisory import propose
        from router import plan
        task=fixture("task-valid.json"); report=fixture("capability-opencode.json")
        proposal=propose(task=task,report=report,root=ROOT,config=CONFIG)
        direct=plan(root=ROOT,config=CONFIG,executor="opencode",brand="asyada-egitim",
                    category="instagram-carousel",capabilities={"filesystem","terminal"})
        self.assertEqual(proposal["candidate"],direct)

if __name__ == "__main__":
    unittest.main()

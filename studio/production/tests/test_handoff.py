"""P2 offline cross-executor handoff — test first, no actual agent execution."""
import copy
import json
import sys
import unittest
from pathlib import Path

PRODUCTION=Path(__file__).resolve().parents[1]
ROOT=PRODUCTION.parents[1]
sys.path.insert(0,str(PRODUCTION))
FIX=PRODUCTION/"tests"/"fixtures"/"contracts"
BASE="a4e2b9b48ab61bb0f3444dfbec20e58b213a8bb5"
SOURCE_HEAD="b"*40
TARGET_HEAD="c"*40

def fixture(name):
    return json.loads((FIX/name).read_text(encoding="utf-8"))

def task_and_receipt():
    task=fixture("task-valid.json")
    source=fixture("receipt-valid.json")
    source["head_sha"]=SOURCE_HEAD
    return task,source

class HandoffTests(unittest.TestCase):
    def prepared(self):
        from handoff.protocol import prepare
        task,source=task_and_receipt()
        return prepare(task,source,target_executor="chatgpt-work",
                       target_branch="publish/work-p2-kaist",
                       receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)

    def test_prepare_pins_original_and_source_head_separately(self):
        env=self.prepared()
        self.assertEqual(env["original_base_sha"],BASE)
        self.assertEqual(env["source_head_sha"],SOURCE_HEAD)
        self.assertEqual(env["source_executor"],"opencode")
        self.assertEqual(env["target_executor"],"chatgpt-work")
        self.assertEqual(env["status"],"prepared")
        self.assertEqual(env["observed_via"],"none")

    def test_prepare_does_not_mutate_original_records(self):
        from handoff.protocol import prepare
        task,receipt=task_and_receipt()
        original=(copy.deepcopy(task),copy.deepcopy(receipt))
        prepare(task,receipt,target_executor="chatgpt-work",
                target_branch="publish/work-p2-kaist",
                receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)
        self.assertEqual(task,original[0]);self.assertEqual(receipt,original[1])

    def test_prepare_rejects_missing_source_head_or_mismatched_task(self):
        from handoff.protocol import prepare
        task,receipt=task_and_receipt()
        for bad in (None,"main"):
            receipt["head_sha"]=bad
            with self.assertRaises(ValueError):
                prepare(task,receipt,target_executor="chatgpt-work",target_branch="publish/work-p2-kaist",
                        receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)
        receipt["head_sha"]=SOURCE_HEAD
        receipt["task_id"]="brandstudio-other"
        with self.assertRaises(ValueError):
            prepare(task,receipt,target_executor="chatgpt-work",target_branch="publish/work-p2-kaist",
                    receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)

    def test_prepare_rejects_same_executor_or_branch_and_disallowed_target(self):
        from handoff.protocol import prepare
        task,receipt=task_and_receipt()
        for executor,branch in (("opencode","publish/other"),("chatgpt-work",receipt["branch"]),
                                 ("antigravity","publish/antigravity-other")):
            with self.subTest(executor=executor,branch=branch),self.assertRaises(ValueError):
                prepare(task,receipt,target_executor=executor,target_branch=branch,
                        receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)

    def test_prepare_refuses_out_of_task_receipt_and_unsafe_branch(self):
        from handoff.protocol import prepare
        task,receipt=task_and_receipt()
        for ref in ("docs/instagram/other-task/receipt.json","../secret", "docs/instagram/p1-test/v1/../wrong"):
            with self.subTest(ref=ref),self.assertRaises(ValueError):
                prepare(task,receipt,target_executor="chatgpt-work",
                        target_branch="publish/work-p2-kaist",receipt_ref=ref,root=ROOT)
        with self.assertRaises(ValueError):
            prepare(task,receipt,target_executor="chatgpt-work",target_branch="publish/../main",
                    receipt_ref="docs/instagram/p1-test/v1/receipt.json",root=ROOT)

    def test_verify_source_refuses_stale_remote_head(self):
        from handoff.protocol import verify
        env=self.prepared()
        for bad in ({"branch":env["source_branch"],"head_sha":"d"*40,"observed_from":"github-connector"},
                    {"branch":"publish/opencode-else","head_sha":SOURCE_HEAD,"observed_from":"github-connector"},
                    {"branch":env["source_branch"],"head_sha":SOURCE_HEAD,"observed_from":"guess"}):
            with self.assertRaises(ValueError):
                verify(env,observation=bad)
        result=verify(env,observation={"branch":env["source_branch"],"head_sha":SOURCE_HEAD,
                                       "observed_from":"github-connector"})
        self.assertEqual(result["status"],"source_verified")
        self.assertEqual(result["observed_via"],"github-connector")
        self.assertEqual(env["status"],"prepared")

    def test_receive_requires_verified_source_and_exact_target_ancestry(self):
        from handoff.protocol import verify,receive
        env=self.prepared()
        receipt=fixture("receipt-valid.json")
        receipt.update(executor="chatgpt-work",branch="publish/work-p2-kaist",head_sha=TARGET_HEAD)
        good={"branch":"publish/work-p2-kaist","base_sha":SOURCE_HEAD,"head_sha":TARGET_HEAD,
              "observed_from":"git-remote"}
        with self.assertRaises(ValueError):
            receive(env,target_observation=good,target_receipt=receipt,root=ROOT)
        verified=verify(env,observation={"branch":env["source_branch"],"head_sha":SOURCE_HEAD,
                                         "observed_from":"git-remote"})
        for x in (dict(good,base_sha=BASE),dict(good,branch="main"),dict(good,head_sha="e"*40)):
            with self.subTest(x=x),self.assertRaises(ValueError):
                receive(verified,target_observation=x,target_receipt=receipt,root=ROOT)
        result=receive(verified,target_observation=good,target_receipt=receipt,root=ROOT)
        self.assertEqual(result["status"],"received")
        self.assertEqual(result["original_base_sha"],BASE)
        self.assertNotIn("creative_approved",result)
        self.assertNotIn("host_execution_verified",result)

if __name__=="__main__":
    unittest.main()

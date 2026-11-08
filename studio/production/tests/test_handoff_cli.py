"""P2 offline CLI rejects secret and stale evidence inputs."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
CLI=P/"handoff"/"cli.py"
FIX=P/"tests"/"fixtures"/"contracts"
SOURCE="b"*40

class HandoffCliTests(unittest.TestCase):
    def call(self,*args):
        return subprocess.run([sys.executable,str(CLI),*map(str,args)],cwd=ROOT,
            capture_output=True,text=True,timeout=15)

    def fixture(self,name):
        return json.loads((FIX/name).read_text(encoding="utf-8"))

    def prepared(self,root):
        task=self.fixture("task-valid.json")
        receipt=self.fixture("receipt-valid.json")
        receipt["head_sha"]=SOURCE
        taskfile=root/"task.json";receiptfile=root/"receipt.json"
        taskfile.write_text(json.dumps(task),encoding="utf-8")
        receiptfile.write_text(json.dumps(receipt),encoding="utf-8")
        r=self.call("prepare","--task",taskfile,"--source",receiptfile,
            "--target-executor","chatgpt-work","--target-branch","publish/work-p2-kaist",
            "--receipt-ref","docs/instagram/p1-test/v1/receipt.json","--root",ROOT)
        return r

    def test_prepare_roundtrip_cli_and_no_agent_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.prepared(Path(tmp))
            self.assertEqual(r.returncode,0,r.stderr)
            e=json.loads(r.stdout)
            self.assertEqual(e["status"],"prepared")
            self.assertEqual(e["source_head_sha"],SOURCE)

    def test_cli_rejects_malformed_secret_without_echo(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp)
            task=self.fixture("task-valid.json")
            task["brief_ref"]="password=SECRET-SHOULD-STAY-HIDDEN"
            f=t/"bad-task.json";f.write_text(json.dumps(task),encoding="utf-8")
            s=t/"source.json";s.write_text((FIX/"receipt-valid.json").read_text(encoding="utf-8"))
            r=self.call("prepare","--task",f,"--source",s,"--target-executor","chatgpt-work",
                "--target-branch","publish/work-p2-kaist",
                "--receipt-ref","docs/instagram/p1-test/v1/receipt.json","--root",ROOT)
            self.assertNotEqual(r.returncode,0)
            self.assertNotIn("SECRET-SHOULD-STAY-HIDDEN",r.stdout+r.stderr)

    def test_cli_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);f=t/"duplicate.json"
            f.write_text('{"schema_version":1,"schema_version":2}')
            r=self.call("verify","--envelope",f,"--observation",f)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("P2_INVALID_INPUT",r.stderr)

    def test_cli_rejects_oversized_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"long.json"
            f.write_text('{"x":"'+('A'*280000)+'"}')
            r=self.call("verify","--envelope",f,"--observation",f)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("P2_INVALID_INPUT",r.stderr)

if __name__=="__main__":
    unittest.main()

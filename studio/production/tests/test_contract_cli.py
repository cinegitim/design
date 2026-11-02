"""Offline P1 commands: never print user input or access provider services."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
F=P/"tests"/"fixtures"/"contracts"
CLI=P/"contracts_cli.py"

class ContractCliTests(unittest.TestCase):
    def run_cli(self,*args):
        return subprocess.run([sys.executable,str(CLI),*map(str,args)],cwd=str(ROOT),capture_output=True,text=True,timeout=15)

    def test_validate_valid_task_exit_zero(self):
        r=self.run_cli("validate","--kind","task","--file",F/"task-valid.json","--root",ROOT)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue(json.loads(r.stdout)["valid"])

    def test_route_work_missing_capability_blocked(self):
        r=self.run_cli("route","--task",F/"task-valid.json","--report",F/"capability-work.json","--root",ROOT)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertFalse(json.loads(r.stdout)["eligible"])

    def test_bad_json_duplicate_keys_oversized_and_deep_input_rejected(self):
        for bad in ('{"schema_version":1,"schema_version":2}', "{"+"x"*270000+"}", "["*40+"0"+"]"*40, '{"x": NaN}'):
            with self.subTest(size=len(bad)),tempfile.TemporaryDirectory() as tmp:
                source=Path(tmp)/"test.json";source.write_text(bad,encoding="utf-8")
                r=self.run_cli("validate","--kind","task","--file",source,"--root",ROOT)
                self.assertNotEqual(r.returncode,0)
                self.assertNotIn(bad[:90],r.stderr)

    def test_utf8_secret_is_not_echoed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"task.json"
            obj=json.loads((F/"task-valid.json").read_text(encoding="utf-8"))
            obj["brief_ref"]="özel veri password=SUPERSECRET"
            source.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
            r=self.run_cli("validate","--kind","task","--file",source,"--root",ROOT)
            self.assertNotEqual(r.returncode,0)
            self.assertNotIn("SUPERSECRET",r.stderr+r.stdout)
            self.assertNotIn("özel veri",r.stderr+r.stdout)

    def test_transition_rejects_ci_creative_approval(self):
        r=self.run_cli("transition","--from","creative_review","--to","accepted","--actor","human","--evidence-ref","ci:success")
        self.assertNotEqual(r.returncode,0)
        a=self.run_cli("transition","--from","creative_review","--to","accepted","--actor","human","--evidence-ref","review:owner-ok")
        self.assertEqual(a.returncode,0,a.stderr)
        self.assertEqual(json.loads(a.stdout)["state"],"accepted")

if __name__=="__main__":
    unittest.main()

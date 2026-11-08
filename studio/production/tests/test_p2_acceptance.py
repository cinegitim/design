"""P2 acceptance gate regression tests. Test real validation behavior, not source strings."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P))
FIX = P / "tests" / "fixtures" / "contracts"
BASE = "a4e2b9b48ab61bb0f3444dfbec20e58b213a8bb5"
SRC = "b" * 40
HEAD = "c" * 40


def fixture(filename):
    return json.loads((FIX / filename).read_text(encoding="utf-8"))


def geometry(**update):
    d = {
        "width": 1080, "height": 1350,
        "sections": [[200, 350], [375, 480], [490, 590],
                     [650, 870], [880, 1110]],
        "footer_top": 1264, "footer_bottom": 1350,
        "images": [True, True, True],
        "font_loaded": True,
        "external_requests": 0,
    }
    d.update(update)
    return d


def valid_records():
    task = fixture("task-valid.json")
    task["allowed_executors"] = ["opencode", "chatgpt-work"]
    source_receipt = fixture("receipt-valid.json")
    source_receipt["head_sha"] = SRC
    self_receipt = copy.deepcopy(source_receipt)
    self_receipt.update(executor="chatgpt-work", head_sha=None,
                        branch="publish/work-p2-kaist")
    target_receipt = copy.deepcopy(self_receipt)
    target_receipt["head_sha"] = HEAD
    envelope = {
        "schema_version": 1, "task_id": task["task_id"],
        "source_executor": "opencode", "target_executor": "chatgpt-work",
        "source_branch": source_receipt["branch"], "source_head_sha": SRC,
        "original_base_sha": BASE, "target_branch": "publish/work-p2-kaist",
        "output_ref": task["output_ref"],
        "receipt_ref": "docs/instagram/p1-test/v1/receipt.json",
        "observed_via": "git-remote", "target_observed_via": "none",
        "status": "source_verified",
    }
    confirmed = dict(envelope, status="received", target_observed_via="git-remote")
    source = {"branch": envelope["source_branch"], "head_sha": SRC,
              "observed_from": "git-remote"}
    target = {"branch": envelope["target_branch"], "head_sha": HEAD,
              "base_sha": SRC, "observed_from": "git-remote"}
    return task, source_receipt, self_receipt, target_receipt, envelope, confirmed, source, target


class RenderMeasurements(unittest.TestCase):
    def test_five_sections_fit_1080x1350_and_assets_font_load(self):
        from p2_acceptance import check_geometry
        self.assertEqual(check_geometry(geometry()), 5)

    def test_reject_clipped_last_section_even_if_root_size_is_correct(self):
        from p2_acceptance import check_geometry, GateError
        with self.assertRaises(GateError):
            check_geometry(geometry(sections=[[200,350], [375,480], [490,590],
                                              [650,870], [1250,1360]]))

    def test_reject_failed_image_or_font_or_remote_request(self):
        from p2_acceptance import check_geometry, GateError
        for payload in (geometry(images=[True, False, True]),
                        geometry(font_loaded=False),
                        geometry(external_requests=1)):
            with self.subTest(payload=payload), self.assertRaises(GateError):
                check_geometry(payload)

    def test_reject_missing_sections_and_wrong_canvas_width(self):
        from p2_acceptance import check_geometry, GateError
        for payload in (geometry(sections=[]), geometry(width=1090),
                        geometry(footer_top=900), geometry(height=1300)):
            with self.subTest(payload=payload), self.assertRaises(GateError):
                check_geometry(payload)


class CanonicalIntegrity(unittest.TestCase):
    def test_verify_real_bytes_not_only_claimed_html_label(self):
        from p2_acceptance import check_assets, GateError
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=root/"brands"/"a.svg"
            p.parent.mkdir(parents=True)
            p.write_bytes(b"genuine")
            expected={"brands/a.svg":hashlib.sha256(b"genuine").hexdigest()}
            self.assertEqual(check_assets(root,expected),expected)
            p.write_bytes(b"altered")
            with self.assertRaises(GateError):
                check_assets(root,expected)


class HandoffIntegrity(unittest.TestCase):
    def test_valid_p1_and_p2_transport_not_creative_approval(self):
        from p2_acceptance import check_records
        docs=valid_records()
        result=check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)
        self.assertEqual(result,"received")

    def test_reject_wrong_original_task_base(self):
        from p2_acceptance import check_records, GateError
        docs=list(valid_records())
        docs[3]["base_sha"]=SRC
        with self.assertRaises((GateError,ValueError)):
            check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)

    def test_reject_stale_target_head_and_fake_received_self_receipt(self):
        from p2_acceptance import check_records, GateError
        docs=list(valid_records())
        docs[7]["head_sha"]="d"*40
        with self.assertRaises((GateError,ValueError)):
            check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)
        docs=list(valid_records())
        docs[2]["head_sha"]=HEAD
        with self.assertRaises((GateError,ValueError)):
            check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)

    def test_reject_unapproved_or_invalid_received_envelope(self):
        from p2_acceptance import check_records, GateError
        docs=list(valid_records())
        docs[5]["source_branch"]="publish/wrong"
        with self.assertRaises((GateError,ValueError)):
            check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)
        docs=list(valid_records())
        docs[4]["status"]="received"
        with self.assertRaises((GateError,ValueError)):
            check_records(*docs,root=P.parents[1],source_head=SRC,work_head=HEAD)


if __name__ == "__main__":
    unittest.main()

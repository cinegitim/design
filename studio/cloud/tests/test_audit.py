"""Rejection tests for the independent checker. No rendering or producer execution."""
import importlib.util
import json
import os
from pathlib import Path
import struct
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib

# In CI this imports audit.py copied from the trusted base, not PR producer code.
here = Path(__file__).resolve()
engine = here.parents[1]/'audit.py'
if not engine.exists():
    engine = here.parents[3]/'audit.py'
spec = importlib.util.spec_from_file_location('audit_engine', engine)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
REPO = Path(os.environ.get('AUDIT_REPO', here.parents[3])).resolve()

def chunk(kind, data):
    return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)

def png(w=1080, h=1350):
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', w,h,8,2,0,0,0))+chunk(b'IDAT', b'x')+chunk(b'IEND', b'')

class CheckerTests(unittest.TestCase):
    def test_actual_deliveries_pass(self):
        result=A.audit(REPO, A.load(REPO/'studio/cloud/policy.json'))
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['bundles'][0]['slides'], 5)

    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(A.AuditError): A.safe_file(Path(td), '../escape')
            with self.assertRaises(A.AuditError): A.safe_file(Path(td), '/etc/passwd')

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'escape').symlink_to(REPO/'AGENTS.md')
            with self.assertRaises(A.AuditError): A.safe_file(root, 'escape')

    def test_hash_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'asset').write_bytes(b'changed')
            with self.assertRaises(A.AuditError): A.matched_file(root, 'asset', '0'*64)

    def test_png_structure_and_crc(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.png';p.write_bytes(png())
            self.assertEqual(A.png_dimensions(p), [1080,1350])
            p.write_bytes(png()[:-2])
            with self.assertRaises(A.AuditError): A.png_dimensions(p)
            broken=bytearray(png());broken[20]^=1;p.write_bytes(broken)
            with self.assertRaises(A.AuditError): A.png_dimensions(p)

    def test_secret_value_never_printed(self):
        token='gh'+'p_'+'x'*36
        with self.assertRaises(A.AuditError) as error: A.scan_text(token.encode(), 'test source')
        self.assertNotIn(token, str(error.exception))

    def test_nonfinite_geometry_rejected(self):
        for value in ('nan','inf','-inf'):
            with self.assertRaises(A.AuditError): A.number(value)

    def test_canonical_anchor_cannot_be_replaced(self):
        policy=A.load(REPO/'studio/cloud/policy.json')
        policy['canonical']['manifest_sha256']='0'*64
        with self.assertRaises(A.AuditError): A.canonical_assets(REPO,policy)

    def test_contract_cannot_be_removed(self):
        policy=A.load(REPO/'studio/cloud/policy.json')
        policy['bundles'][0]['dimensions']=[1,1]
        with self.assertRaises(A.AuditError): A.audit(REPO,policy)

    def test_isolated_stdlib_runner_ignores_pr_module_shadow(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'unittest.py').write_text('raise RuntimeError("PR module executed")')
            (root/'sitecustomize.py').write_text('raise RuntimeError("PR site hook executed")')
            env=dict(os.environ,PYTHONPATH=str(root))
            r=subprocess.run([sys.executable,'-I','-B','-m','unittest','--help'],cwd=root,env=env,capture_output=True)
            self.assertEqual(r.returncode,0)
            self.assertNotIn(b'PR module executed',r.stderr)

class BundleRejectionTests(unittest.TestCase):
    """Mutate actual submitted bundle in disposable copies, not just helper inputs."""
    @classmethod
    def setUpClass(cls):
        cls.policy=A.load(REPO/'studio/cloud/policy.json')
        cls.contract=cls.policy['bundles'][0]
        cls.records=A.canonical_assets(REPO,cls.policy)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.base=self.root/self.contract['path']
        # Hardlink unchanged large artwork; mutated files MUST first be unlinked.
        shutil.copytree(REPO/self.contract['path'],self.base,copy_function=os.link)

    def tearDown(self): self.temp.cleanup()

    def replace(self, path, data):
        path.unlink()
        path.write_bytes(data)

    def bundle(self):
        return A.audit_bundle(self.root,self.contract,self.records,self.policy['canonical']['seal_sha256'])

    def test_wrong_export_dimensions_rejected(self):
        m=A.load(self.base/'manifest.json');s=m['slides'][0]
        file=self.base/s['final_file'];self.replace(file,png(100,100))
        s['final_sha256']=A.digest(file)
        self.replace(self.base/'manifest.json',json.dumps(m).encode())
        with self.assertRaisesRegex(A.AuditError,'PNG dimension mismatch'):self.bundle()

    def test_visible_copy_tamper_rejected_even_with_updated_hash(self):
        m=A.load(self.base/'manifest.json');s=m['slides'][0]
        file=self.base/s['source_file']
        content=file.read_text().replace('>Üniversite için</text>','>Yanlış metin</text>')
        self.replace(file,content.encode());s['source_sha256']=A.digest(file)
        self.replace(self.base/'manifest.json',json.dumps(m).encode())
        with self.assertRaisesRegex(A.AuditError,'visible SVG copy mismatch'):self.bundle()

    def test_unapproved_logo_hash_rejected(self):
        m=A.load(self.base/'manifest.json');m['slides'][0]['canonical_lockup_sha256']='0'*64
        self.replace(self.base/'manifest.json',json.dumps(m).encode())
        with self.assertRaisesRegex(A.AuditError,'unapproved lockup hash'):self.bundle()

    def test_stale_zip_manifest_rejected(self):
        m=A.load(self.base/'manifest.json');m['title']='Updated outside ZIP'
        self.replace(self.base/'manifest.json',json.dumps(m).encode())
        with self.assertRaisesRegex(A.AuditError,'ZIP manifest differs'):self.bundle()

if __name__ == '__main__': unittest.main()

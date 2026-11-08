"""Branch/identity rejection tests; no image generation, rendering or network."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('work_preflight', Path(__file__).parents[1]/'preflight.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        brand = self.root/'brands/test-brand'
        brand.mkdir(parents=True)
        (brand/'seal.svg').write_bytes(b'<svg/>')
        (brand/'decision.md').write_text('Existing human approval fixture')
        self.metadata = {'slug': 'test-brand', 'canonicalLogo': {
            'locked': True, 'path': 'brands/test-brand/seal.svg',
            'sha256': hashlib.sha256(b'<svg/>').hexdigest(),
            'decisionRecord': 'brands/test-brand/decision.md'}}
        self.write_metadata()
        self.git('add', '.')
        self.git('commit', '-m', 'Fixture')
        self.git('switch', '-c', 'publish/work-test')
        self.fake_runtime = patch.object(P, 'runtime', return_value={'render_prerequisites_present': False})
        self.fake_runtime.start()
        self.addCleanup(self.fake_runtime.stop)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def write_metadata(self):
        (self.root/'brands/test-brand/brand.json').write_text(json.dumps(self.metadata))

    def test_preflight_preserves_dirty_files_and_branch(self):
        file = self.root/'other-executor.txt'
        file.write_text('in progress')
        before = self.git('status', '--porcelain')
        result = P.check(self.root, 'test-brand')
        self.assertEqual(result['locked_files_checked'], 1)
        self.assertTrue(result['warnings'])
        self.assertEqual(before, self.git('status', '--porcelain'))
        self.assertEqual(file.read_text(), 'in progress')
        self.assertEqual(self.git('branch', '--show-current'), 'publish/work-test')

    def test_main_is_rejected_for_production_but_readable(self):
        self.git('switch', 'main')
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')
        self.assertEqual(P.check(self.root, 'test-brand', read_only=True)['status'], 'PASS')

    def test_detached_head_rejected(self):
        self.git('checkout', '--detach')
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')

    def test_opencode_branch_works(self):
        self.git('switch', '-c', 'publish/opencode-test')
        self.assertEqual(P.check(self.root, 'test-brand')['status'], 'PASS')

    def test_altered_canonical_source_rejected(self):
        (self.root/'brands/test-brand/seal.svg').write_text('altered')
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')

    def test_identity_path_escape_rejected(self):
        self.metadata['canonicalLogo']['path'] = '../outside'
        self.write_metadata()
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            file = Path(outside)/'seal.svg'
            file.write_bytes(b'<svg/>')
            link = self.root/'brands/test-brand/seal.svg'
            link.unlink()
            link.symlink_to(file)
            with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')

    def test_brand_mismatch_and_traversal_rejected(self):
        self.metadata['slug'] = 'another-brand'
        self.write_metadata()
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')
        with self.assertRaises(P.PreflightError): P.check(self.root, '../test-brand')

    def test_missing_render_runtime_rejected(self):
        with self.assertRaises(P.PreflightError):
            P.check(self.root, 'test-brand', require_render=True)

    def test_lockup_tampering_rejected(self):
        base = self.root/'brands/test-brand'
        (base/'lockup.svg').write_bytes(b'<svg>lockup</svg>')
        manifest = {'brand_id': 'test-brand', 'status': 'APPROVED / CANONICAL',
                    'canonical_seal_sha256': self.metadata['canonicalLogo']['sha256'],
                    'records': [{'canonical_lockup_id': 'P-01/light',
                                 'canonical_file_path': 'brands/test-brand/lockup.svg',
                                 'sha256': hashlib.sha256(b'<svg>lockup</svg>').hexdigest()}]}
        file = base/'manifest.json'
        file.write_text(json.dumps(manifest))
        self.metadata['canonicalLockups'] = {'locked': True,
            'manifest': 'brands/test-brand/manifest.json',
            'manifestSha256': hashlib.sha256(file.read_bytes()).hexdigest()}
        self.write_metadata()
        self.assertEqual(P.check(self.root, 'test-brand')['locked_files_checked'], 2)
        (base/'lockup.svg').write_bytes(b'changed')
        with self.assertRaises(P.PreflightError): P.check(self.root, 'test-brand')


if __name__ == '__main__':
    unittest.main()

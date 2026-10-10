"""Explicit large-file pruning with real independent Git stores and no internet."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('bulk_prune', Path(__file__).parents[1]/'legacy_bulk_prune.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class BulkPruneTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        cfg = self.root/'gitconfig'
        cfg.write_text('[user]\n name = Fixture\n email = fixture@example.invalid\n'
                       '[core]\n hooksPath = /dev/null\n[commit]\n gpgSign = false\n')
        env = patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': str(cfg), 'GIT_CONFIG_NOSYSTEM': '1',
                                     'GIT_ALLOW_PROTOCOL': 'file', 'GIT_TERMINAL_PROMPT': '0'})
        env.start()
        self.addCleanup(env.stop)
        self.target = self.root/'legacy'
        self.source = self.root/'independent'
        self.remote = self.root/'remote.git'
        self.git(self.root, 'init', '-b', 'main', str(self.target))
        (self.target/'.gitignore').write_text('_archive/\nshare/\n')
        (self.target/'AGENTS.md').write_text('Keep shared instructions\n')
        (self.target/'image.png').write_bytes(b'a' * P.MIN_BYTES)
        (self.target/'small.png').write_bytes(b'small source')
        (self.target/'odd[1].png').write_bytes(b'b' * P.MIN_BYTES)
        self.git(self.target, 'add', '.')
        self.git(self.target, 'commit', '-m', 'Archive fixture')
        self.git(self.root, 'clone', '--bare', str(self.target), str(self.remote))
        self.git(self.root, 'clone', str(self.remote), str(self.source))
        self.sha = self.git(self.source, 'rev-parse', 'HEAD')
        (self.target/'_archive').mkdir()
        (self.target/'_archive/copied.png').write_bytes((self.target/'image.png').read_bytes())
        (self.target/'_archive/unique.png').write_bytes(b'c' * P.MIN_BYTES)
        (self.target/'share').mkdir()
        (self.target/'share/image.png').write_bytes((self.target/'image.png').read_bytes())

    def git(self, root, *args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()

    def plan(self):
        return P.plan(self.target, self.source, self.sha)

    def test_verified_plan_does_not_delete_and_keeps_protected_small_unique_files(self):
        manifest = self.plan()
        self.assertEqual(manifest['file_count'], 3)
        self.assertEqual(manifest['independently_verified_blobs'], 2)
        self.assertTrue((self.target/'image.png').exists())
        self.assertEqual(manifest['retained_unverified'][0]['path'], '_archive/unique.png')
        self.assertNotIn('small.png', {c['path'] for c in manifest['files']})
        self.assertNotIn('share/image.png', {c['path'] for c in manifest['files']})

    def test_apply_removes_only_archived_large_files_and_preserves_clean_git_and_linked_worktree(self):
        other = self.root/'other-worktree'
        self.git(self.target, 'worktree', 'add', '-b', 'other', str(other))
        before = self.git(other, 'status', '--porcelain')
        manifest = self.plan()
        result = P.apply(self.target, self.source, manifest)
        self.assertEqual(result['bytes_removed'], 3 * P.MIN_BYTES)
        for name in ('image.png', 'odd[1].png', '_archive/copied.png'):
            self.assertFalse((self.target/name).exists())
        for name in ('AGENTS.md', 'small.png', '_archive/unique.png', 'share/image.png'):
            self.assertTrue((self.target/name).exists())
        self.assertTrue((self.target/'.git').is_dir())
        self.assertTrue((other/'image.png').exists())
        self.assertEqual(self.git(other, 'status', '--porcelain'), before)
        self.assertEqual(self.git(self.target, 'status', '--porcelain'), '')
        self.assertEqual(self.git(self.source, 'status', '--porcelain'), '')

    def test_local_change_after_plan_blocks_all_deletion(self):
        manifest = self.plan()
        (self.target/'_archive/copied.png').write_bytes(b'x' * P.MIN_BYTES)
        with self.assertRaisesRegex(P.Stop, 'changed after'):
            P.apply(self.target, self.source, manifest)
        self.assertTrue((self.target/'image.png').exists())

    def test_tampered_plan_cannot_delete_protected_files(self):
        manifest = self.plan()
        manifest['files'][0]['path'] = 'share/image.png'
        with self.assertRaisesRegex(P.Stop, 'Protected'):
            P.apply(self.target, self.source, manifest)
        self.assertTrue((self.target/'image.png').exists())
        self.assertTrue((self.target/'share/image.png').exists())

    def test_tracked_classification_tampering_is_rejected(self):
        manifest = self.plan()
        for c in manifest['files']:
            if c['path'] == 'image.png':
                c['tracked'] = False
        with self.assertRaisesRegex(P.Stop, 'Invalid plan'):
            P.apply(self.target, self.source, manifest)
        self.assertTrue((self.target/'image.png').exists())

    def test_shared_git_store_cannot_be_independent_proof(self):
        other = self.root/'other-worktree'
        self.git(self.target, 'worktree', 'add', '-b', 'other', str(other))
        with self.assertRaisesRegex(P.Stop, 'independent'):
            P.plan(self.target, other, self.sha)

    def test_dirty_target_and_existing_sparse_rules_are_not_overwritten(self):
        (self.target/'AGENTS.md').write_text('User work\n')
        with self.assertRaisesRegex(P.Stop, 'user changes'):
            self.plan()
        self.assertTrue((self.target/'image.png').exists())
        self.git(self.target, 'add', 'AGENTS.md')
        self.git(self.target, 'commit', '-m', 'Explicit fixture update')
        self.git(self.target, 'sparse-checkout', 'set', '--no-cone', '/*')
        with self.assertRaisesRegex(P.Stop, 'already sparse'):
            self.plan()

    def test_symlink_candidate_cannot_escape_target(self):
        manifest = self.plan()
        (self.target/'_archive/copied.png').unlink()
        (self.target/'_archive/copied.png').symlink_to(self.source/'image.png')
        with self.assertRaisesRegex(P.Stop, 'symlink'):
            P.apply(self.target, self.source, manifest)
        self.assertTrue((self.source/'image.png').exists())

    def test_remote_byte_mismatch_is_rejected_before_any_deletion(self):
        original = P.git
        def corrupt(root, *args, **kwargs):
            if args[:2] == ('cat-file', 'blob'):
                return b'wrong remote bytes'
            return original(root, *args, **kwargs)
        with patch.object(P, 'git', side_effect=corrupt), self.assertRaisesRegex(P.Stop, 'blob identity'):
            self.plan()
        self.assertTrue((self.target/'image.png').exists())


if __name__ == '__main__':
    unittest.main()

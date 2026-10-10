"""Disposable-clone preservation tests using real Git and local-only remotes."""
import hashlib
import contextlib
import io
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('work_ephemeral', Path(__file__).parents[1]/'ephemeral.py')
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


class EphemeralTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name).resolve()
        # Isolate user configuration, hooks, signing and credentials. Git itself
        # rejects all non-file protocols, so these fixtures cannot use the internet.
        config = self.fixture/'gitconfig'
        config.write_text('[user]\n name = Fixture\n email = fixture@example.invalid\n'
                          '[core]\n hooksPath = /dev/null\n'
                          '[commit]\n gpgSign = false\n')
        environment = {
            'GIT_CONFIG_GLOBAL': str(config), 'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_ALLOW_PROTOCOL': 'file', 'GIT_TERMINAL_PROMPT': '0',
            'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
            'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
        }
        self.previous_environment = {key: os.environ.get(key) for key in environment}
        os.environ.update(environment)
        self.addCleanup(self.restore_environment)
        self.seed = self.fixture/'legacy'
        self.remote = self.fixture/'remote.git'
        self.git(self.fixture, 'init', '-b', 'main', str(self.seed))
        self.git(self.seed, 'config', 'user.name', 'Fixture')
        self.git(self.seed, 'config', 'user.email', 'fixture@example.invalid')
        self.git(self.seed, 'config', 'core.filemode', 'true')
        (self.seed/'.gitignore').write_text(
            '.venv/\nnode_modules/\n.cache/\nstudio/cloud/node_modules/\nignored/\n')
        (self.seed/'tracked.txt').write_text('original tracked bytes\n')
        (self.seed/'odd\tname\n.txt').write_text('unusual filename\n')
        (self.seed/'run.sh').write_text('#!/bin/sh\nexit 0\n')
        (self.seed/'run.sh').chmod(0o755)
        (self.seed/'included').mkdir()
        (self.seed/'included/asset.txt').write_text('visible asset\n')
        (self.seed/'excluded').mkdir()
        (self.seed/'excluded/archive.txt').write_text('sparse but durable\n')
        (self.seed/'link').symlink_to('tracked.txt')
        (self.seed/'directory-link').symlink_to('included', target_is_directory=True)
        self.git(self.seed, 'add', '.')
        self.git(self.seed, 'commit', '-m', 'Fixture')
        self.git(self.fixture, 'clone', '--bare', str(self.seed), str(self.remote))
        self.remote_url = self.remote.as_uri()
        self.manager = E.Manager(self.fixture/'owned')
        self.manager.init()

    def restore_environment(self):
        for key, value in self.previous_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def git(self, path, *args, binary=False):
        result = subprocess.run(['git', '-C', str(path), *args], check=True,
                                capture_output=True)
        return result.stdout if binary else result.stdout.decode().strip()

    def start(self, task='alpha', paths=(), executor='opencode'):
        # Only URL validation is substituted; cloning, inspection, pushing,
        # fresh-object verification and deletion all use the implementation.
        with patch.object(E, 'repo_url', return_value=self.remote_url) as local_url:
            result = self.manager.start(task, 'https://github.com/fixture/repository',
                                        paths=paths, executor=executor)
        local_url.assert_called_once_with('https://github.com/fixture/repository')
        path = Path(result['path'])
        self.git(path, 'config', 'core.filemode', 'true')
        return path

    def commit(self, path, message='Explicit task commit'):
        self.git(path, 'add', '-A')
        self.git(path, 'commit', '-m', message)
        return self.git(path, 'rev-parse', 'HEAD')

    def published(self, task='alpha', paths=()):
        path = self.start(task, paths)
        (path/'tracked.txt').write_text('explicitly committed task bytes\n')
        sha = self.commit(path)
        result = self.manager.publish(task)
        self.assertEqual(result['status'], 'pushed')
        self.assertEqual(result['sha'], sha)
        return path

    def record(self, task='alpha'):
        return self.manager.root/'records'/f'{task}.json'

    def assert_retained(self, task='alpha', reason=None, discard_runtime=False):
        record = self.record(task)
        before = record.read_bytes()
        path = self.manager.root/'tasks'/task
        with self.assertRaisesRegex(E.Stop, reason or '.*'):
            self.manager.cleanup(task, apply=True, discard_runtime=discard_runtime)
        self.assertTrue(path.is_dir())
        self.assertEqual(record.read_bytes(), before)

    def test_init_is_private_owned_and_idempotent(self):
        root = self.manager.root
        before = (root/'owner.json').read_bytes()
        self.assertEqual(self.manager.init()['status'], 'ready')
        self.assertEqual((root/'owner.json').read_bytes(), before)
        self.assertEqual(root.stat().st_mode & 0o777, 0o700)
        self.assertEqual((root/'tasks').stat().st_mode & 0o777, 0o700)
        self.assertEqual((root/'records').stat().st_mode & 0o777, 0o700)
        self.assertEqual(json.loads(before)['uid'], os.getuid())

    def test_init_refuses_existing_unowned_directory(self):
        root = self.fixture/'unowned'
        root.mkdir(mode=0o700)
        (root/'valuable.txt').write_text('legacy work')
        with self.assertRaisesRegex(E.Stop, 'will not adopt'):
            E.Manager(root).init()
        self.assertEqual((root/'valuable.txt').read_text(), 'legacy work')
        self.assertEqual(list(root.iterdir()), [root/'valuable.txt'])

    def test_init_refuses_root_symlink_including_dangling_link(self):
        for target in (self.seed, self.fixture/'missing'):
            with self.subTest(target=target):
                link = self.fixture/'root-link'
                link.symlink_to(target, target_is_directory=True)
                try:
                    with self.assertRaisesRegex(E.Stop, 'Root symlinks'):
                        E.Manager(link)
                    self.assertTrue(link.is_symlink())
                finally:
                    link.unlink()

    def test_owned_root_refuses_symlink_manager_paths(self):
        for name in ('owner.json', 'tasks', 'records', '.lock'):
            with self.subTest(name=name):
                root = self.fixture/f'owned-{name.replace(".", "-")}'
                manager = E.Manager(root)
                manager.init()
                path = root/name
                if path.exists():
                    path.rename(root/(name+'-original'))
                path.symlink_to(self.seed)
                with self.assertRaisesRegex(E.Stop, 'may not be symlinks'):
                    manager.init()
                self.assertTrue(path.is_symlink())

    def test_owned_root_refuses_nonprivate_permissions(self):
        self.manager.root.chmod(0o755)
        with self.assertRaisesRegex(E.Stop, 'private'):
            self.manager.init()

    def test_repo_url_validation_remains_unmocked_outside_start(self):
        self.assertEqual(E.repo_url('https://github.com/owner/repo'),
                         'https://github.com/owner/repo.git')
        for value in (self.remote_url, 'https://token@github.com/owner/repo',
                      'https://github.com/owner/repo?token=secret', 'git@github.com:owner/repo'):
            with self.subTest(value=value), self.assertRaises(E.Stop):
                E.repo_url(value)

    def test_start_creates_independent_clone_and_task_record(self):
        path = self.start(executor='codex')
        rec = json.loads(self.record().read_text())
        self.assertTrue((path/'.git').is_dir())
        self.assertFalse((path/'.git/objects/info/alternates').exists())
        self.assertNotEqual(self.git(path, 'rev-parse', '--absolute-git-dir'),
                            self.git(self.seed, 'rev-parse', '--absolute-git-dir'))
        self.assertEqual(self.git(path, 'branch', '--show-current'), 'publish/codex-alpha')
        self.assertEqual(self.git(path, 'rev-parse', '--is-shallow-repository'), 'true')
        self.assertEqual(rec['state'], 'active')
        self.assertEqual(rec['branch'], 'publish/codex-alpha')
        self.assertEqual(rec['base_ref'], 'main')
        self.assertEqual(rec['repo'], self.remote_url)
        self.assertEqual(rec['base_sha'], self.git(self.seed, 'rev-parse', 'HEAD'))
        self.assertEqual(self.git(self.seed, 'branch', '--show-current'), 'main')
        self.assertEqual(self.git(self.seed, 'status', '--porcelain'), '')

    def test_start_refuses_reused_task_id_without_changes(self):
        path = self.start()
        before = self.record().read_bytes()
        with self.assertRaisesRegex(E.Stop, 'already used'):
            self.start()
        self.assertEqual(self.record().read_bytes(), before)
        self.assertTrue(path.is_dir())

    def test_publish_requires_explicit_commit(self):
        path = self.start()
        with self.assertRaisesRegex(E.Stop, 'No task commit'):
            self.manager.publish('alpha')
        self.assertEqual(self.git(self.remote, 'for-each-ref', 'refs/heads/publish'), '')
        self.assertTrue(path.is_dir())

    def test_dirty_tracked_bytes_block_publish_check_and_cleanup(self):
        path = self.published()
        (path/'tracked.txt').write_text('unique uncommitted work')
        before = self.record().read_bytes()
        for operation in (self.manager.publish, self.manager.check):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(E.Stop, 'Uncommitted bytes'):
                    operation('alpha')
        self.assert_retained(reason='Uncommitted bytes')
        self.assertEqual((path/'tracked.txt').read_text(), 'unique uncommitted work')
        self.assertEqual(self.record().read_bytes(), before)

    def test_assume_unchanged_cannot_hide_unique_tracked_bytes(self):
        path = self.published()
        self.git(path, 'update-index', '--assume-unchanged', 'tracked.txt')
        (path/'tracked.txt').write_text('hidden unique bytes')
        self.assertEqual(self.git(path, 'status', '--porcelain'), '')
        self.assert_retained(reason='Uncommitted bytes')
        self.assertEqual((path/'tracked.txt').read_text(), 'hidden unique bytes')

    def test_untracked_and_ignored_unique_files_are_not_discarded(self):
        path = self.published()
        for relative in ('unique.txt', 'ignored/unique.bin'):
            with self.subTest(relative=relative):
                file = path/relative
                file.parent.mkdir(exist_ok=True)
                file.write_bytes(b'unarchived unique data\x00')
                if relative.startswith('ignored/'):
                    self.git(path, 'check-ignore', '--quiet', relative)
                    self.assertEqual(self.git(path, 'status', '--porcelain'), '')
                self.assert_retained(reason='Unarchived file', discard_runtime=True)
                self.assertEqual(file.read_bytes(), b'unarchived unique data\x00')
                file.unlink()

    def test_deleted_tracked_file_blocks_cleanup(self):
        path = self.published()
        (path/'tracked.txt').unlink()
        self.assert_retained(reason='Tracked files missing')
        self.assertFalse((path/'tracked.txt').exists())

    def test_staged_changes_require_explicit_commit(self):
        path = self.published()
        (path/'tracked.txt').write_text('staged task work')
        self.git(path, 'add', 'tracked.txt')
        staged = self.git(path, 'diff', '--cached', binary=True)
        with self.assertRaisesRegex(E.Stop, 'Staged changes'):
            self.manager.publish('alpha')
        self.assert_retained(reason='Staged changes')
        self.assertEqual(self.git(path, 'diff', '--cached', binary=True), staged)

    def test_executable_mode_changes_block_cleanup_even_with_filemode_disabled(self):
        path = self.published()
        self.git(path, 'config', 'core.filemode', 'false')
        for relative, mode in (('tracked.txt', 0o755), ('run.sh', 0o644)):
            with self.subTest(relative=relative):
                file = path/relative
                original = file.stat().st_mode & 0o777
                file.chmod(mode)
                self.assertEqual(self.git(path, 'status', '--porcelain'), '')
                self.assert_retained(reason='File mode changed')
                self.assertEqual(file.stat().st_mode & 0o777, mode)
                file.chmod(original)

    def test_symlink_target_changes_block_cleanup(self):
        path = self.published()
        link = path/'link'
        link.unlink()
        link.symlink_to('run.sh')
        self.assert_retained(reason='Uncommitted bytes')
        self.assertEqual(os.readlink(link), 'run.sh')

    def test_regular_file_replacing_tracked_symlink_blocks_cleanup(self):
        path = self.published()
        (path/'link').unlink()
        (path/'link').write_text('tracked.txt')
        self.assert_retained(reason='File mode changed')
        self.assertFalse((path/'link').is_symlink())

    def test_unexpected_symlink_is_not_followed_or_deleted(self):
        path = self.published()
        outside = self.fixture/'outside.txt'
        outside.write_text('outside work')
        (path/'tracked.txt').unlink()
        (path/'tracked.txt').symlink_to(outside)
        self.assert_retained(reason='Unexpected symlink')
        self.assertEqual(outside.read_text(), 'outside work')

    def test_missing_remote_task_branch_blocks_cleanup(self):
        path = self.start()
        self.assert_retained(reason='Exact task HEAD not found')
        self.assertTrue(path.is_dir())

    def test_unavailable_remote_preserves_files(self):
        path = self.published()
        self.remote.rename(self.fixture/'remote-offline.git')
        self.assert_retained(reason='operation failed')
        self.assertEqual((path/'tracked.txt').read_text(), 'explicitly committed task bytes\n')

    def test_wrong_branch_blocks_publish_and_cleanup(self):
        path = self.published()
        self.git(path, 'switch', '-c', 'publish/other')
        with self.assertRaisesRegex(E.Stop, 'Task branch mismatch'):
            self.manager.publish('alpha')
        self.assert_retained(reason='Task branch mismatch')
        self.assertEqual(self.git(path, 'branch', '--show-current'), 'publish/other')

    def test_changed_origin_blocks_publish_and_cleanup(self):
        path = self.published()
        other = self.fixture/'other.git'
        self.git(self.fixture, 'clone', '--bare', str(self.remote), str(other))
        self.git(path, 'remote', 'set-url', 'origin', other.as_uri())
        with self.assertRaisesRegex(E.Stop, 'Origin changed'):
            self.manager.publish('alpha')
        self.assert_retained(reason='Origin changed')
        self.assertEqual(self.git(path, 'remote', 'get-url', 'origin'), other.as_uri())

    def test_check_dry_run_and_apply_cleanup_keep_durable_receipt(self):
        path = self.published()
        before = self.record().read_bytes()
        checked = self.manager.check('alpha')
        dry = self.manager.cleanup('alpha')
        self.assertEqual(checked['status'], 'verified')
        self.assertEqual(dry['status'], 'dry-run; nothing deleted')
        self.assertEqual(dry['sha'], checked['sha'])
        self.assertTrue(path.is_dir())
        self.assertEqual(self.record().read_bytes(), before)
        result = self.manager.cleanup('alpha', apply=True)
        self.assertEqual(result['status'], 'cleaned; GitHub branch/PR preserved')
        self.assertFalse(path.exists())
        record = json.loads(self.record().read_text())
        self.assertEqual(record['state'], 'cleaned')
        self.assertEqual(record['receipt']['sha'], checked['sha'])
        self.assertEqual(record['receipt']['sha256_inventory_digest'],
                         checked['sha256_inventory_digest'])
        self.assertEqual(self.git(self.remote, 'rev-parse', 'refs/heads/publish/opencode-alpha'),
                         result['sha'])
        with self.assertRaisesRegex(E.Stop, 'independent owned clones'):
            self.manager.cleanup('alpha', apply=True)
        with self.assertRaisesRegex(E.Stop, 'already used'):
            self.start()

    def test_unpushed_local_branch_advance_blocks_cleanup(self):
        path = self.published()
        (path/'tracked.txt').write_text('new committed but unpushed work\n')
        sha = self.commit(path)
        self.assert_retained(reason='Exact task HEAD not found')
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), sha)
        self.manager.publish('alpha')
        self.assertEqual(self.manager.check('alpha')['sha'], sha)

    def test_remote_branch_advance_blocks_cleanup_and_nonfastforward_publish(self):
        path = self.published()
        branch = 'publish/opencode-alpha'
        self.git(self.seed, 'fetch', str(self.remote), f'refs/heads/{branch}')
        self.git(self.seed, 'switch', '-c', branch, 'FETCH_HEAD')
        (self.seed/'tracked.txt').write_text('another executor advanced remote\n')
        remote_sha = self.commit(self.seed, 'Remote advance')
        self.git(self.seed, 'push', str(self.remote), f'HEAD:refs/heads/{branch}')
        self.assert_retained(reason='Exact task HEAD not found')
        (path/'tracked.txt').write_text('divergent local commit\n')
        local_sha = self.commit(path, 'Local divergence')
        with self.assertRaisesRegex(E.Stop, 'operation failed'):
            self.manager.publish('alpha')
        self.assertEqual(self.git(path, 'rev-parse', 'HEAD'), local_sha)
        self.assertEqual(self.git(self.remote, 'rev-parse', f'refs/heads/{branch}'), remote_sha)
        self.assert_retained(reason='Exact task HEAD not found')

    def test_sparse_proof_hashes_all_tracked_blobs_not_only_materialized_files(self):
        path = self.published(paths=('included',))
        self.assertFalse((path/'excluded/archive.txt').exists())
        self.assertIn('S excluded/archive.txt', self.git(path, 'ls-files', '-t'))
        proof = self.manager.check('alpha')
        hashes = {}
        for entry in self.git(path, 'ls-tree', '-r', '-z', 'HEAD', binary=True).split(b'\0'):
            if not entry:
                continue
            fields, name = entry.split(b'\t', 1)
            oid = fields.decode().split()[2]
            data = self.git(path, 'cat-file', 'blob', oid, binary=True)
            hashes[os.fsdecode(name)] = hashlib.sha256(data).hexdigest()
        expected = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        self.assertEqual(proof['tracked_files'], len(hashes))
        self.assertEqual(proof['materialized_files'], len(hashes)-1)
        self.assertEqual(proof['sha256_inventory_digest'], expected)
        self.assertEqual(json.loads(self.record().read_text())['sparse_paths'], ['included'])
        self.manager.cleanup('alpha', apply=True)
        self.assertFalse(path.exists())

    def test_sparse_materialized_unique_bytes_cannot_hide_behind_skip_worktree(self):
        path = self.published(paths=('included',))
        file = path/'excluded/archive.txt'
        file.parent.mkdir()
        file.write_text('unique manually materialized sparse work\n')
        self.assert_retained(reason='Uncommitted bytes')
        self.assertEqual(file.read_text(), 'unique manually materialized sparse work\n')

    def test_ignored_runtimes_require_explicit_discard(self):
        path = self.published()
        for relative in sorted(E.RUNTIME):
            directory = path/relative
            directory.mkdir(parents=True)
            (directory/'cache.bin').write_bytes(b'local runtime bytes')
        self.assertEqual(self.git(path, 'status', '--porcelain'), '')
        self.assert_retained(reason='Unarchived file')
        proof = self.manager.check('alpha', discard_runtime=True)
        self.assertEqual(set(proof['discarded_runtime']), E.RUNTIME)
        dry = self.manager.cleanup('alpha', discard_runtime=True)
        self.assertEqual(set(dry['discarded_runtime']), E.RUNTIME)
        for relative in E.RUNTIME:
            self.assertEqual((path/relative/'cache.bin').read_bytes(), b'local runtime bytes')
        result = self.manager.cleanup('alpha', apply=True, discard_runtime=True)
        self.assertEqual(set(result['discarded_runtime']), E.RUNTIME)
        self.assertFalse(path.exists())

    def test_runtime_discard_refuses_nonignored_directory(self):
        path = self.published()
        (path/'.gitignore').write_text('ignored/\n')
        self.commit(path)
        self.manager.publish('alpha')
        (path/'node_modules').mkdir()
        (path/'node_modules/unique.txt').write_text('not ignored')
        self.assert_retained(reason='operation failed', discard_runtime=True)
        self.assertEqual((path/'node_modules/unique.txt').read_text(), 'not ignored')

    def test_runtime_discard_refuses_tracked_content(self):
        path = self.published()
        (path/'.venv').mkdir()
        (path/'.venv/tracked.txt').write_text('durable tracked runtime content')
        self.git(path, 'add', '-f', '.venv/tracked.txt')
        self.git(path, 'commit', '-m', 'Explicit tracked runtime')
        self.manager.publish('alpha')
        self.assert_retained(reason='contains tracked content', discard_runtime=True)
        self.assertEqual(self.manager.check('alpha')['discarded_runtime'], [])

    def test_lfs_pointer_blocks_publish_and_cleanup(self):
        path = self.published()
        (path/'large.bin').write_text('version https://git-lfs.github.com/spec/v1\n'
                                     'oid sha256:'+'a'*64+'\nsize 123\n')
        self.commit(path)
        with self.assertRaisesRegex(E.Stop, 'LFS'):
            self.manager.publish('alpha')
        # A manually pushed pointer is still not proof of durable LFS objects.
        self.git(path, 'push', 'origin', 'HEAD:refs/heads/publish/opencode-alpha')
        self.assert_retained(reason='LFS')
        self.assertTrue((path/'large.bin').exists())

    def test_sparse_lfs_pointer_blocks_fresh_remote_proof(self):
        (self.seed/'excluded/large.bin').write_text(
            'version https://git-lfs.github.com/spec/v1\noid sha256:'+'b'*64+'\nsize 456\n')
        self.commit(self.seed)
        self.git(self.seed, 'push', str(self.remote), 'HEAD:refs/heads/main')
        path = self.published(paths=('included',))
        self.assertFalse((path/'excluded/large.bin').exists())
        self.assert_retained(reason='LFS cleanup unsupported')

    def test_cleanup_blocks_current_task_directory_and_descendants(self):
        path = self.published()
        previous = Path.cwd()
        try:
            for current in (path, path/'included'):
                with self.subTest(current=current):
                    os.chdir(current)
                    self.assert_retained(reason='Leave the task directory')
        finally:
            os.chdir(previous)
        self.assertEqual(self.manager.cleanup('alpha')['status'], 'dry-run; nothing deleted')

    def test_cleanup_isolates_other_task_and_legacy_repository(self):
        alpha = self.published()
        beta = self.start('beta', executor='work')
        (beta/'tracked.txt').write_text('another task has unfinished work')
        (self.seed/'legacy-untracked.txt').write_text('legacy work must remain')
        beta_record = self.record('beta').read_bytes()
        legacy_status = self.git(self.seed, 'status', '--porcelain')
        legacy_head = self.git(self.seed, 'rev-parse', 'HEAD')
        self.manager.cleanup('alpha', apply=True)
        self.assertFalse(alpha.exists())
        self.assertEqual((beta/'tracked.txt').read_text(), 'another task has unfinished work')
        self.assertEqual(self.record('beta').read_bytes(), beta_record)
        self.assertEqual(self.git(self.seed, 'status', '--porcelain'), legacy_status)
        self.assertEqual(self.git(self.seed, 'rev-parse', 'HEAD'), legacy_head)
        self.assertEqual((self.seed/'legacy-untracked.txt').read_text(), 'legacy work must remain')
        self.assertTrue(self.manager.root.is_dir())
        self.assertTrue(self.remote.is_dir())

    def test_unknown_legacy_task_is_not_adopted_or_cleaned(self):
        legacy = self.manager.root/'tasks/legacy'
        legacy.mkdir()
        (legacy/'unique.txt').write_text('not an owned task')
        with self.assertRaisesRegex(E.Stop, 'legacy directories cannot be cleaned'):
            self.manager.cleanup('legacy', apply=True)
        self.assertEqual((legacy/'unique.txt').read_text(), 'not an owned task')

    def test_task_and_record_symlinks_are_refused(self):
        path = self.published()
        saved = path.with_name('alpha-saved')
        path.rename(saved)
        path.symlink_to(saved, target_is_directory=True)
        with self.assertRaisesRegex(E.Stop, 'Task symlink refused'):
            self.manager.cleanup('alpha', apply=True)
        self.assertTrue(saved.is_dir())
        path.unlink()
        saved.rename(path)
        record = self.record()
        saved_record = record.with_suffix('.saved')
        record.rename(saved_record)
        record.symlink_to(saved_record)
        with self.assertRaisesRegex(E.Stop, 'Record symlink refused'):
            self.manager.cleanup('alpha', apply=True)
        self.assertTrue(path.is_dir())
        self.assertTrue(saved_record.is_file())

    def test_stash_and_other_local_branch_work_block_cleanup(self):
        path = self.published()
        (path/'tracked.txt').write_text('unique stashed work')
        self.git(path, 'stash', 'push', '-m', 'preserve')
        self.assert_retained(reason='Unarchived stash')
        self.git(path, 'stash', 'pop')
        self.commit(path, 'Preserve stash in task')
        self.manager.publish('alpha')
        self.git(path, 'switch', '-c', 'publish/other-local')
        (path/'tracked.txt').write_text('unique other-branch work')
        self.commit(path)
        self.git(path, 'switch', 'publish/opencode-alpha')
        self.assert_retained(reason='operation failed')

    def test_amended_reflog_work_is_not_silently_discarded(self):
        path = self.published()
        (path/'tracked.txt').write_text('replacement')
        self.git(path, 'add', 'tracked.txt')
        self.git(path, 'commit', '--amend', '--no-edit')
        self.assert_retained(reason='Unarchived reflog')

    def test_cli_apply_requires_exact_pr_ci_gate(self):
        path = self.published()
        with patch.object(sys, 'argv', ['ephemeral', '--root', str(self.manager.root),
                                       'cleanup', 'alpha', '--apply']):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(E.main(), 1)
        self.assertTrue(path.exists())

    def test_pr_gate_rejects_wrong_head_closed_and_pending_ci(self):
        path = self.published()
        sha = self.git(path, 'rev-parse', 'HEAD')
        good = {'state': 'OPEN', 'headRefName': 'publish/opencode-alpha',
                'headRefOid': sha, 'baseRefName': 'main', 'isCrossRepository': False,
                'statusCheckRollup': [{'name': 'submitted-files', 'status': 'COMPLETED',
                                       'conclusion': 'SUCCESS'}]}
        real_run = E.run
        def stub(data):
            def call(args, **kwargs):
                if args[0] == 'gh':
                    return json.dumps(data)
                return real_run(args, **kwargs)
            return call
        with patch.object(E, 'run', side_effect=stub(good)):
            self.assertEqual(E.pr_gate(self.manager, 'alpha', 123), sha)
        changes = [{'state': 'CLOSED'}, {'headRefOid': '0'*40}, {'baseRefName': 'elsewhere'},
                   {'isCrossRepository': True}, {'headRefName': 'publish/other'},
                   {'statusCheckRollup': []},
                   {'statusCheckRollup': good['statusCheckRollup'] + [{'state': 'FAILURE'}]},
                   {'statusCheckRollup': [{'name': 'submitted-files', 'status': 'IN_PROGRESS'}]}]
        for change in changes:
            with self.subTest(change=change):
                with patch.object(E, 'run', side_effect=stub(dict(good, **change))):
                    with self.assertRaises(E.Stop):
                        E.pr_gate(self.manager, 'alpha', 123)
                self.assertTrue(path.exists())

    def test_cleanup_binds_ci_verified_sha(self):
        path = self.published()
        with self.assertRaisesRegex(E.Stop, 'CI-verified PR head'):
            self.manager.cleanup('alpha', apply=True, expected_sha='0'*40)
        self.assertTrue(path.exists())

    def test_new_host_does_not_reuse_an_existing_remote_task_branch(self):
        path = self.published()
        other = E.Manager(self.fixture/'other-owned')
        other.init()
        with patch.object(E, 'repo_url', return_value=self.remote_url):
            with self.assertRaisesRegex(E.Stop, 'already exists remotely'):
                other.start('alpha', 'https://github.com/fixture/repository')
        self.assertFalse((other.root/'tasks/alpha').exists())
        self.assertTrue(path.exists())

    def test_executor_handoff_uses_explicit_parent_branch_and_new_clone(self):
        source = self.published()
        source_sha = self.git(source, 'rev-parse', 'HEAD')
        with patch.object(E, 'repo_url', return_value=self.remote_url):
            result = self.manager.start('continuation', 'https://github.com/fixture/repository',
                                        base='publish/opencode-alpha', executor='codex')
        target = Path(result['path'])
        self.assertEqual(result['base_sha'], source_sha)
        self.assertEqual((source/'tracked.txt').read_bytes(), (target/'tracked.txt').read_bytes())
        (target/'handoff.txt').write_text('local executor simulation; not a Codex account test')
        target_sha = self.commit(target)
        self.manager.publish('continuation')
        self.assertEqual(self.git(self.remote, 'rev-parse', 'refs/heads/publish/opencode-alpha'), source_sha)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'refs/heads/publish/codex-continuation'), target_sha)
        self.manager.cleanup('alpha', apply=True)
        self.assertFalse(source.exists())
        self.assertTrue(target.exists())
        self.assertEqual(self.manager.check('continuation')['sha'], target_sha)

    def test_merged_pr_gate_requires_checked_head_and_main_ancestry(self):
        path = self.published()
        sha = self.git(path, 'rev-parse', 'HEAD')
        data = {'state': 'MERGED', 'headRefName': 'publish/opencode-alpha',
                'headRefOid': sha, 'baseRefName': 'main', 'isCrossRepository': False,
                'mergeCommit': {'oid': 'a'*40},
                'statusCheckRollup': [{'name': 'submitted-files', 'status': 'COMPLETED',
                                       'conclusion': 'SUCCESS'}]}
        real_run = E.run
        def stub(payload, comparison):
            def call(args, **kwargs):
                if args[:3] == ['gh', 'pr', 'view']:
                    return json.dumps(payload)
                if args[:2] == ['gh', 'api']:
                    self.assertTrue(args[2].endswith('/compare/'+'a'*40+'...main'))
                    return json.dumps({'status': comparison})
                return real_run(args, **kwargs)
            return call
        for state in ('ahead', 'identical'):
            with self.subTest(state=state), patch.object(E, 'run', side_effect=stub(data, state)):
                self.assertEqual(E.pr_gate(self.manager, 'alpha', 123), sha)
        for state in ('behind', 'diverged', 'unknown'):
            with self.subTest(state=state), patch.object(E, 'run', side_effect=stub(data, state)):
                with self.assertRaisesRegex(E.Stop, 'not in current main'):
                    E.pr_gate(self.manager, 'alpha', 123)
        for commit in (None, {'oid': 'invalid'}):
            with patch.object(E, 'run', side_effect=stub(dict(data, mergeCommit=commit), 'identical')):
                with self.assertRaisesRegex(E.Stop, 'no valid merge commit'):
                    E.pr_gate(self.manager, 'alpha', 123)
        for update in ({'headRefOid': 'b'*40}, {'statusCheckRollup': []}, {'state': 'CLOSED'}):
            with patch.object(E, 'run', side_effect=stub(dict(data, **update), 'identical')):
                with self.assertRaises(E.Stop):
                    E.pr_gate(self.manager, 'alpha', 123)
        self.assertTrue(path.exists())


if __name__ == '__main__':
    unittest.main()

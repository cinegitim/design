#!/usr/bin/env python3
"""Owned disposable clones. No auto staging, merging, or deletion of legacy repos."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

VERSION = 1
RUNTIME = {'.venv', 'node_modules', '.cache', 'studio/cloud/node_modules'}
BASELINE_FILES = {'AGENTS.md', 'README.md', '.gitignore', 'opencode.json', 'opencode.jsonc'}
BASELINE_DIRS = ('.opencode', '.agents', '.github', 'studio/work', 'studio/cloud',
                 'studio/templates', 'studio/references', 'studio/workflow', 'studio/tools')
BASELINE_EXT = {'.md', '.py', '.sh', '.json', '.jsonc', '.ts', '.js', '.mjs', '.txt', '.yml', '.yaml'}


def baseline_path(name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        return False
    if any(part in {'.git', '.venv', 'node_modules', '__pycache__', '.cache'}
           or part.startswith('.env') for part in p.parts):
        return False
    return name in BASELINE_FILES or (p.suffix in BASELINE_EXT or name == '.github/CODEOWNERS') and any(
        name.startswith(directory + '/') for directory in BASELINE_DIRS)


class Stop(RuntimeError):
    pass


def run(args, cwd=None, binary=False):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    if result.returncode:
        # Never print credential-bearing remote URLs or tool diagnostics.
        raise Stop(f'{args[0]} operation failed (exit {result.returncode}); files retained')
    return result.stdout if binary else result.stdout.decode().strip()


def git(path, *args, binary=False):
    return run(['git', '-C', str(path), *args], binary=binary)


def atomic(path, data):
    tmp = path.with_suffix('.tmp')
    with tmp.open('x') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def slug(value):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,70}', value):
        raise Stop('Use a lowercase task id/topic containing only letters, numbers, hyphens')
    return value


def repo_url(value):
    match = re.fullmatch(r'https://github\.com/([A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?', value)
    if not match:
        raise Stop('Repository must be a credential-free https://github.com/owner/repo URL')
    return f'https://github.com/{match[1]}/{match[2]}.git'


def safe_ref(value):
    if value != 'main' and not re.fullmatch(r'publish/[a-z0-9][a-z0-9/-]*', value):
        raise Stop('Base must be main or an explicitly selected publish/ branch')
    run(['git', 'check-ref-format', 'refs/heads/' + value])
    return value


class Baseline:
    """Persistent immutable source snapshots, not a shared Git object store."""
    def __init__(self, root, repo):
        raw = Path(root).expanduser().absolute()
        if raw.is_symlink():
            raise Stop('Baseline root symlinks refused')
        self.root = raw.resolve()
        self.repo = repo

    @contextlib.contextmanager
    def lock(self):
        if not self.root.exists():
            self.root.mkdir(parents=True, mode=0o700)
        if self.root.stat().st_uid != os.getuid() or self.root.stat().st_mode & 0o077:
            raise Stop('Baseline must be owned and private (mode 700)')
        marker = self.root/'owner.json'
        if not marker.exists():
            if any(self.root.iterdir()):
                raise Stop('Will not adopt a nonempty baseline directory')
            atomic(marker, {'version': VERSION, 'uid': os.getuid(), 'repo': self.repo})
            (self.root/'snapshots').mkdir(mode=0o700)
        for name in ('owner.json', 'snapshots', '.lock', 'active.json', 'ephemeral.py'):
            if (self.root/name).is_symlink():
                raise Stop('Baseline control symlink refused')
        if json.loads(marker.read_text()) != {'version': VERSION, 'uid': os.getuid(), 'repo': self.repo}:
            raise Stop('Baseline repository/ownership mismatch')
        with (self.root/'.lock').open('a') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield

    def current(self, rec=None, check_launcher=True):
        if rec is None:
            active = self.root/'active.json'
            if not active.exists():
                return None, {}
            rec = json.loads(active.read_text())
        digest = rec['digest']
        if not re.fullmatch('[a-f0-9]{64}', digest):
            raise Stop('Invalid baseline digest')
        snapshot = self.root/'snapshots'/digest
        if snapshot.is_symlink() or not snapshot.is_dir():
            raise Stop('Invalid baseline snapshot')
        entries = rec['files']
        if hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest() != digest:
            raise Stop('Baseline inventory changed')
        actual = set()
        for parent, dirs, files in os.walk(snapshot, followlinks=False):
            if any((Path(parent)/name).is_symlink() for name in dirs):
                raise Stop('Baseline directory symlink refused')
            for name in files:
                relative = (Path(parent)/name).relative_to(snapshot).as_posix()
                if relative not in entries or not baseline_path(relative):
                    raise Stop('Unrecorded baseline file; files retained')
                file = Path(parent)/name
                meta = entries[relative]
                if (file.is_symlink() or not file.is_file() or
                        bool(file.stat().st_mode & 0o111) != (meta['mode'] == '100755')):
                    raise Stop('Baseline file mode/type changed')
                data = file.read_bytes()
                oid = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                if oid != meta['oid'] or hashlib.sha256(data).hexdigest() != meta['sha256']:
                    raise Stop('Baseline bytes changed; preserve edits before recalibrating')
                actual.add(relative)
        if actual != set(entries):
            raise Stop('Baseline files missing')
        if check_launcher and rec.get('launcher_sha256'):
            launcher = self.root/'ephemeral.py'
            if not launcher.is_file() or hashlib.sha256(launcher.read_bytes()).hexdigest() != rec['launcher_sha256']:
                raise Stop('Installed launcher changed; preserve edits before recalibrating')
        return snapshot, rec

    def calibrate(self, source, sha):
        """Read only committed main tree, never dirty worktree bytes or PR sources."""
        with self.lock():
            old, rec = self.current()
            available = {meta['oid']: old/name for name, meta in rec.get('files', {}).items()}
            tree = {}
            for entry in git(source, 'ls-tree', '-r', '-z', sha, binary=True).split(b'\0'):
                if not entry:
                    continue
                fields, rawname = entry.split(b'\t', 1)
                mode, kind, oid = fields.decode().split()
                name = os.fsdecode(rawname)
                if baseline_path(name):
                    if kind != 'blob' or mode not in ('100644', '100755'):
                        raise Stop('Baseline sources must be regular committed files')
                    tree[name] = (mode, oid)
            if not tree or 'AGENTS.md' not in tree:
                raise Stop('Baseline requires committed AGENTS.md')
            missing = sorted({oid for _, oid in tree.values()} - set(available))
            if missing:
                # Prefetch only selected source blobs, not brand imagery or outputs.
                git(source, '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', '--no-tags',
                    '--no-write-fetch-head', 'origin', *missing)
            entries, contents = {}, {}
            for name, (mode, oid) in tree.items():
                data = available[oid].read_bytes() if oid in available else git(source, 'cat-file', 'blob', oid, binary=True)
                if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != oid:
                    raise Stop('Source blob mismatch')
                entries[name] = {'oid': oid, 'mode': mode, 'sha256': hashlib.sha256(data).hexdigest()}
                contents[name] = data
            digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
            snapshot = self.root/'snapshots'/digest
            if not snapshot.exists():
                with tempfile.TemporaryDirectory(prefix='prepare-', dir=self.root) as tmp:
                    prepared = Path(tmp)/'source'
                    prepared.mkdir()
                    for name, data in contents.items():
                        file = prepared/name
                        file.parent.mkdir(parents=True, exist_ok=True)
                        file.write_bytes(data)
                        file.chmod(0o555 if entries[name]['mode'] == '100755' else 0o444)
                    os.rename(prepared, snapshot)
            elif old != snapshot:
                self.current({'digest': digest, 'files': entries}, check_launcher=False)
            launcher_sha = None
            if 'studio/work/ephemeral.py' in contents:
                launcher = self.root/'ephemeral.py'
                if launcher.exists() and not rec.get('launcher_sha256'):
                    raise Stop('Unrecorded installed launcher; files retained')
                data = contents['studio/work/ephemeral.py']
                launcher_sha = hashlib.sha256(data).hexdigest()
                if launcher_sha != rec.get('launcher_sha256'):
                    with tempfile.NamedTemporaryFile(dir=self.root, delete=False) as f:
                        f.write(data)
                        temporary = Path(f.name)
                    temporary.chmod(0o444)
                    os.replace(temporary, launcher)
            atomic(self.root/'active.json', {'source_sha': sha, 'digest': digest, 'files': entries,
                                           'launcher_sha256': launcher_sha})
            self.current()
            return {'status': 'calibrated' if digest != rec.get('digest') else 'unchanged',
                    'source_sha': sha, 'digest': digest, 'path': str(snapshot),
                    'files': len(entries), 'loaded_blobs': len(missing),
                    'reused_blobs': len({oid for _, oid in tree.values()}) - len(missing),
                    'launcher': str(self.root/'ephemeral.py') if launcher_sha else None}

    def seed(self, destination):
        with self.lock():
            snapshot, rec = self.current()
            if snapshot is None:
                return 0
            for name, meta in rec['files'].items():
                # Independent objects: no alternates, hardlinks, or worktree symlinks.
                if git(destination, 'hash-object', '-w', '--no-filters', '--', str(snapshot/name)) != meta['oid']:
                    raise Stop('Baseline import mismatch')
            return len(rec['files'])


class Manager:
    def __init__(self, root):
        raw = Path(root).absolute()
        if raw.is_symlink():
            raise Stop('Root symlinks are not permitted')
        self.root = raw.resolve()

    def init(self):
        if self.root.exists() and any(self.root.iterdir()):
            # Idempotent only for a valid, previously owned root.
            self.validate()
            return {'status': 'ready', 'root': str(self.root), 'launcher': str(self.root/'control/ephemeral.py')}
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        atomic(self.root / 'owner.json', {'version': VERSION, 'id': str(uuid.uuid4()), 'uid': os.getuid()})
        for name in ('tasks', 'records', 'control'):
            (self.root / name).mkdir(mode=0o700)
        shutil.copyfile(__file__, self.root/'control/ephemeral.py')
        return {'status': 'ready', 'root': str(self.root), 'launcher': str(self.root/'control/ephemeral.py')}

    def validate(self):
        if not self.root.is_dir() or self.root.stat().st_uid != os.getuid():
            raise Stop('Root ownership mismatch')
        if self.root.stat().st_mode & 0o077:
            raise Stop('Owned root must be private (mode 700)')
        for name in ('owner.json', 'tasks', 'records', 'control', '.lock'):
            if (self.root / name).is_symlink():
                raise Stop('Manager paths may not be symlinks')
        try:
            data = json.loads((self.root / 'owner.json').read_text())
            if data['version'] != VERSION or data['uid'] != os.getuid():
                raise ValueError()
            uuid.UUID(data['id'])
            if not all((self.root / n).is_dir() for n in ('tasks', 'records')):
                raise ValueError()
        except (OSError, ValueError, KeyError):
            raise Stop('Not an owned ephemeral root; will not adopt existing directories')

    @contextlib.contextmanager
    def lock(self):
        self.validate()
        with (self.root / '.lock').open('a') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield

    def record(self, task):
        slug(task)
        p = self.root / 'records' / (task + '.json')
        if p.is_symlink():
            raise Stop('Record symlink refused')
        try:
            rec = json.loads(p.read_text())
        except (OSError, ValueError):
            raise Stop('Unknown task; legacy directories cannot be cleaned')
        path = self.root / 'tasks' / task
        if rec['task'] != task or rec['owner'] != json.loads((self.root / 'owner.json').read_text())['id']:
            raise Stop('Task ownership mismatch')
        if path.is_symlink() or path.resolve() != path:
            raise Stop('Task symlink refused')
        return p, path, rec

    def start(self, task, repo, base='main', executor='opencode', paths=(), baseline_root=None):
        slug(task)
        safe_ref(base)
        repo = repo_url(repo)
        branch = f'publish/{executor}-{task}'
        if baseline_root and Path(baseline_root).expanduser().resolve().is_relative_to(self.root):
            raise Stop('Persistent baseline must be outside the temporary manager root')
        with self.lock():
            record = self.root / 'records' / (task + '.json')
            path = self.root / 'tasks' / task
            if record.exists() or path.exists():
                raise Stop('Task id already used; no reuse of another task directory')
            for value in paths:
                p = Path(value)
                if p.is_absolute() or '..' in p.parts or value.startswith('-'):
                    raise Stop('Sparse paths must be repository-relative directories')
            if run(['git', 'ls-remote', '--heads', repo, 'refs/heads/'+branch]):
                raise Stop('Task branch already exists remotely; use a fresh task id')
            atomic(record, {'task': task, 'owner': json.loads((self.root/'owner.json').read_text())['id'],
                            'repo': repo, 'base_ref': base, 'branch': branch, 'executor': executor,
                            'state': 'starting'})
            # Independent clone: its objects disappear too. Never use legacy worktree stores.
            run(['git', '-c', 'core.autocrlf=false', 'clone', '--depth=1', '--single-branch', '--filter=blob:none',
                 '--no-checkout', '--branch', base, '--', repo, str(path)])
            baseline = None
            if baseline_root:
                cache = Baseline(baseline_root, repo)
                if base == 'main':
                    baseline = cache.calibrate(path, git(path, 'rev-parse', 'refs/remotes/origin/main'))
                cache.seed(path)
            if paths:
                git(path, 'sparse-checkout', 'set', '--cone', '--', *paths)
            git(path, 'checkout', '-b', branch, 'refs/remotes/origin/'+base)
            _, _, rec = self.record(task)
            rec.update(state='active', base_sha=git(path, 'rev-parse', 'HEAD'), sparse_paths=list(paths), baseline=baseline)
            atomic(record, rec)
            return {'status': 'active', 'task': task, 'path': str(path), 'branch': branch,
                    'base_sha': rec['base_sha'], 'baseline': baseline}

    def calibrate(self, repo, baseline_root):
        repo = repo_url(repo)
        if Path(baseline_root).expanduser().resolve().is_relative_to(self.root):
            raise Stop('Persistent baseline must be outside the temporary manager root')
        with self.lock(), tempfile.TemporaryDirectory(prefix='baseline-sync-', dir=self.root) as tmp:
            run(['git', 'clone', '--depth=1', '--single-branch', '--filter=blob:none',
                 '--no-checkout', '--branch', 'main', '--', repo, tmp])
            sha = git(tmp, 'rev-parse', 'refs/remotes/origin/main')
            return Baseline(baseline_root, repo).calibrate(tmp, sha)

    def inspect(self, path, rec, discard_runtime=False):
        if not path.is_dir() or not (path/'.git').is_dir() or (path/'.git').is_symlink():
            raise Stop('Only independent owned clones may be cleaned')
        if Path(git(path, 'rev-parse', '--show-toplevel')).resolve() != path:
            raise Stop('Repository path mismatch')
        if git(path, 'symbolic-ref', '--short', 'HEAD') != rec['branch']:
            raise Stop('Task branch mismatch')
        if git(path, 'remote', 'get-url', 'origin') != rec['repo']:
            raise Stop('Origin changed; refusing publish/cleanup')
        if git(path, 'rev-parse', '--show-object-format') != 'sha1':
            raise Stop('Only SHA-1 Git object format is supported by this verifier')
        if (path/'.git/objects/info/alternates').exists():
            raise Stop('Shared object stores are not permitted')
        if len(git(path, 'worktree', 'list', '--porcelain').split('worktree ')) != 2:
            raise Stop('Clone has linked worktrees; cleanup refused')
        if git(path, 'stash', 'list'):
            raise Stop('Unarchived stash remains')
        for marker in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'rebase-merge', 'rebase-apply'):
            if (path/'.git'/marker).exists():
                raise Stop('Git operation in progress')
        heads = git(path, 'for-each-ref', '--format=%(objectname)', 'refs/heads').splitlines()
        for sha in heads:
            git(path, 'merge-base', '--is-ancestor', sha, 'HEAD')
        for sha in set(git(path, 'reflog', '--all', '--format=%H').splitlines()):
            try:
                git(path, 'merge-base', '--is-ancestor', sha, 'HEAD')
            except Stop:
                raise Stop('Unarchived reflog commit remains; preserve it before cleanup')
        # Git status alone can miss assume-unchanged, ignored files and sparse materializations.
        tree = {}
        for entry in git(path, 'ls-tree', '-r', '-z', 'HEAD', binary=True).split(b'\0'):
            if not entry:
                continue
            fields, rawname = entry.split(b'\t', 1)
            mode, kind, oid = fields.decode().split()
            name = os.fsdecode(rawname)
            if kind != 'blob':
                raise Stop('Submodules are not supported by preservation verification')
            tree[name] = (mode, oid)
        if git(path, 'diff', '--cached', '--name-only'):
            raise Stop('Staged changes remain; commit explicitly before publish')
        sparse = set()
        for entry in git(path, 'ls-files', '-t', '-z', binary=True).split(b'\0'):
            if entry.startswith(b'S '):
                sparse.add(os.fsdecode(entry[2:]))
        inventory = {}
        runtime = []
        for parent, dirs, files in os.walk(path, followlinks=False):
            relparent = Path(parent).relative_to(path)
            if relparent == Path('.'):
                dirs.remove('.git')
            for name in dirs[:]:
                rel = (relparent/name).as_posix()
                if rel in RUNTIME and discard_runtime:
                    # Allow only ignored runtime trees; tracked content must remain verified.
                    if any(n == rel or n.startswith(rel+'/') for n in tree):
                        raise Stop('Runtime directory contains tracked content')
                    git(path, 'check-ignore', '--quiet', '--', rel+'/')
                    runtime.append(rel)
                    dirs.remove(name)
                elif (Path(parent)/name).is_symlink():
                    files.append(name)
                    dirs.remove(name)
            for name in files:
                file = Path(parent)/name
                rel = file.relative_to(path).as_posix()
                if rel not in tree:
                    raise Stop(f'Unarchived file remains: {rel}; include it or resolve explicitly')
                mode, oid = tree[rel]
                st = file.lstat()
                if stat.S_ISLNK(st.st_mode):
                    if mode != '120000':
                        raise Stop(f'Unexpected symlink: {rel}')
                    data = os.fsencode(os.readlink(file))
                elif stat.S_ISREG(st.st_mode):
                    if mode == '120000' or bool(st.st_mode & 0o111) != (mode == '100755'):
                        raise Stop(f'File mode changed: {rel}')
                    data = file.read_bytes()
                else:
                    raise Stop(f'Special file refused: {rel}')
                object_hash = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                if object_hash != oid:
                    raise Stop(f'Uncommitted bytes remain: {rel}')
                if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
                    raise Stop('LFS requires a separate durable-object verifier; cleanup blocked')
                inventory[rel] = hashlib.sha256(data).hexdigest()
        missing = set(tree) - set(inventory) - sparse
        if missing:
            raise Stop('Tracked files missing from working directory')
        if git(path, 'status', '--porcelain', '--untracked-files=all'):
            raise Stop('Worktree is not clean')
        return tree, inventory, runtime

    def remote_head(self, path, rec):
        result = git(path, 'ls-remote', '--heads', 'origin', 'refs/heads/'+rec['branch'])
        return result.split()[0] if result else None

    def publish(self, task, discard_runtime=False):
        with self.lock():
            record, path, rec = self.record(task)
            self.inspect(path, rec, discard_runtime)
            sha = git(path, 'rev-parse', 'HEAD')
            if sha == rec['base_sha']:
                raise Stop('No task commit to publish')
            # Normal fast-forward push only. Remote conflict fails without retry/force.
            git(path, 'push', 'origin', f'HEAD:refs/heads/{rec["branch"]}')
            if self.remote_head(path, rec) != sha:
                raise Stop('Remote head mismatch after push')
            rec.update(state='pushed', pushed_sha=sha)
            atomic(record, rec)
            return {'status': 'pushed', 'branch': rec['branch'], 'sha': sha,
                    'next': 'Open PR and follow the checked-delivery policy; no files deleted'}

    def proof(self, path, rec, discard_runtime=False):
        tree, inventory, runtime = self.inspect(path, rec, discard_runtime)
        head = git(path, 'rev-parse', 'HEAD')
        if self.remote_head(path, rec) != head:
            raise Stop('Exact task HEAD not found on remote; files retained')
        # Fresh object store, not a local ref/alternate. Fetch and verify remote bytes.
        with tempfile.TemporaryDirectory(prefix='verify-', dir=self.root) as tmp:
            remote = Path(tmp)
            run(['git', 'init', '-q', str(remote)])
            git(remote, 'fetch', '--depth=1', rec['repo'], 'refs/heads/'+rec['branch'])
            if git(remote, 'rev-parse', 'FETCH_HEAD') != head:
                raise Stop('Remote changed while verifying; files retained')
            git(remote, 'fsck', '--full', '--no-reflogs')
            if git(remote, 'ls-tree', '-r', '-z', 'FETCH_HEAD', binary=True) != git(path, 'ls-tree', '-r', '-z', 'HEAD', binary=True):
                raise Stop('Remote tree mismatch')
            # Hash every remote blob, including sparse files, not just materialized files.
            hashes = {}
            proc = subprocess.Popen(['git', '-C', str(remote), 'cat-file', '--batch'],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            try:
                for name, (_, oid) in tree.items():
                    proc.stdin.write((oid+'\n').encode()); proc.stdin.flush()
                    header = proc.stdout.readline().decode().split()
                    if len(header) != 3 or header[:2] != [oid, 'blob']:
                        raise Stop('Remote blob missing')
                    data = proc.stdout.read(int(header[2]))
                    if len(data) != int(header[2]) or proc.stdout.read(1) != b'\n':
                        raise Stop('Incomplete remote blob')
                    if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
                        raise Stop('LFS cleanup unsupported')
                    hashes[name] = hashlib.sha256(data).hexdigest()
                    if name in inventory and hashes[name] != inventory[name]:
                        raise Stop('Remote byte hash mismatch')
            finally:
                proc.stdin.close(); proc.stdout.close(); proc.wait()
            if proc.returncode:
                raise Stop('Remote object read failed')
        if self.remote_head(path, rec) != head:
            raise Stop('Remote head moved during verification')
        digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        return {'sha': head, 'tracked_files': len(tree), 'materialized_files': len(inventory),
                'sha256_inventory_digest': digest, 'discarded_runtime': runtime}

    def check(self, task, discard_runtime=False):
        with self.lock():
            _, path, rec = self.record(task)
            return dict(status='verified', **self.proof(path, rec, discard_runtime))

    def cleanup(self, task, apply=False, discard_runtime=False, expected_sha=None):
        with self.lock():
            record, path, rec = self.record(task)
            if Path.cwd().resolve() == path or path in Path.cwd().resolve().parents:
                raise Stop('Leave the task directory / move the session before cleanup')
            result = self.proof(path, rec, discard_runtime)
            if expected_sha and result['sha'] != expected_sha:
                raise Stop('HEAD no longer matches the CI-verified PR head')
            if not apply:
                return dict(status='dry-run; nothing deleted', **result)
            # Recheck local files immediately before deletion. User must stop writers first.
            self.inspect(path, rec, discard_runtime)
            if git(path, 'rev-parse', 'HEAD') != result['sha'] or self.remote_head(path, rec) != result['sha']:
                raise Stop('Head changed before cleanup')
            rec.update(state='verified-for-cleanup', receipt=result)
            atomic(record, rec)
            shutil.rmtree(path)  # Only owned task clone; never delete root/records/legacy repos.
            rec['state'] = 'cleaned'
            atomic(record, rec)
            return dict(status='cleaned; GitHub branch/PR preserved', task=task, **result)


def pr_gate(manager, task, number):
    """CLI delivery gate; cleanup never merges or closes PRs."""
    with manager.lock():
        _, path, rec = manager.record(task)
        repository = rec['repo'].removeprefix('https://github.com/').removesuffix('.git')
        data = json.loads(run(['gh', 'pr', 'view', str(number), '--repo', repository,
                               '--json', 'state,headRefName,headRefOid,baseRefName,isCrossRepository,statusCheckRollup,mergeCommit']))
        if (data['state'] not in ('OPEN', 'MERGED') or data['baseRefName'] != 'main' or data['isCrossRepository']
                or data['headRefName'] != rec['branch'] or data['headRefOid'] != git(path, 'rev-parse', 'HEAD')):
            raise Stop('PR is not the exact OPEN/MERGED task branch/head targeting main')
        checks = data['statusCheckRollup'] or []
        passed = any(c.get('name') == 'submitted-files' and c.get('status') == 'COMPLETED'
                     and c.get('conclusion') == 'SUCCESS' for c in checks)
        if not passed or any(c.get('conclusion') not in (None, '', 'SUCCESS', 'NEUTRAL', 'SKIPPED')
                             or c.get('status') in ('QUEUED', 'IN_PROGRESS', 'PENDING')
                             or c.get('state') not in (None, 'SUCCESS') for c in checks):
            raise Stop('Exact-head submitted-files CI has not passed; files retained')
        if data['state'] == 'MERGED':
            merge_sha = (data.get('mergeCommit') or {}).get('oid', '')
            if not re.fullmatch('[a-f0-9]{40}', merge_sha):
                raise Stop('MERGED PR has no valid merge commit; files retained')
            comparison = json.loads(run(['gh', 'api',
                                         f'repos/{repository}/compare/{merge_sha}...main']))
            if comparison.get('status') not in ('ahead', 'identical'):
                raise Stop('PR merge commit is not in current main history; files retained')
        return data['headRefOid']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = Path(__file__).resolve()
    installed_root = source.parent.parent if source.parent.name == 'control' else None
    default_root = installed_root if installed_root and (installed_root/'owner.json').is_file() else Path(tempfile.gettempdir())/'brand-studio-ephemeral'
    parser.add_argument('--root', default=os.environ.get('BRAND_STUDIO_TEMP_ROOT',
                       str(default_root)))
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    start = commands.add_parser('start')
    start.add_argument('task')
    start.add_argument('--repo', default='https://github.com/cinegitim/design.git')
    start.add_argument('--base', default='main')
    start.add_argument('--executor', choices=['opencode', 'codex', 'work'], default='opencode')
    start.add_argument('--paths', nargs='*', default=[])
    baseline_default = os.environ.get('BRAND_STUDIO_BASELINE_ROOT',
                                     str(Path.home()/'.local/share/brand-studio/baseline'))
    start.add_argument('--baseline-root', default=baseline_default)
    start.add_argument('--no-baseline', action='store_true', help='Use independent remote sources without local source reuse')
    calibrate = commands.add_parser('calibrate', help='Refresh persistent source baseline from current main')
    calibrate.add_argument('--repo', default='https://github.com/cinegitim/design.git')
    calibrate.add_argument('--baseline-root', default=baseline_default)
    for command in ('publish', 'check', 'cleanup'):
        sub = commands.add_parser(command)
        sub.add_argument('task')
        sub.add_argument('--discard-runtime', action='store_true', help='Exclude ignored dependency/cache directories; consent to discard them on cleanup')
        if command == 'cleanup':
            sub.add_argument('--apply', action='store_true', help='Delete ONLY after verification; default is dry run')
            sub.add_argument('--pr', type=int, help='Exact OPEN/MERGED PR number; required for --apply')
    args = vars(parser.parse_args())
    root = args.pop('root')
    command = args.pop('command')
    try:
        manager = Manager(root)
        if command == 'start' and args.pop('no_baseline'):
            args['baseline_root'] = None
        if command == 'cleanup':
            pr = args.pop('pr')
            if args['apply'] and not pr:
                raise Stop('--apply requires --pr and passing exact-head CI')
            if pr:
                args['expected_sha'] = pr_gate(manager, args['task'], pr)
        print(json.dumps(getattr(manager, command)(**args), indent=2))
    except (Stop, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'STOP; files retained', 'reason': str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

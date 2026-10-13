#!/usr/bin/env python3
"""Explicit, manifest-scoped local pruning; never deletes remote or shared Git files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

MIN_BYTES = 1024 * 1024
PROTECTED = {'.git', '.opencode', '.agents', '.github', 'studio', 'figma',
             'share', 'share-seal', 'share-runtime', '.venv', 'node_modules',
             '.cache', '__pycache__'}
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.zip', '.pdf', '.mp4', '.mov'}


class Stop(RuntimeError):
    pass


def git(root, *args, data=None):
    result = subprocess.run(['git', '-C', str(root), *args], input=data, capture_output=True)
    if result.returncode:
        raise Stop('Git operation failed; no further pruning permitted')
    return result.stdout


def safe_file(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or not p.parts:
        raise Stop('Unsafe candidate path')
    if any(part in PROTECTED for part in p.parts) or p.suffix.lower() not in EXTENSIONS:
        raise Stop('Protected/non-bulk candidate')
    candidate = root/p
    if candidate.resolve() != candidate or candidate.is_symlink() or not candidate.is_file():
        raise Stop('Candidate missing, changed type or traverses symlink')
    return candidate


def fingerprint(file):
    before = file.stat()
    if not stat.S_ISREG(before.st_mode):
        raise Stop('Only regular files can be pruned')
    sha256 = hashlib.sha256()
    blob = hashlib.sha1(b'blob '+str(before.st_size).encode()+b'\0')
    with file.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            sha256.update(block)
            blob.update(block)
    after = file.stat()
    identity = lambda st: (st.st_ino, st.st_size, st.st_mtime_ns, st.st_mode)
    if identity(before) != identity(after):
        raise Stop('Candidate changed while hashing')
    return {'bytes': before.st_size, 'oid': blob.hexdigest(), 'sha256': sha256.hexdigest(),
            'inode': before.st_ino, 'mtime_ns': before.st_mtime_ns,
            'mode': stat.S_IMODE(before.st_mode)}


def tree(source, sha):
    records = {}
    for entry in git(source, 'ls-tree', '-r', '-z', sha).split(b'\0'):
        if not entry:
            continue
        fields, name = entry.split(b'\t', 1)
        mode, kind, oid = fields.decode().split()
        if kind == 'blob' and mode in ('100644', '100755'):
            records[os.fsdecode(name)] = oid
    return records


def clean_target(target):
    if git(target, 'status', '--porcelain=v1', '--untracked-files=all').strip():
        raise Stop('Target has user changes; preserve them before pruning')
    # Existing sparse patterns might have another owner's purpose. Do not replace them.
    if subprocess.run(['git', '-C', str(target), 'config', '--bool', 'core.sparseCheckout'],
                      capture_output=True).stdout.strip() == b'true':
        raise Stop('Target already sparse; this one-shot recipe will not replace its rules')


def validate_roots(target, source):
    if target == source or source.is_relative_to(target) or target.is_relative_to(source):
        raise Stop('Proof source must be outside the target')
    for root in (target, source):
        if git(root, 'rev-parse', '--show-toplevel').decode().strip() != str(root):
            raise Stop('Root is not the exact repository top level')
    common = lambda p: Path(git(p, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()).resolve()
    if common(target) == common(source) or (common(source)/'objects/info/alternates').exists():
        raise Stop('Proof source must have an independent object store')


def plan(target, source, sha):
    validate_roots(target, source)
    clean_target(target)
    # The executor supplies an independently cloned, pinned GitHub main source.
    if git(source, 'rev-parse', 'refs/remotes/origin/main').decode().strip() != sha:
        raise Stop('Source is not pinned to its fetched main tree')
    records = tree(source, sha)
    by_oid = {}
    for name, oid in records.items():
        by_oid.setdefault(oid, name)
    candidates, retained = [], []
    tracked = set(os.fsdecode(n) for n in git(target, 'ls-files', '-z').split(b'\0') if n)
    for parent, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if d not in PROTECTED and not (Path(parent)/d).is_symlink()]
        for name in files:
            file = Path(parent)/name
            if file.is_symlink() or not file.is_file() or file.stat().st_size < MIN_BYTES:
                continue
            relative = file.relative_to(target).as_posix()
            if file.suffix.lower() not in EXTENSIONS:
                retained.append({'path': relative, 'reason': 'not a bulk asset/package'})
                continue
            meta = fingerprint(safe_file(target, relative))
            if meta['oid'] not in by_oid:
                retained.append({'path': relative, 'bytes': meta['bytes'],
                                 'reason': 'exact container/blob not found in pinned main'})
                continue
            candidates.append(dict(path=relative, archive_path=relative if records.get(relative) == meta['oid']
                                   else by_oid[meta['oid']], tracked=relative in tracked, **meta))
    # Fetch the remote blobs in batches; never trust target objects or its index alone.
    oids = sorted({c['oid'] for c in candidates})
    for offset in range(0, len(oids), 100):
        git(source, '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', '--no-tags',
            '--no-write-fetch-head', 'origin', *oids[offset:offset+100])
    hashes = {}
    for oid in oids:
        data = git(source, 'cat-file', 'blob', oid)
        if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != oid:
            raise Stop('Independent remote blob identity mismatch')
        hashes[oid] = hashlib.sha256(data).hexdigest()
    for c in candidates:
        if hashes[c['oid']] != c['sha256']:
            raise Stop('Independent remote byte hash mismatch')
    return {'version': 1, 'state': 'verified-plan; no files deleted',
            'target_label': 'legacy Design workspace', 'target_head': git(target, 'rev-parse', 'HEAD').decode().strip(),
            'archive_source_sha': sha, 'minimum_bytes': MIN_BYTES,
            'protected': sorted(PROTECTED), 'files': sorted(candidates, key=lambda c: c['path']),
            'file_count': len(candidates), 'bytes': sum(c['bytes'] for c in candidates),
            'independently_verified_blobs': len(oids), 'retained_unverified': retained}


def apply(target, source, manifest):
    validate_roots(target, source)
    clean_target(target)
    if (manifest['version'] != 1 or manifest['state'] != 'verified-plan; no files deleted'
            or manifest['minimum_bytes'] != MIN_BYTES or manifest['protected'] != sorted(PROTECTED)
            or git(target, 'rev-parse', 'HEAD').decode().strip() != manifest['target_head']):
        raise Stop('Plan authority/target head changed')
    records = tree(source, manifest['archive_source_sha'])
    tracked = set(os.fsdecode(n) for n in git(target, 'ls-files', '-z').split(b'\0') if n)
    # Validate the entire deletion set before touching the target.
    names = set()
    verified = set()
    for c in manifest['files']:
        if (c['path'] in names or c['bytes'] < MIN_BYTES or records.get(c['archive_path']) != c['oid']
                or c['tracked'] != (c['path'] in tracked)):
            raise Stop('Invalid plan entry')
        names.add(c['path'])
        if fingerprint(safe_file(target, c['path'])) != {k: c[k] for k in
                ('bytes', 'oid', 'sha256', 'inode', 'mtime_ns', 'mode')}:
            raise Stop('Local file changed after verification; nothing pruned')
        if c['oid'] not in verified:
            if hashlib.sha256(git(source, 'cat-file', 'blob', c['oid'])).hexdigest() != c['sha256']:
                raise Stop('Independent proof object changed')
            verified.add(c['oid'])
    if manifest['file_count'] != len(names) or manifest['bytes'] != sum(c['bytes'] for c in manifest['files']):
        raise Stop('Plan totals changed')
    # Sparse-checkout removes only the exact archived tracked blobs. It preserves
    # a clean local index, so a later commit cannot accidentally delete GitHub assets.
    escape = lambda name: re.sub(r'([\\*?\[\]])', r'\\\1', name)
    excluded = [c['path'] for c in manifest['files'] if c['tracked']]
    patterns = '/*\n' + ''.join('!/'+escape(name)+'\n' for name in excluded)
    git(target, 'sparse-checkout', 'set', '--no-cone', '--stdin', data=patterns.encode())
    for c in manifest['files']:
        file = target/c['path']
        if c['tracked']:
            if file.exists():
                raise Stop('Sparse checkout did not omit a planned tracked file; inspect partial outcome')
        else:
            if fingerprint(safe_file(target, c['path']))['sha256'] != c['sha256']:
                raise Stop('Untracked candidate changed; inspect partial outcome')
            file.unlink()  # One explicitly verified file, never recursive deletion.
    if git(target, 'status', '--porcelain=v1', '--untracked-files=all').strip():
        raise Stop('Unexpected target changes after pruning; inspect outcome')
    return {'state': 'applied', 'file_count': len(names), 'bytes_removed': manifest['bytes'],
            'git_status': 'clean; archived tracked assets intentionally omitted by sparse checkout',
            'shared_git_and_preview_roots': 'retained', 'archive_source_sha': manifest['archive_source_sha']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'apply'])
    parser.add_argument('--target', required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--sha')
    parser.add_argument('--confirm-target', help='Exact resolved path; mandatory explicit deletion consent for apply')
    args = parser.parse_args()
    target, source = Path(args.target).resolve(), Path(args.source).resolve()
    try:
        if args.command == 'plan':
            if not args.sha or not re.fullmatch('[a-f0-9]{40}', args.sha):
                raise Stop('Plan requires the independently fetched main SHA')
            result = plan(target, source, args.sha)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            with args.manifest.open('x') as f:
                json.dump(result, f, indent=2)
                f.write('\n')
            print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))
        else:
            if args.confirm_target != str(target):
                raise Stop('Apply requires explicit --confirm-target with the exact resolved target')
            print(json.dumps(apply(target, source, json.loads(args.manifest.read_text())), indent=2))
    except (Stop, OSError, KeyError, ValueError) as exc:
        print(json.dumps({'state': 'STOP', 'reason': str(exc)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

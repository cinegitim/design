#!/usr/bin/env python3
"""Read-only Brand Studio branch, identity hash and local runtime preflight.

No network, installation, rendering, image/model calls or tracked-file writes.
This is a procedural guard; it does not enforce remote branch protection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


class PreflightError(Exception):
    pass


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                            text=True, timeout=15)
    if result.returncode:
        raise PreflightError('Git metadata unavailable; use an isolated checkout/task branch')
    return result.stdout.strip()


def source(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise PreflightError('Invalid identity source path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise PreflightError('Missing identity source or path outside repository')
    return path


def matched(root, relative, expected):
    path = source(root, relative)
    if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected):
        raise PreflightError('Missing/invalid approved identity hash')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise PreflightError('Locked identity hash mismatch; stop production')
    return path


def runtime(root):
    node = shutil.which('node')
    version = subprocess.run([node, '--version'], capture_output=True, text=True,
                             timeout=10).stdout.strip() if node else None
    py = root / '.venv/bin/python'
    report = {'node': version, 'librsvg_available': bool(shutil.which('rsvg-convert')),
              'pinned_python_packages': False, 'pinned_python_312': False,
              'pinned_browser_recipe_present': False}
    if py.is_file():
        requirements = source(root, 'studio/cloud/requirements.txt').read_text().splitlines()
        pins = dict(line.split('==') for line in requirements if line and not line.startswith('#'))
        code = ('import sys,json,importlib.metadata as m,PIL,fontTools,numpy,cv2; '
                'assert sys.version_info[:2] == (3,12); '
                'pins=json.loads(sys.argv[1]); '
                'assert all(m.version(p)==v for p,v in pins.items())')
        result = subprocess.run([str(py), '-I', '-B', '-c', code, json.dumps(pins)], capture_output=True,
                                timeout=15)
        report['pinned_python_packages'] = result.returncode == 0
        result = subprocess.run([str(py), '-I', '-B', '-c',
                                 'import sys; assert sys.version_info[:2] == (3,12)'],
                                capture_output=True, timeout=15)
        report['pinned_python_312'] = result.returncode == 0
    if node and version and version.startswith('v22.'):
        # Read installed package version and browser path; do not launch/render.
        code = ('const{createRequire}=require("node:module"),fs=require("node:fs");'
                'const r=createRequire(process.argv[1]);'
                'const p=r("playwright-core/package.json");'
                'const expected=JSON.parse(fs.readFileSync(process.argv[1])).dependencies["playwright-core"];'
                'if(p.version!==expected||!fs.existsSync(r("playwright-core").chromium.executablePath()))process.exit(1);')
        result = subprocess.run([node, '-e', code, str(root/'studio/cloud/package.json')],
                                capture_output=True, timeout=15)
        report['pinned_browser_recipe_present'] = result.returncode == 0
    report['render_prerequisites_present'] = bool(
        version and version.startswith('v22.') and report['librsvg_available']
        and report['pinned_python_packages'] and report['pinned_browser_recipe_present'])
    report['browser_smoke_test'] = 'not run; use studio/cloud/doctor.sh before rendering'
    report['session_image_and_github_tools'] = 'verify actual conversation tools; not detectable by shell'
    return report


def check(root, brand, read_only=False, require_render=False):
    root = root.resolve()
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', brand):
        raise PreflightError('Use an exact kebab-case brand slug')
    branch = git(root, 'branch', '--show-current')
    if not read_only and not re.fullmatch('publish/[a-z0-9][a-z0-9._/-]*', branch):
        raise PreflightError('Production requires a named publish/<topic> branch; main/detached HEAD is read-only')
    metadata = json.loads(source(root, f'brands/{brand}/brand.json').read_text())
    if metadata.get('slug') != brand:
        raise PreflightError('Brand slug/metadata mismatch; do not substitute another brand')
    count = 0
    logo = metadata.get('canonicalLogo', {})
    if logo.get('locked'):
        matched(root, logo.get('path'), logo.get('sha256'))
        source(root, logo.get('decisionRecord'))
        count += 1
    lockups = metadata.get('canonicalLockups', {})
    if lockups.get('locked'):
        manifest_path = matched(root, lockups.get('manifest'), lockups.get('manifestSha256'))
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('brand_id') != brand or manifest.get('status') != 'APPROVED / CANONICAL':
            raise PreflightError('Lockup manifest approval/brand mismatch')
        records = manifest.get('records', [])
        if not records or len({r.get('canonical_lockup_id') for r in records}) != len(records):
            raise PreflightError('Empty/duplicate lockup records')
        if manifest.get('canonical_seal_sha256') != logo.get('sha256'):
            raise PreflightError('Lockup seal provenance mismatch')
        for record in records:
            matched(root, record.get('canonical_file_path'), record.get('sha256'))
            count += 1
    system = root / f'brands/{brand}/brand-system.md'
    warnings = []
    if not system.is_file():
        warnings.append('Full brand-system.md absent: use approved identity + selected application spec/brief; never borrow a sibling or claim full-system approval')
    elif metadata.get('canonicalIdentity') is not True:
        warnings.append('System text is not human approval: metadata does not mark this identity canonical; inspect actual decisions before production')
    local_runtime = runtime(root)
    if require_render and not local_runtime['render_prerequisites_present']:
        raise PreflightError('Pinned rendering prerequisites missing; use cloud setup/doctor before building')
    return {'status': 'PASS', 'mode': 'read-only inspection' if read_only else 'task-branch preflight',
            'branch': branch or 'detached HEAD', 'head_sha': git(root, 'rev-parse', 'HEAD'),
            'brand': brand, 'locked_files_checked': count, 'warnings': warnings,
            'runtime': local_runtime,
            'limits': 'Source hashes/local prerequisites only; no fresh-main, task-ownership, visual, CI or account activation proof; no merge authorized'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--brand', required=True)
    parser.add_argument('--read-only', action='store_true')
    parser.add_argument('--require-render', action='store_true')
    args = parser.parse_args()
    try:
        result = check(args.root, args.brand, args.read_only, args.require_render)
    except (PreflightError, OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        result = {'status': 'FAIL', 'error': str(exc) if isinstance(exc, PreflightError)
                  else 'Invalid/missing preflight input or unavailable runtime'}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

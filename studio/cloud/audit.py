#!/usr/bin/env python3
"""Read-only independent audit of submitted files. Stdlib; no render or producer imports.

--policy may point to trusted base policy outside the submitted tree. Existing
bundle contracts are retained; candidate policy can only add registrations.
This proves file/source consistency, NOT actual production execution or aesthetics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

NS = '{http://www.w3.org/2000/svg}'
XLINK = '{http://www.w3.org/1999/xlink}'
MAX_FILE = 100 * 1024 * 1024
TEXT_EXT = {'.py', '.js', '.mjs', '.ts', '.json', '.html', '.svg', '.md', '.txt', '.yml', '.yaml', '.sh', '.toml', '.xml', '.csv'}
SECRETS = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
    re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
    re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(rb'\bAIza[0-9A-Za-z_-]{35}\b'),
]

class AuditError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise AuditError(message)

def safe_file(root: Path, relative: str) -> Path:
    """Untrusted metadata cannot escape the tree, even using symlinks."""
    need(isinstance(relative, str) and bool(relative), 'empty/invalid file path')
    p = PurePosixPath(relative)
    need(not p.is_absolute() and '\\' not in relative and '..' not in p.parts,
         'unsafe relative path')
    candidate = (root / relative).resolve()
    need(candidate.is_relative_to(root.resolve()), 'file path escapes tree')
    need(candidate.is_file(), f'missing file: {relative}')
    need(candidate.stat().st_size <= MAX_FILE, f'file exceeds audit limit: {relative}')
    return candidate

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def matched_file(root, name, expected):
    need(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'invalid SHA-256')
    path = safe_file(root, name)
    need(digest(path) == expected, f'hash mismatch: {name}')
    return path

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def png_dimensions(path):
    """Validate chunk CRC/structure without rendering or decompressing a raster."""
    data = path.read_bytes()
    need(data[:8] == b'\x89PNG\r\n\x1a\n', 'invalid PNG signature')
    offset, dims, ended, idat = 8, None, False, False
    while offset < len(data):
        need(offset + 12 <= len(data), 'truncated PNG chunk')
        length = struct.unpack('>I', data[offset:offset+4])[0]
        kind = data[offset+4:offset+8]
        end = offset + 8 + length
        need(end + 4 <= len(data), 'truncated PNG payload')
        payload = data[offset+8:end]
        crc = struct.unpack('>I', data[end:end+4])[0]
        need(zlib.crc32(kind + payload) & 0xffffffff == crc, 'PNG CRC mismatch')
        if dims is None:
            need(kind == b'IHDR' and length == 13, 'PNG must start with IHDR')
            dims = struct.unpack('>II', payload[:8])
            need(all(0 < d <= 16384 for d in dims), 'unsafe PNG dimensions')
        else:
            need(kind != b'IHDR', 'duplicate PNG header')
        idat |= kind == b'IDAT'
        offset = end + 4
        if kind == b'IEND':
            need(length == 0 and offset == len(data), 'invalid PNG end')
            ended = True
            break
    need(ended and idat and dims is not None, 'incomplete PNG')
    return list(dims)

def normal(text):
    return ' '.join(text.split())

def number(value):
    v = float(value)
    need(math.isfinite(v), 'non-finite geometry')
    return v

def scan_text(data, label):
    # Never print matching secret values.
    need(not any(p.search(data) for p in SECRETS), f'possible credential in {label}; values withheld')

def svg_links(path, root):
    tree = ET.parse(path).getroot()
    for el in tree.iter():
        need(el.tag not in {NS+'script', NS+'foreignObject'}, f'active SVG content: {path.name}')
        href = el.get('href', el.get(XLINK+'href'))
        if href and not href.startswith(('#', 'data:')):
            need(':' not in href and not href.startswith('/'), 'external SVG dependency')
            dep = (path.parent / href).resolve()
            need(dep.is_relative_to(root.resolve()) and dep.is_file(), f'broken SVG dependency: {path.name}')
    return tree

def canonical_assets(root, policy):
    c = policy['canonical']
    matched_file(root, c['seal'], c['seal_sha256'])
    manifest_path = matched_file(root, c['manifest'], c['manifest_sha256'])
    m = load(manifest_path)
    need(m['canonical_seal_sha256'] == c['seal_sha256'], 'seal anchor mismatch')
    records = {r['canonical_lockup_id']: r for r in m['records']}
    need(len(records) == 15 and len(m['records']) == 15, 'canonical record count')
    for rec in records.values():
        asset = matched_file(root, rec['canonical_file_path'], rec['sha256'])
        tree = ET.parse(asset).getroot()
        need(not list(tree.iter(NS+'text')) and not list(tree.iter(NS+'image')), 'canonical mark not path-only')
    return records

def audit_bundle(root, contract, canonical, seal_sha):
    root = root.resolve()
    base = (root / contract['path']).resolve()
    need(base.is_relative_to(root), 'bundle escapes repository')
    need(contract['format'] == 'carousel', 'unsupported bundle format; add a reviewed checker')
    for name in contract['required_files']:
        safe_file(base, name)
    m = load(safe_file(base, contract['manifest']))
    dims = contract['dimensions']
    need(m['dimensions'] == dims, 'bundle dimension contract mismatch')
    ids = [s['id'] for s in m['slides']]
    need(ids == contract['slide_ids'] and len(set(ids)) == len(ids), 'slide set/order mismatch')
    font = matched_file(base, m['font']['file'], m['font']['sha256'])
    report = load(safe_file(base, 'render-validation.json'))
    zip_members = {m['font']['file']: font}
    for name in ('build.py', 'render.mjs', 'verify_and_package.py', 'render-validation.json', 'quality-review.md', 'generation-notes.md'):
        zip_members[name] = safe_file(base, name)
    for slide in m['slides']:
        final = matched_file(base, slide['final_file'], slide['final_sha256'])
        original = matched_file(base, slide['original_file'], slide['original_sha256'])
        source = matched_file(base, slide['source_file'], slide['source_sha256'])
        editable = safe_file(base, slide['editable_html_file'])
        need(png_dimensions(final) == dims == slide['dimensions'], f'{slide["id"]}: PNG dimension mismatch')
        png_dimensions(original)
        rec = canonical[slide['canonical_lockup_id']]
        need(slide['canonical_seal_sha256'] == seal_sha == slide['canonical_logo_sha256'], 'seal provenance mismatch')
        need(slide['canonical_lockup_sha256'] == rec['sha256'], 'unapproved lockup hash')
        logo = matched_file(base, slide['canonical_lockup_file'], rec['sha256'])
        tree = svg_links(source, root)
        need(tree.get('width') == str(dims[0]) and tree.get('height') == str(dims[1]), 'SVG dimension mismatch')
        group = next((e for e in tree.iter() if e.get('id') == 'editable-campaign-copy'), None)
        need(group is not None, 'missing editable copy')
        visible = ' '.join((e.text or '') for e in group.iter(NS+'text'))
        need(normal(visible) == normal(' '.join(slide['copy'])), 'visible SVG copy mismatch')
        need(json.loads(group.get('data-exact-copy-json', '[]')) == slide['copy'] == m['exact_copy'][slide['id']], 'copy metadata mismatch')
        mark = next((e for e in tree.iter() if e.get('id') == 'canonical-lockup'), None)
        need(mark is not None and mark.tag == NS+'image', 'complete linked canonical mark required')
        href = mark.get('href', mark.get(XLINK+'href', ''))
        need((source.parent / href).resolve() == logo, 'canonical source link mismatch')
        x, y, w, h = [number(mark.get(k)) for k in ('x', 'y', 'width', 'height')]
        need([x, y] == slide['logo_x_y_px'] and w == slide['logo_width_px'], 'logo placement metadata mismatch')
        need(math.isclose(h, slide['logo_height_px'], abs_tol=1e-5), 'logo height mismatch')
        vb = list(map(float, ET.parse(logo).getroot().get('viewBox').split()))
        need(math.isclose(w/h, vb[2]/vb[3], rel_tol=1e-6), 'distorted complete mark')
        minimum = rec['minimum_supported_display_size']['screen_width_px']
        need(w >= minimum and slide['minimum_supported_display_width_px'] == minimum, 'logo below approved minimum')
        need(x >= 0 and y >= 0 and x+w <= dims[0] and y+h <= dims[1], 'clipped logo viewport')
        metrics = report[slide['id']]
        need(metrics == slide['render_validation'], 'render-report/manifest mismatch')
        need(metrics['jostLoaded'] is True and metrics['issues'] == [], 'producer reported a render issue')
        # Reports are evidence submitted by producer, not independently remeasured geometry.
        for name in ('final_file', 'original_file', 'source_file', 'editable_html_file', 'canonical_lockup_file'):
            zip_members[slide[name]] = safe_file(base, slide[name])
        zip_members[Path(slide['final_file']).name] = final
        for el in tree.iter(NS+'image'):
            dep = (source.parent / el.get('href', '')).resolve()
            if dep.is_file() and dep.is_relative_to(base):
                zip_members[dep.relative_to(base).as_posix()] = dep
        html_text = editable.read_text(encoding='utf-8')
        # The editable HTML must embed the same SVG, not an unrelated reconstruction.
        need(source.read_text(encoding='utf-8') in html_text, 'editable HTML/SVG mismatch')
    for name in m['mobile_preview_files']:
        need(png_dimensions(safe_file(base, name)) == [375, 469], 'mobile dimension mismatch')
    for key in ('contact_sheet_file', 'source_vs_final_contact_sheet_file', 'revision_comparison_file'):
        name = m[key]
        zip_members[name] = safe_file(base, name)
    for extra in m.get('alternate_generations', []):
        zip_members[extra['file']] = matched_file(base, extra['file'], extra['sha256'])
    for p in (base/'assets').rglob('*'):
        if p.is_file():
            zip_members[p.relative_to(base).as_posix()] = safe_file(base, p.relative_to(base).as_posix())
    package = safe_file(base, m['package_file'])
    with zipfile.ZipFile(package) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        need(len(names) == len(set(names)), 'duplicate ZIP members')
        need(sum(i.file_size for i in infos) < 512*1024*1024, 'ZIP expands beyond audit limit')
        for i in infos:
            p = PurePosixPath(i.filename)
            need(not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename, 'unsafe ZIP path')
            need((i.external_attr >> 16) & 0o170000 != 0o120000, 'ZIP symlink is not a deliverable')
            need(i.file_size <= MAX_FILE, 'ZIP member too large')
        need(z.testzip() is None, 'ZIP CRC failure')
        need(z.read(contract['manifest']) == safe_file(base, contract['manifest']).read_bytes(), 'ZIP manifest differs')
        for name, path in zip_members.items():
            need(name in names and hashlib.sha256(z.read(name)).hexdigest() == digest(path), f'ZIP missing/stale member: {name}')
        for i in infos:
            if PurePosixPath(i.filename).suffix.lower() in TEXT_EXT:
                scan_text(z.read(i.filename), 'ZIP text member')
    return {'path': contract['path'], 'slides': len(ids), 'package_sha256': digest(package), 'status': 'PASS'}

def tracked(root):
    r = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'], capture_output=True, check=True)
    return r.stdout.decode().strip('\0').split('\0') if r.stdout else []

def audit(root, policy):
    root = root.resolve()
    need(policy['version'] == 1, 'unsupported policy version')
    records = canonical_assets(root, policy)
    registered = {c['path']: c for c in policy['bundles']}
    candidate = load(safe_file(root, 'studio/cloud/policy.json'))
    need(candidate['canonical'] == policy['canonical'], 'canonical policy change requires explicit approval')
    need(candidate.get('preservation') == policy.get('preservation'), 'preservation anchor cannot be silently changed')
    need(candidate['version'] == 1, 'invalid candidate policy')
    incoming = {c['path']: c for c in candidate['bundles']}
    need(len(incoming) == len(candidate['bundles']), 'duplicate bundle registration')
    for key, value in registered.items():
        need(incoming.get(key) == value, 'existing bundle audit contract cannot be silently removed/changed')
    registered.update(incoming)
    bundles = [audit_bundle(root, c, records, policy['canonical']['seal_sha256']) for c in registered.values()]
    scanned = 0
    for name in tracked(root):
        parts = PurePosixPath(name).parts
        need(not any(p in {'node_modules', '.venv', 'share-runtime', '__pycache__'} for p in parts), 'runtime material tracked')
        need(not (Path(name).name.startswith('.env') and Path(name).name != '.env.example'), 'environment secrets file tracked')
        need(Path(name).suffix not in {'.pem', '.key'}, 'private key container tracked')
        if Path(name).suffix.lower() in TEXT_EXT:
            scan_text(safe_file(root, name).read_bytes(), name)
            scanned += 1
    # Verify migration preservation records when available, without publishing runtime logs.
    preservation = policy.get('preservation')
    if preservation:
        archive = matched_file(root, preservation['manifest'], preservation['sha256'])
        evidence = load(archive)
        commit = evidence['baseline_commit']
        need(re.fullmatch('[a-f0-9]{40}', commit) is not None, 'invalid archive baseline')
        for item in evidence['files']:
            if item['disposition'] == 'preserved':
                matched_file(root, item['repository_path'], item['sha256'])
            entries = item.get('entries', []) if item['disposition'] == 'duplicate_package' else [item]
            for entry in entries:
                if entry['disposition'] != 'duplicate':
                    continue
                rel = entry['repository_path']
                # A future edit need not freeze an active file forever: history is the archive.
                result = subprocess.run(['git', '-C', str(root), 'show', f'{commit}:{rel}'], capture_output=True)
                need(result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == entry['sha256'],
                     'archived duplicate is not present at the recorded GitHub baseline')
    return {'status': 'PASS', 'mode': 'audit-only; no render/build/API calls', 'canonical_records': len(records),
            'bundles': bundles, 'text_files_scanned': scanned,
            'limits': 'Source/file consistency only; no OCR, raster authenticity, independent render or aesthetic approval.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--report', type=Path, help='Optional CI report outside the source tree')
    args = parser.parse_args()
    try:
        policy_path = args.policy or args.root/'studio/cloud/policy.json'
        result = audit(args.root, load(policy_path))
    except (AuditError, OSError, ValueError, KeyError, StopIteration, ET.ParseError, zipfile.BadZipFile) as exc:
        # Do not include raw input lines, XML/JSON parse context, or secret values.
        message = str(exc) if isinstance(exc, AuditError) else f'invalid/missing audit input ({type(exc).__name__})'
        result = {'status': 'FAIL', 'error': message}
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    print(text)
    if args.report:
        args.report.write_text(text, encoding='utf-8')
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())

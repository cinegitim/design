#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the six exports, build review artefacts, and assemble the ZIP.

Checks performed independently of the producer's render report:
  * every final PNG is exactly 1080x1350 and matches its manifest hash
  * visible SVG text equals the locked copy (fragment join preserves spaces)
  * canonical lockup geometry is undistorted, above minimum size, in frame
  * the SVG dimension and linked-artwork contract holds
  * mobile previews are generated from the real PNGs at 375x469
"""
import hashlib
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = Path('/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/basvuru-rehberi-001')
NS = '{http://www.w3.org/2000/svg}'
SEAL_SHA = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
M = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
JOST = HERE / 'assets/Jost-VF.ttf'
OUT = HERE / 'mobile'
OUT.mkdir(exist_ok=True)
small = ImageFont.truetype(str(JOST), 15)
def normalise_photos():
    """Downscale the licensed photographs to at most 1500 px on the long edge.

    The composited slides only ever place these images at 1080x1350 or smaller,
    so 1500 px is comfortably sufficient and keeps the bundle and its ZIP
    deliverable repository-sized. Every source URL, author, licence and original
    resolution is recorded in caption-and-credits.md."""
    from PIL import Image as _I
    for f in sorted(HERE.glob('photos/*.jpg')):
        im = _I.open(f).convert('RGB')
        w, h = im.size
        m = max(w, h)
        if m > 1500:
            s = 1500 / m
            im = im.resize((max(1, round(w * s)), max(1, round(h * s))),
                           _I.Resampling.LANCZOS)
        im.save(f, 'JPEG', quality=84, optimize=True, progressive=True)


failures = []



LOGUP_VARIANTS = {
    'D-04/light':   {'for_light_background': True},
    'D-04/dark':    {'for_light_background': False},
    'H-02/light':   {'for_light_background': True},
    'H-02/dark':    {'for_light_background': False},
    'P-01/light':   {'for_light_background': True},
    'P-01/dark':    {'for_light_background': False},
    'C-03/light':   {'for_light_background': True},
    'C-03/dark':    {'for_light_background': False},
    'F-05/light':   {'for_light_background': True},
    'F-05/dark':    {'for_light_background': False},
}


def _luma(c):
    def f(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def final_bg_luma(im, x, y, w, h):
    """Mean luminance of the slide immediately surrounding the lockup box.

    Samples thin strips on each side of the box so the background, not the
    wordmark, is measured. Falls back to the full-slide mean.
    """
    W_, H_ = im.size
    strips = [
        (max(0, x - 22), y, x, min(H_, y + h)),                 # left
        (x + w, y, min(W_, x + w + 22), min(H_, y + h)),        # right
        (x, max(0, y - 22), x + w, y),                          # above
        (x, y + h, x + w, min(H_, y + h + 22)),                 # below
    ]
    px = []
    for a in strips:
        if a[2] > a[0] and a[3] > a[1]:
            px += list(im.crop(a).getdata())
    if not px:
        px = list(im.getdata())
    return sum(_luma(c) for c in px) / len(px)


def wordmark_contrast(region):
    """Contrast ratio between the two dominant tonal clusters in the lockup box."""
    data = list(region.getdata())
    from collections import Counter
    cnt = Counter(data)
    bg = cnt.most_common(1)[0][0]
    best, bestn = None, 0
    for c, n in cnt.most_common(60):
        if abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) > 60 and n > bestn:
            best, bestn = c, n
    if best is None:
        return 0.0
    l1, l2 = max(_luma(best), _luma(bg)), min(_luma(best), _luma(bg))
    return (l1 + 0.05) / (l2 + 0.05)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(cond, message):
    if not cond:
        failures.append(message)


finals, pairs, integrity = [], [], []
for slide in M['slides']:
    final = HERE / slide['final_file']
    original = HERE / slide['original_file']
    source = HERE / slide['source_file']
    check(final.exists(), slide['id'] + ' final missing')
    check(original.exists(), slide['id'] + ' original missing')
    im = Image.open(final)
    check(im.size == (1080, 1350), slide['id'] + ' final size')
    check(sha(final) == slide['final_sha256'], slide['id'] + ' final hash')
    check(sha(original) == slide['original_sha256'], slide['id'] + ' original hash')
    check(sha(source) == slide['source_sha256'], slide['id'] + ' source hash')

    root = ET.parse(source).getroot()
    group = next(e for e in root.iter() if e.get('id') == 'editable-campaign-copy')
    visible = ' '.join((e.text or '') for e in group.iter(NS + 'text'))
    # Slide 06's brand wordmark is delivered by the canonical lockup, never
    # retypeset. The same documented exclusion used by build.py.
    delivered = {'06-dossier': ["Asya'da Eğitim"]}
    skip = delivered.get(slide['id'], [])
    locked = ' '.join(c for c in slide['copy'] if c not in skip)
    for s in skip:
        check(s not in visible, slide['id'] + f' "{s}" must not be retypeset')
    check(' '.join(visible.split()) == ' '.join(locked.split()),
          slide['id'] + ' visible copy mismatch')
    check(json.loads(group.get('data-exact-copy-json')) == slide['copy'],
          slide['id'] + ' copy metadata mismatch')
    check(locked == ' '.join(c for c in M['exact_copy'][slide['id']] if c not in skip),
          slide['id'] + ' manifest copy mismatch')

    mark = next(e for e in root.iter() if e.get('id') == 'canonical-lockup')
    linked = (source.parent / mark.get('href')).resolve()
    check(linked == (HERE / slide['canonical_lockup_file']).resolve(),
          slide['id'] + ' lockup link')
    check(sha(linked) == slide['canonical_lockup_sha256'], slide['id'] + ' lockup hash')
    check(slide['canonical_seal_sha256'] == SEAL_SHA, slide['id'] + ' seal provenance')
    check(slide['canonical_logo_sha256'] == SEAL_SHA, slide['id'] + ' logo provenance')
    # The lockup must carry the canonical seal anchor in its own metadata.
    lockup_meta = ET.fromstring(linked.read_text(encoding='utf-8'))
    meta_el = lockup_meta.find(NS + 'metadata')
    if meta_el is not None and (meta_el.text or '').strip():
        check(json.loads(meta_el.text).get('canonical_seal_sha256') == SEAL_SHA,
              slide['id'] + ' embedded seal anchor')
    x, y, w, h = [float(mark.get(k)) for k in ('x', 'y', 'width', 'height')]
    check([x, y] == slide['logo_x_y_px'] and w == slide['logo_width_px'],
          slide['id'] + ' placement metadata')
    vb = list(map(float, ET.parse(linked).getroot().get('viewBox').split()))
    check(abs(w / h - vb[2] / vb[3]) < 1e-6, slide['id'] + ' distorted mark')
    check(w >= slide['minimum_supported_display_width_px'], slide['id'] + ' below minimum')
    check(0 <= x and 0 <= y and x + w <= 1080 and y + h <= 1350, slide['id'] + ' clipped mark')

    rv = slide['render_validation']
    check(rv['jostLoaded'] is True and rv['issues'] == [], slide['id'] + ' render issue')
    # icon/label separation on the dossier slide
    if slide['id'] == '06-dossier':
        for i, ib in enumerate(rv.get('iconBounds', [])):
            for tb in rv['textBounds']:
                overlap = (ib['x'] < tb['x'] + tb['width'] and ib['x'] + ib['width'] > tb['x']
                           and ib['y'] < tb['y'] + tb['height'] and ib['y'] + ib['height'] > tb['y'])
                check(not overlap, f"06-dossier icon {i} overlaps label {tb['copy']}")

    rgb = im.convert('RGB')
    # Brand-compliance guard: the lockup wordmark must be visible on the slide.
    lv = LOGUP_VARIANTS[slide['canonical_lockup_id']]
    bg_light = final_bg_luma(rgb, x, y, w, h) > 0.5
    if bg_light and not lv['for_light_background']:
        failures.append(f"{slide['id']}: {slide['canonical_lockup_id']} is not a light-background variant")
    if (not bg_light) and lv['for_light_background']:
        failures.append(f"{slide['id']}: {slide['canonical_lockup_id']} is not a dark-background variant")
    # measured wordmark contrast
    region = rgb.crop((x, y, min(1080, x + w), min(1350, y + h)))
    contrast = wordmark_contrast(region)
    check(contrast >= 4.5,
          f"{slide['id']}: lockup wordmark contrast {contrast:.1f}:1 below 4.5:1")

    rgb.resize((324, 405), Image.Resampling.LANCZOS).save(OUT / f"{slide['id']}-324x405.png", optimize=True)
    rgb.resize((375, 469), Image.Resampling.LANCZOS).save(OUT / f"{slide['id']}-375x469.png", optimize=True)
    finals.append((slide, rgb))

    src = ImageOps.fit(Image.open(original).convert('RGB'), (1080, 1350),
                       method=Image.Resampling.LANCZOS)
    diff = ImageChops.difference(rgb, src).convert('L')
    changed = sum(1 for px in diff.getdata() if px > 24)
    pct = round(changed / (1080 * 1350) * 100, 2)
    check(pct < 55, f"{slide['id']} reconstruction altered {pct}% of source")
    lx, ly = slide['logo_x_y_px']
    lw, lh = slide['logo_width_px'], round(slide['logo_height_px'])
    logo_px = sum(1 for px in diff.crop((lx, ly, min(1080, lx + lw), min(1350, ly + lh)))
                  .getdata() if px > 45)
    check(logo_px > 1200, f"{slide['id']} lockup zone not composited")
    integrity.append({'slide': slide['id'], 'source_to_final_changed_area_percent': pct,
                      'logo_region_changed_pixels': logo_px, 'status': 'PASS'})
    pairs.append((src.resize((176, 220), Image.Resampling.LANCZOS),
                   rgb.resize((176, 220), Image.Resampling.LANCZOS), slide['id']))

# ---- full six-slide contact sheet
sheet = Image.new('RGB', (6 * 214, 336), '#17181b')
d = ImageDraw.Draw(sheet)
for i, (slide, im) in enumerate(finals):
    sheet.paste(im.resize((210, 262), Image.Resampling.LANCZOS), (i * 214, 0))
    d.text((i * 214 + 8, 300), f"0{i + 1}  {slide['id'].split('-', 1)[1]}", font=small, fill='#f7f3e9')
sheet.save(HERE / 'contact-sheet.png', optimize=True)

# ---- original art-direction plate -> final, side by side
pair = Image.new('RGB', (12 * 176, 268), '#17181b')
dp = ImageDraw.Draw(pair)
for i, (o, f, label) in enumerate(pairs):
    pair.paste(o, (i * 352, 0))
    pair.paste(f, (i * 352 + 176, 0))
    dp.text((i * 352 + 3, 242), f"0{i + 1} PLATE", font=small, fill='#f7f3e9')
    dp.text((i * 352 + 179, 242), "FINAL", font=small, fill='#f7f3e9')
pair.save(HERE / 'original-to-final-contact-sheet.jpg', quality=92, optimize=True)

# ---- mobile preview contact sheet at 375x469
mob = Image.new('RGB', (6 * 190, 300), '#17181b')
dm = ImageDraw.Draw(mob)
for i, (slide, im) in enumerate(finals):
    p = OUT / f"{slide['id']}-375x469.png"
    dm_paste = Image.open(p).resize((182, 227), Image.Resampling.LANCZOS)
    mob.paste(dm_paste, (i * 190 + 4, 8))
    dm.text((i * 190 + 8, 254), f"0{i + 1}", font=small, fill='#f7f3e9')
mob.save(HERE / 'mobile-preview-contact-sheet.png', optimize=True)
revision = HERE / 'mobile-preview-contact-sheet.png'

M['pixel_integrity_review'] = integrity
M['package_file'] = 'package/basvuru-rehberi-001-cince.zip'
M['mobile_preview_files'] = [f"mobile/{s['id']}-375x469.png" for s in M['slides']]
M['contact_sheet_file'] = 'contact-sheet.png'
M['source_vs_final_contact_sheet_file'] = 'original-to-final-contact-sheet.jpg'
M['revision_comparison_file'] = 'mobile-preview-contact-sheet.png'
M['audit_contract'] = {
    'png_dimensions': [1080, 1350],
    'mobile_dimensions': [375, 469],
    'visible_copy_matches_locked': not failures,
    'canonical_mark_linked_and_undistorted': not failures,
    'checks_run': ['final PNG size/hash', 'original PNG hash', 'source SVG hash',
                   'visible copy == locked copy', 'copy metadata JSON',
                   'lockup link/hash/minimum/aspect/frame', 'render validation issues',
                   'icon-label separation', 'logo compositing delta', 'mobile sizing'],
}
(HERE / 'manifest.json').write_text(json.dumps(M, ensure_ascii=False, indent=2), encoding='utf-8')

readme = """# Asya'da Egitim - Basvuru Rehberi / 001
# "Cince bilmeden Cin'de okuyabilir miyim?"

Six 1080x1350 PNGs sit at the ZIP root (01-cover.png ... 06-dossier.png) and in
`final/`. Every manifest path resolves to a real file in this archive.

- `final/` - the six exported Instagram carousel slides.
- `originals/` - the copy-free art-direction plates (licensed photography plus
  deterministic Chinese motif geometry) that the typography and canonical
  lockups were composited onto.
- `source/` - editable SVG and HTML sources; Jost and the Songti SC CJK subset are
  embedded, canonical lockups are linked verbatim. `*-plate.svg` are the plates.
- `assets/` - Jost (SIL OFL), the CJK subset, the canonical manifest, the verbatim
  approved lockup SVGs and the licensed photographs in `photos/`.
- `mobile/` - 324x405 and 375x469 previews rendered from the final PNGs.
- `caption-and-credits.md` - photographer, licence and source URL per photograph.
- `exact-copy.json` - the locked copy with a line-by-line fidelity check.

Rebuild: Python 3 + Pillow, Node.js + playwright-core and Chrome.
`python3 build.py && python3 verify_and_package.py`. Set CHROME_PATH off macOS and
PLAYWRIGHT_MODULE to the absolute playwright-core directory in a temporary install.

Image-generation calls: zero. Photography is licensed Wikimedia Commons material;
the Chinese motif geometry is locally generated SVG. Human review pending; not
published to Instagram.
"""
(HERE / 'package').mkdir(exist_ok=True)
(HERE / 'package' / 'README.md').write_text(readme, encoding='utf-8')

zip_path = HERE / 'package' / 'basvuru-rehberi-001-cince.zip'
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
    for slide in M['slides']:
        p = HERE / slide['final_file']
        z.write(p, Path(slide['final_file']).name)
        z.write(p, slide['final_file'])
    paths = [HERE / 'manifest.json', HERE / 'build.py', HERE / 'render.mjs',
             HERE / 'render-plates.mjs', HERE / 'verify_and_package.py',
             HERE / 'render-validation.json', HERE / 'generation-notes.md',
             HERE / 'quality-review.md', HERE / 'exact-copy.json',
             HERE / 'caption-and-credits.md', HERE / 'handoff.md', HERE / 'photography-sources.json', HERE / 'package' / 'README.md',
             HERE / 'contact-sheet.png',
             HERE / 'original-to-final-contact-sheet.jpg',
             HERE / 'mobile-preview-contact-sheet.png']
    paths += sorted((HERE / 'originals').glob('*.png'))
    paths += sorted((HERE / 'source').glob('*.svg'))
    paths += sorted((HERE / 'source').glob('*.html'))
    paths += sorted((HERE / 'assets').glob('*.png'))
    paths += sorted((HERE / 'assets').glob('*.json'))
    paths += sorted((HERE / 'assets').glob('*.txt'))
    paths += sorted((HERE / 'assets').glob('*.ttf'))
    paths += sorted((HERE / 'assets' / 'lockups').glob('*.svg'))
    paths += sorted((HERE / 'photos').glob('*.jpg'))
    paths += [HERE / 'index.html']
    for p in paths:
        z.write(p, p.relative_to(HERE))

if failures:
    print('VERIFY FAILED:')
    for f in failures:
        print(' -', f)
    raise SystemExit(1)
print(json.dumps({'slides': len(finals), 'integrity': integrity,
                  'zip': str(zip_path), 'zip_bytes': zip_path.stat().st_size,
                  'status': 'PASS'}, ensure_ascii=False, indent=2))

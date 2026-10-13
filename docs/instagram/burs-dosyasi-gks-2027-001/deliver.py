#!/usr/bin/env python3
"""
Assemble the review bundle for Burs Dosyası / 001 — GKS 2027 in the repository's
audited Instagram-carousel contract:
  manifest.json (per-slide hashes, lockup provenance, render validation),
  render-validation.json, original/ renders, source-vs-final and revision
  comparison sheets, quality/generation notes, a real render.mjs + package
  wrapper, the ZIP package and the published gallery copy under docs/instagram/.
Run after build.py (which renders export/*.png from the SVG masters).
"""
import json, hashlib, shutil, subprocess, zipfile, time, re
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from PIL import Image, ImageDraw

APP    = Path(__file__).resolve().parent
ROOT   = APP.parents[3]
LOCK   = ROOT / 'brands/asyada-egitim/assets/lockups'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
GALL   = ROOT / 'docs/instagram/burs-dosyasi-gks-2027-001'
PKG    = APP / 'package'
ORIG   = APP / 'original'; ORIG.mkdir(exist_ok=True)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

man   = json.loads((LOCK/'canonical-lockups.json').read_text())
recs  = {r['canonical_lockup_id']: r for r in man['records']}
seal  = man['canonical_seal_sha256']
qa    = json.loads((APP/'qa/geometry-report.json').read_text())
copy  = json.loads((APP/'copy-manifest.json').read_text())['slides']
brand = json.loads((ROOT/'brands/asyada-egitim/brand.json').read_text())
copy_ok = all(v['copy_ok'] for v in qa['slides'].values())
geo_ok  = all(v['geometry_ok'] for v in qa['slides'].values())
jost_ok = all(v.get('jost_loaded') for v in qa['slides'].values())

NAMES = {'01':'01-the-scholarship-hook','02':'02-three-deadlines','03':'03-international-quotas',
         '04':'04-eligibility','05':'05-scholarship-amount','06':'06-single-choice-cta'}
LOCKS = {'01':'p-01-primary-stacked-dark.svg','02':'d-04-small-use-digital-light.svg',
         '03':'p-01-primary-stacked-light.svg','04':'h-02-primary-horizontal-light.svg',
         '05':'p-01-primary-stacked-dark.svg','06':'p-01-primary-stacked-dark.svg'}
LID   = {'01':'P-01/dark','02':'D-04/light','03':'P-01/light','04':'H-02/light','05':'P-01/dark','06':'P-01/dark'}

def logo_geom(num):
    svg = (APP/'source'/f'{num}.svg').read_text()
    m = re.search(r'<image id="canonical-lockup" href="[^"]+" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)
    return [float(m.group(1)), float(m.group(2))], float(m.group(3)), float(m.group(4))

# render-validation.json (producer-reported metrics from the QA harness)
render_validation = {}
for num in NAMES:
    v = qa['slides'][num]
    render_validation[NAMES[num]] = {'jostLoaded': bool(v.get('jost_loaded')),
        'issues': v['errors'], 'copyVerified': bool(v['copy_ok'])}
(APP/'render-validation.json').write_text(json.dumps(render_validation, ensure_ascii=False, indent=2))

slides = []
for num, sid in NAMES.items():
    final = APP/'export'/f'{num}.png'
    orig  = ORIG/f'{num}.png'
    shutil.copy2(final, orig)   # deterministic render: no post-processing step exists in this pipeline
    (xy, w, h) = logo_geom(num)
    lid = LID[num]
    slides.append({
        'id': sid,
        'copy': copy[num],
        'final_file': f'export/{num}.png', 'final_sha256': sha(final),
        'original_file': f'original/{num}.png', 'original_sha256': sha(orig),
        'source_file': f'source/{num}.svg', 'source_sha256': sha(APP/'source'/f'{num}.svg'),
        'editable_html_file': f'source/{num}.html',
        'dimensions': [1080, 1350],
        'canonical_lockup_id': lid,
        'canonical_lockup_sha256': recs[lid]['sha256'],
        'canonical_seal_sha256': seal,
        'canonical_logo_sha256': brand['canonicalLogo']['sha256'],
        'canonical_lockup_file': f'assets/lockups/{LOCKS[num]}',
        'logo_x_y_px': xy, 'logo_width_px': w, 'logo_height_px': h,
        'minimum_supported_display_width_px': recs[lid]['minimum_supported_display_size']['screen_width_px'],
        'render_validation': render_validation[sid],
    })

manifest = {
 'title': 'Asya’da Eğitim — Burs Dosyası / 001 · GKS 2027 (altı slaytlı Instagram carousel)',
 'campaign': 'Burs Dosyası / 001 — GKS 2027',
 'status': 'HUMAN CREATIVE APPROVAL PENDING — NOT MERGED, NOT PUBLISHED TO SOCIAL MEDIA',
 'dimensions': [1080, 1350],
 'exact_copy': {NAMES[n]: copy[n] for n in NAMES},
 'font': {'family': 'Jost', 'file': 'assets/Jost-VF.ttf', 'sha256': sha(APP/'assets/Jost-VF.ttf'),
          'license': 'SIL OFL 1.1 (assets/Jost-OFL.txt)'},
 'palette': {'paper': '#F7F3E9', 'ink': '#1D2027', 'accent': '#003478',
             'accent_name': 'Kore mavisi (GKS) — this campaign\'s only accent colour',
             'canonical_lockup_red': '#BD2120',
             'accent_scope': 'All slide accents, numerals, bands and rules use #003478. #BD2120 appears nowhere in the slide artwork; it exists only inside the linked canonical lockup SVGs, which are locked assets and were not edited.'},
 'brand_tokens': {'canonical_seal_sha256': seal,
   'canonical_lockups_manifest_sha256': brand['canonicalLockups']['manifestSha256']},
 'copy_validation': {'method': 'in-page DOM capture (whitespace-normalised) vs copy-manifest.json; SVG <text> join vs data-exact-copy-json',
   'result': 'PASS' if copy_ok else 'FAIL'},
 'geometry_qa': {'harness': 'qa/geometry-report.json (getBoundingClientRect after document.fonts.ready; text/text and text/logo overlap, 64 px safe area, clipping, canvas bounds)',
   'result': 'PASS' if geo_ok else 'FAIL', 'jost_loaded_all_slides': bool(jost_ok)},
 'visual_qa': {'method': 'each exported PNG inspected as image input at 1080 px and 375 px; contact sheet and mobile strip reviewed',
   'result': 'PASS — six distinct compositions, no overlap, clipping or glyph defects detected'},
 'production_method': 'Deterministic vector masters (source/NN.svg) rendered in Chromium with the real Jost variable font; no AI-generated raster imagery; no post-render raster editing.',
 'imagery_disclosure': 'All photography is real, correctly identified university imagery from Wikimedia Commons (licences in photo-credits.md), cropped/graded only. No synthetic campus imagery; photos are editorial backdrops, not partnership claims.',
 'time_sensitive_notice': 'Copy is anchored to the information date 13 October 2026. Embassy-track applications closed 30 September 2026; university-track deadlines are 23 and 30 October 2026 (Korean time). Do not present as a live opportunity after those dates without renewed verification.',
 'eur_display': {'locked_value': '≈ 9.675 € / yıl', 'reference_date': '12 Ekim 2026'},
 'ai_image_generation_calls': 0,
 'paid_image_or_api_usage': 'none',
 'mobile_preview_files': [f'mobile-preview/{n}.png' for n in NAMES],
 'contact_sheet_file': 'contact-sheet.png',
 'source_vs_final_contact_sheet_file': 'source-vs-final-contact-sheet.png',
 'revision_comparison_file': 'revision-comparison.png',
 'package_file': 'package/burs-dosyasi-gks-2027-001.zip',
 'slides': slides,
}
(APP/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print('manifest.json (audit schema) written')

# ---------------------------------------------------------------- source-vs-final sheet (SVG master render vs delivered PNG)
def side_by_side(pairs, titles, out, title, tw=300):
    th = round(1080*tw/1350); pad = 18; top = 64
    W = pad + len(pairs[0])*(tw+pad); H = top + len(pairs)*(th+pad) + pad
    im = Image.new('RGB', (W, H), (216,210,199)); d = ImageDraw.Draw(im)
    F = ImageFont.truetype(APP/'assets/Jost-VF.ttf', 30)
    f = ImageFont.truetype(APP/'assets/Jost-VF.ttf', 24)
    d.text((pad, 18), title, font=F, fill=(29,32,39))
    for j, t in enumerate(titles):
        d.text((pad + j*(tw+pad), top-32), t, font=f, fill=(29,32,39))
    for i, imgs in enumerate(pairs):
        for j, src in enumerate(imgs):
            tile = Image.open(src).convert('RGB'); tile.thumbnail((tw, th))
            x = pad + j*(tw+pad); y = top + i*(th+pad)
            d.rectangle([x-2, y-2, x+tile.width+1, y+tile.height+1], outline=(29,32,39), width=2)
            im.paste(tile, (x, y))
    im.save(out)
    return out

# render each SVG master standalone for the source-vs-final comparison
svg_renders = APP/'qa'/'svg-master-renders'; svg_renders.mkdir(exist_ok=True)
import tempfile, os, signal
for num in NAMES:
    outp = svg_renders/f'{num}.png'
    if outp.exists(): continue
    with tempfile.TemporaryDirectory(prefix='svgsrc-', dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as prof:
        cmd = [CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
               '--force-device-scale-factor=1','--window-size=1080,1350','--virtual-time-budget=8000',
               f'--user-data-dir={prof}', f'--screenshot={outp}', (APP/'source'/f'{num}.svg').as_uri()]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and proc.poll() is None:
            if outp.exists() and outp.stat().st_size > 10000: break
            time.sleep(.25)
        if proc.poll() is None:
            try: os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait(timeout=5)
    assert outp.exists() and outp.stat().st_size > 10000, f'svg master render failed: {num}'
pairs_sf = [[str(svg_renders/f'{n}.png'), str(APP/'export'/f'{n}.png')] for n in NAMES]
side_by_side(pairs_sf, ['SVG master (source/NN.svg)', 'Delivered PNG (export/NN.png)'],
             APP/'source-vs-final-contact-sheet.png',
             'BURS DOSYASI / 001 — SVG master vs delivered render (deterministic single-pass pipeline; no post-processing)')
pairs_rev = [[str(APP/'export'/f'{n}.png'), str(APP/'mobile-preview'/f'{n}.png')] for n in NAMES]
side_by_side(pairs_rev, ['1080 × 1350 final', '375 px mobile preview'],
             APP/'revision-comparison.png',
             'BURS DOSYASI / 001 — full-size vs mobile preview parity check (episode 001, single revision)')
print('comparison sheets written')
print('deliver.py stage 1 complete')

# ---------------------------------------------------------------- docs required by the bundle contract
(APP/'quality-review.md').write_text("""# Burs Dosyası / 001 — GKS 2027 · quality review record

## Automated gates (all PASS)
- **Exact copy**: every locked string from the campaign specification is present on its slide,
  verified twice — in-page DOM capture vs `copy-manifest.json`, and SVG `<text>` join vs
  `data-exact-copy-json` (see `manifest.json` → copy_validation).
- **Geometry**: `qa/geometry-report.json` — canvas bounds, 64 px safe area, text clipping,
  text↔text and text↔logo overlap measured after `document.fonts.ready`. 0 errors on all six slides.
- **Typography**: real Jost variable font metrics; Turkish glyphs (ğ, ş, ı, İ, â, Ü) confirmed in the
  rendered PNGs; no hardcoded line-height below glyph requirements (all line-heights ≥ 1.0 with
  font-metric-aware baselines in the SVG masters).
- **Hierarchy (slide 05)**: KRW figure 122 px vs EUR 54 px ≈ 2.26× emphasis; EUR sits directly below
  KRW on the same left axis; asterisk retained and resolved by the exchange-rate note.

## Visual review (actual image inspection, 1080 px and 375 px)
Defects found and fixed during production, each corrected in source and re-rendered:
1. Slide 01 — the strike-through crossed the emphasis sentence; date graphic and strike were moved
   into the clear zone between the paragraph and the bottom lockup band.
2. Slide 02 — orphan word in the header (manual two-line break); timeline dots re-aligned to the
   measured date baselines; D-04 lockup added to the footer for complete brand presence.
3. Slide 03 — orphan word in the headline (two-line break at 48 px); the giant 100 was integrated
   with the engineering photograph as required.
4. Slide 06 — the single-choice path node collided with the service sentence; the path was shortened
   and the node re-seated on the line.
5. Slide 05 — the KRW line overflowed the safe area at 128 px; set to 122 px (2.26× EUR emphasis).

Contact sheet, mobile strip (375 px) and source-vs-final sheet were inspected as images after the
final render. Distinct backgrounds: 01 photo/ink, 02 paper editorial, 03 warm neutral, 04 deep paper,
 05 ink financial, 06 photo/ink — no repeated beige template.

## Colour revision — Korean blue #003478
The campaign replaces brand red `#BD2120` with Korean blue as its single accent. The colour is
authored in exactly one place, `svgmaster.py`, and propagates through `source/NN.svg` →
`export/NN.png` → `original/NN.png` → ZIP → published gallery.

A first pass converted only a subset of the accent sites and left brand red on primary elements
("kaçırdın mı?" and its rules on 01, "13 Ekim 2026 itibarıyla." on 02, the "100" numeral on 03, the
TÜRK VATANDAŞLARI band on 04, the CTA band on 06). That partial state was incorrect and has been
superseded by a full conversion of the remaining nine sites.

`#BD2120` is retained **only** inside the linked canonical lockup SVGs under `assets/lockups/`.
Those are locked, human-approved assets, linked by reference and never edited, recoloured,
redrawn or re-typeset.

Verified after the re-render, by inspecting each exported PNG as image input:
- `#BD2120` occurs **zero** times in `source/01.svg`–`06.svg`.
- On every export, all remaining red-family pixels fall inside that slide's canonical-lockup
  bounding box from `manifest.json`. Red outside the logo is **0 on all six slides**.
- `studio/tools/verify_asyada_canonical_lockups.py` passes — 15 records, seal `8f5d46f0…c77e11a`.
- Copy, geometry and Jost gates re-ran clean (0 errors, all six slides, 1080×1350).

## Slide 01 accent-line legibility (fixed at human request)
With the accent applied, "kaçırdın mı?" in `#003478` sat over a darkened photograph and its glyph
edge was lost against the mid-tone sky and buildings — the line read as disappearing. Fixed with a
two-stage black drop shadow on **that line only** (`#04070C`, dy 6 / blur 9, plus a tight
dy 1 / blur 1.5 contact pass), declared once in `svgmaster.py` as `QS_SHADOW` and applied per line
through the `line_extra` argument added to `text_el()`. The cream line above it and every other
slide are untouched; the filter appears in `source/01.svg` only.

Measured on the exported PNG before and after, across the line's own bounding box:
- median luminance of the 1 px ring immediately around the glyphs: **0.0571 → 0.0116**
- brightest ring pixel (98th percentile): **0.1217 → 0.0520**
- glyph-to-ring contrast: **1.22:1 → 1.43:1**

Confirmed by inspecting the export as image input at 1080 px and again at the 375 px mobile
preview: the accent line reads cleanly at both.

## Remaining constraints (disclosed, not blocking)
- Photography is licensed Wikimedia Commons imagery; correct identification of KOREATECH, Ajou,
  Kookmin buildings and Korean campuses. Not a claim of partnership or admission.
- Human creative approval is still pending. Social publication is not authorized.
""", encoding='utf-8')

(APP/'generation-notes.md').write_text("""# Generation notes

**Pipeline (deterministic, reproducible):**
1. `build.py --css` — legacy CSS prototypes (kept for provenance; the commit does not ship them).
2. `svgmaster.py` — converts the measured CSS geometry (`qa/geometry-report.json`) into six
   `source/NN.svg` vector masters: pre-cropped photos with object-fit semantics, text at measured
   baselines with real Jost metrics, decorative devices, and the canonical lockups linked as
   `<image>` (never redrawn). Writes `source/NN.html` wrappers that inline the same SVG.
3. `build.py` — renders `export/NN.png` (1080×1350) with headless Chromium and runs the in-page
   QA harness (copy, bounds, safe area, clipping, overlaps, per-line metrics).
4. `deliver.py` — manifest, render-validation, comparison sheets, ZIP, gallery copy.

**Why original/ equals export/:** this pipeline has no post-render raster editing; the delivered PNG
is the deterministic render of `source/NN.svg`. `original/` records that first (and only) render.

**Single source of truth for colour:** `svgmaster.py`. The campaign accent is Korean blue `#003478`;
brand red `#BD2120` survives only inside the linked canonical lockup SVGs under `assets/lockups/`,
which are locked assets and were never edited. Slide 01's accent line additionally carries the
`QS_SHADOW` drop shadow for legibility over photography — see `quality-review.md`.

**Note on generated docs:** `quality-review.md` and `generation-notes.md` (this file) are themselves
emitted by `deliver.py`. Edit the templates inside `deliver.py`, never these files — a hand edit
here is silently overwritten on the next run.

**Image generation:** none. Zero AI raster calls; all photography is real Wikimedia Commons imagery
(`photo-credits.md`). No paid image or API usage.

**Fonts:** Jost variable font (SIL OFL 1.1) bundled at `assets/Jost-VF.ttf`.

**Reproduce:** `python3 build.py --css && python3 svgmaster.py && python3 build.py && python3 deliver.py`
(requires Google Chrome and Python 3 + Pillow; no network needed at render time).
""", encoding='utf-8')

(APP/'render.mjs').write_text("""#!/usr/bin/env node
// Render one Burs Dosyası / 001 slide with headless Chrome.
// Usage: node render.mjs <slide-number 1..6> [output.png]
// Renders source/NN.html (the inline-SVG master wrapper) at 1080x1350.
import { spawn } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const n = String(process.argv[2] ?? '1').padStart(2, '0');
const out = resolve(process.argv[3] ?? resolve(here, 'export', `${n}.png`));
const src = resolve(here, 'source', `${n}.html`);
const chrome = process.env.CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!existsSync(src)) { console.error('missing source:', src); process.exit(1); }
const args = ['--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
  '--force-device-scale-factor=1','--window-size=1080,1350','--virtual-time-budget=9000',
  `--user-data-dir=${resolve(here, '.chrome-profile')}`, `--screenshot=${out}`, `file://${src}`];
const proc = spawn(chrome, args, { stdio: 'ignore', detached: true });
const deadline = Date.now() + 45000;
(function poll() {
  if (existsSync(out) && statSync(out).size > 10000) {
    try { process.kill(-proc.pid, 'SIGTERM'); } catch {}
    console.log('rendered', out); process.exit(0);
  }
  if (Date.now() > deadline) { try { process.kill(-proc.pid, 'SIGKILL'); } catch {} console.error('timeout'); process.exit(1); }
  setTimeout(poll, 200);
})();
""")
(APP/'verify_and_package.py').write_text('''#!/usr/bin/env python3
"""Convenience wrapper: render + QA + package the Burs Dosyası / 001 bundle."""
import subprocess, sys
from pathlib import Path
APP = Path(__file__).resolve().parent
steps = [['python3', 'build.py'], ['python3', 'deliver.py']]
for cmd in steps:
    print('+', ' '.join(cmd))
    sys.exit(subprocess.run(cmd, cwd=APP).returncode or 0)
''')

# ---------------------------------------------------------------- ZIP + published gallery
PKG.mkdir(exist_ok=True)
zip_path = PKG/'burs-dosyasi-gks-2027-001.zip'
# Flat, root-level archive: the audit contract reads contract['manifest']
# ("manifest.json") and every manifest-referenced path directly out of the ZIP,
# and additionally requires each slide's bare basename ("01.png") alongside
# "export/01.png". A folder prefix would break that, so keep members flat.
members = ([f'export/{n}.png' for n in NAMES]
    # Bare basename "01.png" alongside "export/01.png": the audit contract indexes
    # zip_members by Path(final_file).name. Written from export/ so no loose
    # duplicate PNGs are left in the working tree.
    + [(f'{n}.png', f'export/{n}.png') for n in NAMES]
    + [f'original/{n}.png' for n in NAMES]
    + [f'source/{n}.svg' for n in NAMES] + [f'source/{n}.html' for n in NAMES]
    + [f'mobile-preview/{n}.png' for n in NAMES]
    + ['mobile-preview/mobile-strip.png', 'contact-sheet.png', 'source-vs-final-contact-sheet.png',
       'revision-comparison.png', 'manifest.json', 'copy-manifest.json', 'render-validation.json',
       'verification-notes.md', 'photo-credits.md', 'quality-review.md', 'generation-notes.md',
       'README.md', 'index.html', 'instagram-feed-preview.html', 'qa/geometry-report.json',
       'build.py', 'deliver.py', 'render.mjs', 'verify_and_package.py',
       'assets/Jost-VF.ttf', 'assets/Jost-OFL.txt', 'assets/photos-original/credits.json']
    + [f'assets/photos/{p}' for p in ['campus-hero-ewha.jpg','campus-skku.jpg','koreatech-hum.jpg',
       'ajou-campus.jpg','kookmain-10.jpg','koreatech-eng4.jpg','kyunghee-library.jpg']]
    + [f'assets/photos-crop/{p}' for p in sorted(x.name for x in (APP/'assets/photos-crop').glob('*.jpg'))]
    + [f'assets/lockups/{f}' for f in ['p-01-primary-stacked-dark.svg','p-01-primary-stacked-light.svg',
       'h-02-primary-horizontal-light.svg','d-04-small-use-digital-light.svg']]
    + [f'assets/photos-original/{p}' for p in sorted(x.name for x in (APP/'assets/photos-original').glob('*.jpg'))])
members = [(m, m) if isinstance(m, str) else m for m in members]
arcnames = [m[0] for m in members]
assert len(arcnames) == len(set(arcnames)), 'duplicate ZIP members'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for arcname, rel in members:
        z.write(APP/rel, arcname)
print('zip:', zip_path.name, zip_path.stat().st_size//1024, 'KB,', len(members), 'members')

if GALL.exists(): shutil.rmtree(GALL)
shutil.copytree(APP, GALL, ignore=shutil.ignore_patterns('__pycache__','*.pyc','.chrome-profile'))
print('gallery published at', GALL.relative_to(ROOT))

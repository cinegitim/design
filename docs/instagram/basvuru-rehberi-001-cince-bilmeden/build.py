#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the six-slide 'Başvuru Rehberi / 001 — Çince bilmeden Çin'de okuyabilir
miyim?' Instagram carousel for Asya'da Eğitim.

Pipeline: verify canonical lockups -> compose SVG sources -> render with
Chromium -> validate geometry -> write manifest. All copy is locked; all
photography is licensed Wikimedia Commons material recorded in assets/.
"""
import base64
import html
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/basvuru-rehberi-001')
CANON = ROOT / 'brands/asyada-egitim/assets/lockups/canonical-lockups.json'
JOST_SRC = ROOT / 'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf'
VERIFIER = ROOT / 'studio/tools/verify_asyada_canonical_lockups.py'
sys.path.insert(0, str(HERE))
from slides_data import (COPY, LOCKUP, SEAL_SHA, CANON, ROOT, W, H,
                          ASSETS, SOURCE, FINAL, ORIGINALS, PHOTOS,
                          BRAND_RED, INK, PAPER, CHINA_RED, GOLD_IMP,
                          GOLD_BRIGHT, IVORY, sha, font_css, prepare_assets)
from slides_build import SLIDES
import motifs

NS = '{http://www.w3.org/2000/svg}'
PALETTE = {
    'brand_red': BRAND_RED, 'brand_ink': INK, 'brand_paper': PAPER,
    'china_red': CHINA_RED, 'imperial_gold': GOLD_IMP,
    'bright_gold': GOLD_BRIGHT, 'warm_ivory': IVORY,
}


def svg_for(slide, rec, plate=False):
    """Compose one 1080x1350 SVG. plate=True renders the art-direction base
    (photography + Chinese motif geometry) without copy or the lockup."""
    # The brand wordmark is delivered by the canonical lockup, never retypeset.
    LOCKUP_DELIVERED = {"Asya'da Eğitim"}
    slack = [v for v in slide['texts'] if v[5]]
    values = [v[5] for v in slack]
    typeset = [c for c in COPY[slide['id']] if c not in LOCKUP_DELIVERED]
    assert ' '.join(values) == ' '.join(typeset), slide['id'] + ': copy mismatch'
    exact = html.escape(json.dumps(COPY[slide['id']], ensure_ascii=False), quote=True)
    texts = []
    for x, y, size, colour, weight, value, extra in slack:
        texts.append(
            f'<text x="{x}" y="{y}" font-family="Jost" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{extra or "0"}" fill="{colour}" '
            f'data-copy="{html.escape(value, quote=True)}">{html.escape(value)}</text>')
    cjk_marks = ''.join(
        f'<text x="{x}" y="{y}" font-family="SongCJK" font-size="{size}" '
        f'font-weight="400" letter-spacing=".14em" fill="{colour}">{html.escape(v)}</text>'
        for x, y, size, colour, v in slide.get('cjk', []))
    copy_group = (f'<g id="editable-campaign-copy" data-typeface="Jost" '
                  f'data-exact-copy-json="{exact}">{"".join(texts)}</g>')
    logo_file = Path(rec['canonical_file_path']).name
    vb = list(map(float, ET.parse(ASSETS / 'lockups' / logo_file).getroot()
                  .attrib['viewBox'].split()))
    x, y = LOCKUP[slide['id']][1]
    width = LOCKUP[slide['id']][2]
    height = width * vb[3] / vb[2]
    slide['logo_height'] = height
    logo = (f'<image id="canonical-lockup" href="../assets/lockups/{logo_file}" '
            f'x="{x}" y="{y}" width="{width}" height="{height:.6f}" '
            f'preserveAspectRatio="xMidYMid meet"/>')
    cjk_group = (f'<g id="chinese-cultural-marks" data-verification="names '
                 f'verified against zh.wikipedia.org and official university '
                 f'domains; secondary to Turkish copy">{cjk_marks}</g>'
                 if cjk_marks else '')
    layers = slide['layers']
    if not plate:
        layers = layers + copy_group + cjk_group + logo
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<title>{html.escape(slide['id'])} — Başvuru Rehberi / 001 · Çince bilmeden Çin'de okuyabilir miyim?</title>
<metadata>{{"campaign":"Başvuru Rehberi / 001","brand":"asyada-egitim","slide":"{slide['id']}","locked_copy":true}}</metadata>
<defs><style>{font_css()}</style>
{base64.b64encode(b'').decode() and ''}</defs>
{layers}
</svg>'''


def main():
    subprocess.run(['python3', str(VERIFIER)], check=True, capture_output=True)
    recs = prepare_assets()
    canonical = json.loads(CANON.read_text())
    records = {r['canonical_lockup_id']: r for r in canonical['records']}
    for s in SLIDES:
        lid = LOCKUP[s['id']][0]
        rec = records[lid]
        assert sha(ASSETS / 'lockups' / Path(rec['canonical_file_path']).name) == rec['sha256']
        markup = svg_for(s, rec, plate=False)
        (SOURCE / f"{s['id']}.svg").write_text(markup, encoding='utf-8')
        (SOURCE / f"{s['id']}.html").write_text(
            f'<!doctype html><html lang="tr"><meta charset="utf-8">'
            f'<title>{s["id"]} — Başvuru Rehberi / 001</title>'
            f'<style>html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;'
            f'background:{INK}}}svg{{display:block}}</style>{markup}</html>',
            encoding='utf-8')
        # art-direction plate without typeset copy or the canonical mark
        plate_markup = svg_for(s, rec, plate=True)
        (SOURCE / f"{s['id']}-plate.svg").write_text(plate_markup, encoding='utf-8')
        (SOURCE / f"{s['id']}-plate.html").write_text(
            f'<!doctype html><html lang="tr"><meta charset="utf-8">'
            f'<title>{s["id"]} — art-direction plate</title>'
            f'<style>html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;'
            f'background:{INK}}}svg{{display:block}}</style>{plate_markup}</html>',
            encoding='utf-8')
    subprocess.run(['node', str(HERE / 'render.mjs')], check=True,
                   env={**__import__('os').environ,
                        'PLAYWRIGHT_MODULE': '/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/pw/node_modules/playwright-core'})
    # render the copy-free plates as the recorded originals
    subprocess.run(['node', str(HERE / 'render-plates.mjs')], check=True,
                   env={**__import__('os').environ,
                        'PLAYWRIGHT_MODULE': '/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/pw/node_modules/playwright-core'})
    metrics = json.loads((HERE / 'render-validation.json').read_text())
    m = {
        'title': "Asya'da Eğitim — Başvuru Rehberi / 001 · Çince bilmeden Çin'de okuyabilir miyim?",
        'campaign': 'BAŞVURU REHBERİ / 001 — Çince bilmeden Çin\'de okuyabilir miyim?',
        'brand': 'asyada-egitim', 'revision': 1,
        'status': 'HUMAN CREATIVE REVIEW PENDING',
        'dimensions': [W, H],
        'production_method': ('Six composable 1080x1350 SVG slides: authentic licensed '
                              'Wikimedia Commons university photography, locally generated '
                              'deterministic Chinese editorial motif geometry, editable Jost '
                              'text and verbatim manifest-listed canonical lockup SVGs. '
                              'Rendered once at final resolution by Chromium/Playwright.'),
        'font': {'family': 'Jost', 'file': 'assets/Jost-VF.ttf',
                 'sha256': sha(ASSETS / 'Jost-VF.ttf'),
                 'license': 'SIL Open Font License 1.1',
                 'license_file': 'assets/Jost-OFL.txt'},
        'cjk_font': {'family': 'Songti SC', 'file': 'assets/SongtiSC-CJK-subset.ttf',
                     'sha256': sha(ASSETS / 'SongtiSC-CJK-subset.ttf'),
                     'note': 'Subset to the 17 verified characters used on slides 01 and 03. '
                             'No Arabic/Turkish glyph dependency.'},
        'palette': {**PALETTE, 'note': 'Brand values are canonical; China red, imperial '
                                       'gold, bright gold and warm ivory are campaign-only '
                                       'treatments and do not alter the canonical identity.'},
        'exact_copy': {s['id']: COPY[s['id']] for s in SLIDES},
        'copy_integrity': ('Every on-slide Turkish string is verbatim locked copy. '
                           'Line breaks split only at existing spaces; joining the '
                           'fragments reproduces the supplied text exactly. '
                           'Slide 06 line 15 "Asya\'da Eğitim" is delivered by the '
                           'approved canonical lockup, not retypeset — see exact-copy.json.'),
        'imagery_disclosure': ('All photographs are authentic, freely licensed Wikimedia '
                               'Commons images of the named institutions, credited in '
                               'caption-and-credits.md. No AI imagery, no generated '
                               'photography, no fabricated buildings, classrooms or labs.'),
        'image_generation': {'calls': 0, 'paid_backends': 0,
                             'note': 'Zero image-model calls by design. Photography is '
                                     'licensed source material; Chinese motifs are local '
                                     'deterministic SVG geometry.'},
        'chinese_art_direction': {
            'motif_families': ['Chinese window lattice geometry', 'xiangyun auspicious cloud forms',
                               'geometric seal-inspired accents', 'moon-gate circular architecture'],
            'primary_device_per_slide': {
                '01-cover': 'Circular moon-gate opening + ice-ray lattice panel (architecture)',
                '02-fields': 'Lattice geometry interrupting the photographic collage (window lattice)',
                '03-atlas': 'Lattice-inspired crop frames and gold location markers (window lattice)',
                '04-masters': 'Gold editorial rules + geometric seal-inspired accents (seal aesthetic)',
                '05-doctorate': 'Large abstracted circular architectural motif + xiangyun contour (cloud/architecture)',
                '06-dossier': 'Red archival-folder form, gold rules and restrained seal-like accents (stationery)',
            },
            'chinese_character_marks': {'留学': 'study abroad (verified)',
                                        '清华大学': 'Tsinghua University (verified)',
                                        '上海大学': 'Shanghai University (verified)',
                                        '浙江大学': 'Zhejiang University (verified)'},
            'verification': 'Character forms verified against zh.wikipedia.org and the official university domains (tsinghua.edu.cn, apply.shu.edu.cn, ism.zju.edu.cn, sirpa.fudan.edu.cn).',
        },
        'slides': [],
    }
    for s in SLIDES:
        lid = LOCKUP[s['id']][0]
        rec = records[lid]
        m['slides'].append({
            'id': s['id'],
            'final_file': f"final/{s['id']}.png",
            'final_sha256': sha(FINAL / f"{s['id']}.png"),
            'original_file': f"originals/{s['id']}.png",
            'original_sha256': sha(ORIGINALS / f"{s['id']}.png"),
            'source_file': f"source/{s['id']}.svg",
            'source_sha256': sha(SOURCE / f"{s['id']}.svg"),
            'editable_html_file': f"source/{s['id']}.html",
            'plate_source_file': f"source/{s['id']}-plate.svg",
            'dimensions': [W, H],
            'copy': COPY[s['id']],
            'canonical_lockup_id': lid,
            'canonical_lockup_sha256': rec['sha256'],
            'canonical_logo_sha256': SEAL_SHA,
            'canonical_seal_sha256': SEAL_SHA,
            'canonical_lockup_file': f"assets/lockups/{Path(rec['canonical_file_path']).name}",
            'logo_width_px': LOCKUP[s['id']][2],
            'logo_height_px': s['logo_height'],
            'logo_x_y_px': list(LOCKUP[s['id']][1]),
            'minimum_supported_display_width_px': rec['minimum_supported_display_size']['screen_width_px'],
            'render_validation': metrics[s['id']],
        })
    (HERE / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Built {len(SLIDES)} slides; canonical hashes unchanged.")


if __name__ == '__main__':
    main()

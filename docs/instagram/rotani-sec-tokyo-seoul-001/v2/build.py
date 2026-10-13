#!/usr/bin/env python3
"""Rotani Sec V2 - measured-layout composition build.

Verifies canonical assets, extracts real text geometry and a clean photograph
layer from the HTML templates, composes editable SVG with exact typography,
then renders six 1080x1350 PNGs with repository-pinned Playwright.
"""
from pathlib import Path
import hashlib, html, json, os, subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = ['01-admission-letter', '02-campus-geography', '03-six-universities',
       '04-english-taught', '05-accommodation', '06-final-decision']
LOCKUPS = {
    'D-04/light': ('d-04-small-use-digital-light.svg',
                   '2ff2263dcdab496e81cda01601f4abb746890c3478d05a2ff6b9278c71f9b59e', 200),
    'D-04/dark': ('d-04-small-use-digital-dark.svg',
                  'e77d5607426ce7764d4f5fdf2c7d4fb1f2779beaaabfc1e1644460133e55b335', 200),
    'H-02/dark': ('h-02-primary-horizontal-dark.svg',
                  'c9eb55f95a60924f34e6f7b043e81216963441833a4f158ff882d710cc8dd1e7', 528),
}
# Slide 02 releases text from horizontal grid columns, so its wrapped lines use
# the measured run order rather than a computed line index.
LINE_INDEX_EXCEPTIONS = {('02-campus-geography', n) for n in (2, 4, 5, 6)}
SEAL = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def esc(s):
    return html.escape(s, quote=True)


def compose(ident, layout, copy):
    groups = []
    for item in layout['copy']:
        runs = []
        for run_index, r in enumerate(item['runs']):
            if not r['text']:
                continue
            line_index = run_index if (ident, item['index']) in LINE_INDEX_EXCEPTIONS else r.get('lineIndex', 0)
            line_top = item['box']['y'] + item.get('paddingTop', 0) + line_index * r['lineHeight']
            # Real font metrics: the baseline sits inside the line box, plus the
            # half-leading offset when line-height is tighter than the font size.
            baseline = line_top + (r['lineHeight'] - r['fontSize']) / 2 + r['fontSize'] * 0.75
            runs.append(
                f'<text x="{r["x"]:.3f}" y="{baseline:.3f}" font-size="{r["fontSize"]:.3f}" '
                f'font-weight="{esc(str(r["fontWeight"]))}" letter-spacing="{r["letterSpacing"]:.3f}" '
                f'fill="{r["color"]}" xml:space="preserve" '
                f'data-linetop="{line_top:.3f}" data-lineheight="{r["lineHeight"]:.3f}">{esc(r["text"])}</text>')
        groups.append(f'<g data-copy="{item["index"]}" data-role="{esc(str(item.get("role", "")))}">{"".join(runs)}</g>')

    # Decorative editorial typography: rendered, audited, but outside the copy contract.
    decor = []
    for d in layout['decor']:
        baseline = d['box']['y'] + d['fontSize'] * 0.75 + (d.get('lineHeight', d['fontSize']) - d['fontSize']) / 2
        decor.append(f'<text x="{d["box"]["x"]:.3f}" y="{baseline:.3f}" font-size="{d["fontSize"]:.3f}" '
                     f'font-weight="{esc(str(d["fontWeight"]))}" fill="{d["color"]}" '
                     f'data-decor="1">{esc(d["text"])}</text>')
    decor_group = f'<g id="editorial-decoration">{"".join(decor)}</g>' if decor else ''

    logo = layout['logo']
    lock_name = LOCKUPS[logo['lockupId']][0]
    vb = list(map(float, ET.parse(HERE / 'assets/lockups' / lock_name).getroot().attrib['viewBox'].split()))
    logo_h = logo['width'] * vb[3] / vb[2]
    logo_y = logo['y'] + (logo['height'] - logo_h) / 2
    exact = esc(json.dumps(copy, ensure_ascii=False))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img">'
        f'<title>{esc(copy[0])}</title>'
        f'<defs><style>@font-face{{font-family:Jost;src:url(\'../assets/Jost-VF.ttf\') format(\'truetype\');font-weight:100 900;font-style:normal}}'
        f'text{{font-family:Jost,Arial,sans-serif;font-synthesis:none}}</style></defs>'
        f'<image href="../originals/{ident}.png" x="0" y="0" width="1080" height="1350"/>'
        f'{decor_group}'
        f'<g id="editable-campaign-copy" data-exact-copy-json="{exact}">{"".join(groups)}</g>'
        f'<image id="canonical-lockup" data-lockup-id="{logo["lockupId"]}" href="../assets/lockups/{lock_name}" '
        f'x="{logo["x"]:.3f}" y="{logo_y:.6f}" width="{logo["width"]:.3f}" height="{logo_h:.6f}" '
        f'preserveAspectRatio="xMidYMid meet"/></svg>')


def main():
    subprocess.run(['python3', str(ROOT / 'studio/tools/verify_asyada_canonical_lockups.py')], check=True)
    for ident, (name, digest, _) in LOCKUPS.items():
        assert sha(HERE / 'assets/lockups' / name) == digest, f'canonical lockup mismatch: {ident}'
    exact = json.loads((HERE / 'exact-copy.json').read_text())['slides']
    env = os.environ.copy()
    env.setdefault('PLAYWRIGHT_MODULE', str((ROOT / 'studio/cloud/node_modules/playwright-core').resolve()))
    subprocess.run(['node', str(HERE / 'extract-backgrounds.mjs')], check=True, env=env)
    layouts = json.loads((HERE / 'text-layout.json').read_text())
    for ident in IDS:
        markup = compose(ident, layouts[ident], exact[ident])
        (HERE / 'source' / f'{ident}.svg').write_text(markup, encoding='utf-8')
        (HERE / 'source' / f'{ident}.html').write_text(
            f'<!doctype html><html lang="tr"><meta charset="utf-8"><title>{ident}</title>'
            f'<style>html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:#1D2027}}'
            f'svg{{display:block}}</style>{markup}</html>', encoding='utf-8')
    subprocess.run(['node', str(HERE / 'render.mjs')], check=True, env=env)
    print('V2: six editable SVG/HTML slides built with measured geometry and canonical signatures.')


if __name__ == '__main__':
    main()

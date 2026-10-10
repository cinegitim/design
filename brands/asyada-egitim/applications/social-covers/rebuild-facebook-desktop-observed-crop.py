#!/usr/bin/env python3
"""Match Facebook desktop cover export to the real page crop supplied by the user."""
from __future__ import annotations
import base64, hashlib, json, re, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'docs/social-covers'; ASSETS=OUT/'assets'
LOCKUP_ID='D-04/light'
SEAL_SHA='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
LOCKUP_MANIFEST=json.loads((ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
RECORD=next(r for r in LOCKUP_MANIFEST['records'] if r['canonical_lockup_id']==LOCKUP_ID)
LOCKUP_PATH=ROOT/RECORD['canonical_file_path']
PIXEL_W,PIXEL_H=1702,617
VIEW_W,VIEW_H=851,308.5


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    if sha(LOCKUP_PATH)!=RECORD['sha256']:
        raise SystemExit('Canonical D-04 lockup hash mismatch')
    manifest_path=OUT/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    archive=OUT/'manifest-v04.json'
    if not archive.exists():
        archive.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (ASSETS/'Jost-VF.ttf').write_bytes((ROOT/'docs/instagram/carousel-01/assets/Jost-VF.ttf').read_bytes())
    raw=LOCKUP_PATH.read_bytes()
    vb=re.search(rb'<svg[^>]*viewBox="([^"]+)"',raw).group(1).decode()
    _,_,native_w,native_h=map(float,vb.split())
    logo_w=210; logo_h=logo_w*native_h/native_w
    logo=base64.b64encode(raw).decode()
    metadata={
      'brand_id':'asyada-egitim',
      'status':'APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE',
      'crop_basis':'Observed user-provided Facebook Page screenshot; approx. 2.76:1 desktop viewport',
      'canonical_lockup_id':LOCKUP_ID,
      'canonical_lockup_sha256':RECORD['sha256'],
      'canonical_logo_sha256':SEAL_SHA,
      'canonical_seal_sha256':SEAL_SHA,
    }
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{PIXEL_W}" height="{PIXEL_H}" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" aria-labelledby="title desc">
<title id="title">Facebook desktop cover — screenshot-matched wide crop</title>
<desc id="desc">Asya'da Eğitim Facebook Page desktop cover, 2.76:1 crop matched to the supplied live-page screenshot. Slogan, countries and canonical D-04 lockup.</desc>
<metadata>{json.dumps(metadata,ensure_ascii=False)}</metadata>
<defs><style>@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}.medium{{font-family:Jost,'Arial',sans-serif;font-weight:500;letter-spacing:-.02em}}.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.045em}}</style></defs>
<rect width="{VIEW_W}" height="{VIEW_H}" fill="#F7F3E9"/>
<rect width="13" height="{VIEW_H}" fill="#BD2120"/>
<path d="M478 48V{VIEW_H}" stroke="#1D2027" stroke-width="1" opacity=".2"/>
<image x="245" y="109" width="{logo_w}" height="{logo_h:.2f}" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{logo}"/>
<text x="510" y="104" fill="#1D2027" class="medium" font-size="25">Üniversite için</text>
<text x="510" y="151" fill="#BD2120" class="display" font-size="32">başka bir dünya var.</text>
<path d="M510 172H813" stroke="#BD2120" stroke-width="2"/>
<text x="510" y="215" fill="#1D2027" class="label" font-size="15">Çin <tspan fill="#BD2120">·</tspan> Japonya <tspan fill="#BD2120">·</tspan> Güney Kore</text>
<text x="510" y="243" fill="#1D2027" class="label" font-size="15">Singapur <tspan fill="#BD2120">·</tspan> Hong Kong</text>
</svg>'''
    slug='facebook-page-cover-desktop-v5-2x'
    svg_path=ASSETS/f'{slug}.svg'; png_path=ASSETS/f'{slug}.png'
    svg_path.write_text(svg)
    subprocess.run(['rsvg-convert','-w',str(PIXEL_W),'-h',str(PIXEL_H),str(svg_path),'-o',str(png_path)],check=True)
    item={
      'platform':'Facebook Page','id':slug,'crop':'desktop — matches supplied live-page screenshot',
      'dimensions_px':{'width':PIXEL_W,'height':PIXEL_H},
      'design_viewbox_px':{'width':VIEW_W,'height':VIEW_H},
      'png':f'assets/{png_path.name}','png_sha256':sha(png_path),
      'svg':f'assets/{svg_path.name}','svg_sha256':sha(svg_path),
      'formats':['PNG 2×','SVG editable source'],
      'canonical_lockup_id':LOCKUP_ID,'canonical_lockup_path':RECORD['canonical_file_path'],
      'canonical_lockup_sha256':RECORD['sha256'],
      'canonical_logo_sha256':SEAL_SHA,'canonical_seal_sha256':SEAL_SHA,
      'minimum_lockup_width_px':200,'lockup_width_design_px':logo_w,
      'render_scale':2,'supersedes':'facebook-page-cover-desktop-v4-2x',
      'status':'APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE',
    }
    assets=[]; replaced=False
    for old in manifest['assets']:
        if old['id'] in {'facebook-page-cover-desktop-v4-2x','facebook-page-cover-desktop-v5-2x'}:
            assets.append(item); replaced=True
        else: assets.append(old)
    if not replaced: assets.append(item)
    manifest['version']='05 — Facebook desktop crop matched to live screenshot'
    manifest['assets']=assets
    manifest['dimensions_researched']['Facebook Page']={
      'desktop_observed_ratio':'approximately 2.76:1',
      'desktop_export_px':[PIXEL_W,PIXEL_H],
      'desktop_evidence':'User-provided live Facebook Page screenshot; rendered cover area approx. 1920×696, ratio ~2.76:1. This is observed UI behavior, not a universal platform guarantee.',
      'mobile_ratio':'2.4:1','mobile_export_px':[1704,710],
      'official_source':'https://www.facebook.com/help/125379114252045',
      'official_source_note':'Meta help text lists 16:9 desktop, 2.4:1 mobile, and separately lists 851×315 as a fastest-loading JPG example. The supplied desktop screenshot instead renders at ~2.76:1; this export follows the observed page crop. Mobile export remains its own 2.4:1 version.',
    }
    manifest['superseded_manifest']='manifest-v04.json'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()

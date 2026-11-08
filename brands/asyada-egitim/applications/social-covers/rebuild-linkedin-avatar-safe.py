#!/usr/bin/env python3
"""Move the LinkedIn cover lockup clear of the company-page avatar overlay."""
from __future__ import annotations
import base64, hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'docs/social-covers'; ASSETS=OUT/'assets'
LOCKUP_ID='H-02/light'; SEAL_SHA='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
MANIFEST=json.loads((ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
RECORD=next(r for r in MANIFEST['records'] if r['canonical_lockup_id']==LOCKUP_ID)
LOCKUP=ROOT/RECORD['canonical_file_path']
W,H=3024,512; VW,VH=1512,256

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->None:
    if sha(LOCKUP)!=RECORD['sha256']: raise SystemExit('Canonical H-02/light lockup hash mismatch')
    out_manifest=OUT/'manifest.json'; m=json.loads(out_manifest.read_text())
    archive=OUT/'manifest-v05.json'
    if not archive.exists(): archive.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    (ASSETS/'Jost-VF.ttf').write_bytes((ROOT/'docs/instagram/carousel-01/assets/Jost-VF.ttf').read_bytes())
    raw=LOCKUP.read_bytes(); vb=re.search(rb'<svg[^>]*viewBox="([^"]+)"',raw).group(1).decode()
    _,_,nw,nh=map(float,vb.split()); logo_w=528; logo_h=logo_w*nh/nw
    encoded=base64.b64encode(raw).decode()
    metadata={'brand_id':'asyada-egitim','status':'APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE','layout_note':'H-02 lockup placed in the right safe zone; LinkedIn Page avatar overlap area at lower-left kept clear.','canonical_lockup_id':LOCKUP_ID,'canonical_lockup_sha256':RECORD['sha256'],'canonical_logo_sha256':SEAL_SHA,'canonical_seal_sha256':SEAL_SHA}
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {VW} {VH}" role="img" aria-labelledby="title desc">
<title id="title">LinkedIn Page cover — avatar-safe editorial layout</title>
<desc id="desc">Slogan and country list centered in the clear middle band. Exact H-02/light lockup sits on the right, outside the company profile avatar overlap.</desc>
<metadata>{json.dumps(metadata,ensure_ascii=False)}</metadata>
<defs><style>@font-face{{font-family:Jost;src:url('Jost-VF.ttf')}}.display{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:-.045em}}.medium{{font-family:Jost,'Arial',sans-serif;font-weight:500;letter-spacing:-.02em}}.label{{font-family:Jost,'Arial',sans-serif;font-weight:600;letter-spacing:.045em}}</style></defs>
<rect width="{VW}" height="{VH}" fill="#F7F3E9"/>
<rect width="18" height="{VH}" fill="#BD2120"/>
<path d="M320 38V218" stroke="#1D2027" stroke-width="1" opacity=".18"/>
<text x="365" y="78" fill="#1D2027" class="medium" font-size="29">Üniversite için</text>
<text x="365" y="128" fill="#BD2120" class="display" font-size="41">başka bir dünya var.</text>
<path d="M365 150H855" stroke="#BD2120" stroke-width="2"/>
<text x="365" y="184" fill="#1D2027" class="label" font-size="13">Çin <tspan fill="#BD2120">·</tspan> Japonya <tspan fill="#BD2120">·</tspan> Güney Kore <tspan fill="#BD2120">·</tspan> Singapur <tspan fill="#BD2120">·</tspan> Hong Kong</text>
<path d="M900 28V228" stroke="#1D2027" stroke-width="1" opacity=".22"/>
<image x="930" y="29" width="{logo_w}" height="{logo_h:.2f}" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{encoded}"/>
</svg>'''
    slug='linkedin-page-cover-v6-avatar-safe'; svg_path=ASSETS/f'{slug}.svg'; png_path=ASSETS/f'{slug}.png'
    svg_path.write_text(svg,encoding='utf-8')
    subprocess.run(['rsvg-convert','-w',str(W),'-h',str(H),str(svg_path),'-o',str(png_path)],check=True)
    a={
      'platform':'LinkedIn Page','id':slug,'dimensions_px':{'width':W,'height':H},
      'design_viewbox_px':{'width':VW,'height':VH},'png':f'assets/{png_path.name}','png_sha256':sha(png_path),
      'svg':f'assets/{svg_path.name}','svg_sha256':sha(svg_path),'formats':['PNG 2×','SVG editable source'],
      'canonical_lockup_id':LOCKUP_ID,'canonical_lockup_path':RECORD['canonical_file_path'],
      'canonical_lockup_sha256':RECORD['sha256'],'canonical_logo_sha256':SEAL_SHA,'canonical_seal_sha256':SEAL_SHA,
      'minimum_lockup_width_px':528,'lockup_width_px':logo_w,'render_scale':2,
      'safe_zone_note':'The lower-left avatar overlap zone is intentionally empty; H-02 is in the right-hand safe area.',
      'supersedes':'linkedin-page-cover-v4-2x','status':'APPLICATION CANDIDATE — NOT A NEW CANONICAL TEMPLATE'}
    m['version']='06 — Facebook screenshot crop + LinkedIn avatar-safe placement'
    m['assets']=[a if x['id']=='linkedin-page-cover-v4-2x' else x for x in m['assets']]
    m['dimensions_researched']['LinkedIn Page']['provided_export_px']=[W,H]
    m['dimensions_researched']['LinkedIn Page']['note']='2× raster export. Screenshot review showed the page avatar overlaps the lower-left cover area; canonical H-02 is moved to the right safe zone. Composition remains 1512×256.'
    out_manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()

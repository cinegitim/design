#!/usr/bin/env python3
"""Build Rotanı Seç #001 as photo backgrounds + editable SVG typography + locked SVG signatures."""
from pathlib import Path
import hashlib, html, json, os, subprocess
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
LOCKUPS={"D-04/light":("d-04-small-use-digital-light.svg","2ff2263dcdab496e81cda01601f4abb746890c3478d05a2ff6b9278c71f9b59e",200),"H-02/dark":("h-02-primary-horizontal-dark.svg","c9eb55f95a60924f34e6f7b043e81216963441833a4f158ff882d710cc8dd1e7",528)}
IDS=['01-hook','02-life-after-class','03-universities','04-language','05-budget','06-decision']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def esc(s):return html.escape(s,quote=True)

def svg_for(ident,layout,copy):
  groups=[]
  for item in layout['copy']:
    runs=[]
    for run_index,r in enumerate(item['runs']):
      if not r['text']:continue
      line_index=run_index if ident=='02-life-after-class' and item['index']==2 else r.get('lineIndex',0)
      line_top=item['bounds']['y']+item.get('paddingTop',0)+line_index*r['lineHeight']
      baseline=line_top+r['fontSize']*1.075
      runs.append(f'<text x="{r["x"]:.3f}" y="{baseline:.3f}" font-size="{r["fontSize"]:.3f}" font-weight="{esc(str(r["fontWeight"]))}" letter-spacing="{r["letterSpacing"]:.3f}" fill="{r["color"]}">{esc(r["text"])}</text>')
    groups.append(f'<g data-copy="{item["index"]}">{"".join(runs)}</g>')
  logo=layout['logo'];lock=LOCKUPS[logo['lockupId']];exact=esc(json.dumps(copy,ensure_ascii=False))
  vb=list(map(float,ET.parse(HERE/'assets/lockups'/lock[0]).getroot().attrib['viewBox'].split()))
  logo_h=logo['width']*vb[3]/vb[2];logo_y=logo['y']+(logo['height']-logo_h)/2
  box=''
  if ident in ('01-hook','04-language'):box=f'<rect x="{logo["x"]:.3f}" y="{logo["y"]:.3f}" width="{logo["width"]:.3f}" height="{logo["height"]:.3f}" fill="#F7F3E9" opacity=".94"/>'
  return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img"><title>{esc(copy[0])}</title><defs><style>@font-face{{font-family:Jost;src:url('../assets/Jost-VF.ttf') format('truetype');font-weight:100 900;font-style:normal}}text{{font-family:Jost,Arial,sans-serif;font-synthesis:none}}</style></defs><image href="../originals/{ident}.png" x="0" y="0" width="1080" height="1350"/>{box}<g id="editable-campaign-copy" data-exact-copy-json="{exact}">{''.join(groups)}</g><image id="canonical-lockup" data-lockup-id="{logo['lockupId']}" href="../assets/lockups/{lock[0]}" x="{logo['x']:.3f}" y="{logo_y:.6f}" width="{logo['width']:.3f}" height="{logo_h:.6f}" preserveAspectRatio="xMidYMid meet"/></svg>'''

def main():
 subprocess.run(['python3',str(ROOT/'studio/tools/verify_asyada_canonical_lockups.py')],check=True)
 for ident,(name,digest,_) in LOCKUPS.items():assert sha(HERE/'assets/lockups'/name)==digest,f'canonical lockup mismatch: {ident}'
 exact=json.loads((HERE/'exact-copy.json').read_text())['slides'];env=os.environ.copy();env.setdefault('PLAYWRIGHT_MODULE',str((ROOT/'studio/cloud/node_modules/playwright-core').resolve()))
 subprocess.run(['node',str(HERE/'extract-backgrounds.mjs')],check=True,env=env);layouts=json.loads((HERE/'text-layout.json').read_text())
 for ident in IDS:
  markup=svg_for(ident,layouts[ident],exact[ident]);(HERE/'source'/f'{ident}.svg').write_text(markup,encoding='utf-8');(HERE/'source'/f'{ident}.html').write_text(f'<!doctype html><html lang="tr"><meta charset="utf-8"><title>{ident}</title><style>html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:#1D2027}}svg{{display:block}}</style>{markup}</html>',encoding='utf-8')
 subprocess.run(['node',str(HERE/'render.mjs')],check=True,env=env);print('Built six editable SVG/HTML slides with clean photographic backgrounds, exact copy and locked canonical signatures.')
if __name__=='__main__':main()

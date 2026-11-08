#!/usr/bin/env python3
"""Export exact canonical symbol geometry with approved fills and opaque backgrounds.
Requires Python stdlib and rsvg-convert. No network, model calls or browser render.
Run from a repo checkout; the ZIP can also rebuild in its extracted directory.
"""
from pathlib import Path
import copy, hashlib, json, shutil, subprocess, sys, textwrap, xml.etree.ElementTree as E, zipfile
HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'brands/cin-egitim/assets/symbol.svg').is_file()),None)
OUT=ROOT/'docs/cin-egitim/social-avatars-02' if ROOT else HERE
SOURCE=ROOT/'brands/cin-egitim/assets/symbol.svg' if ROOT else HERE/'assets/canonical-symbol.svg'
SHA='1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381'
NS='{http://www.w3.org/2000/svg}'
E.register_namespace('',NS[1:-1])
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(SOURCE)==SHA,'Canonical source changed'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'assets').mkdir(exist_ok=True)
shutil.copyfile(SOURCE,OUT/'assets/canonical-symbol.svg') if SOURCE!=OUT/'assets/canonical-symbol.svg' else None
if HERE!=OUT:
    shutil.copyfile(Path(__file__),OUT/'build.py')
    shutil.copyfile(HERE/'application-spec.md',OUT/'application-spec.md')
variants=[('white','Beyaz','#FFFFFF',['#BF0C1A','#202020']),('red','Kırmızı','#BF0C1A',['#FFFFFF','#FFFFFF']),('dark','Koyu','#141414',['#BF0C1A','#FFFFFF'])]
records=[];specs=[]
canonical=E.parse(SOURCE).getroot()
for theme,label,bg,fills in variants:
    for kind,shape,n in [('profile','square',1080),('circle','circle',1080),('favicon','square',64)]:
        id=f'{kind}-{theme}'
        svg=E.Element(NS+'svg',{'width':str(n),'height':str(n),'viewBox':f'0 0 {n} {n}','role':'img','aria-label':f'Çin Eğitim — {label} {kind}'})
        E.SubElement(svg,NS+'title').text=f'Çin Eğitim — {label} / {kind}'
        if shape=='square': E.SubElement(svg,NS+'rect',{'width':str(n),'height':str(n),'fill':bg})
        else: E.SubElement(svg,NS+'circle',{'cx':str(n/2),'cy':str(n/2),'r':str(n/2),'fill':bg})
        h=n*.68;w=h*916/924
        mark=E.SubElement(svg,NS+'svg',{'id':'canonical-mark','viewBox':'0 0 916 924','x':f'{(n-w)/2:.8f}','y':f'{(n-h)/2:.8f}','width':f'{w:.8f}','height':f'{h:.8f}'})
        for i,group in enumerate(e for e in canonical if e.tag==NS+'g'):
            g=copy.deepcopy(group);g.set('fill',fills[i]);mark.append(g)
        path=OUT/f'{id}.svg';E.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)
        png=OUT/f'{id}.png'
        subprocess.run(['rsvg-convert','--width',str(n),'--height',str(n),'--output',str(png),str(path)],check=True)
        records.append({'id':id,'svg_file':path.name,'svg_sha256':digest(path),'png_file':png.name,'png_sha256':digest(png)})
        specs.append({'id':id,'dimensions':[n,n],'shape':shape,'background':bg,'symbol_fills':fills})
required=['assets/primary-logo.svg','index.html','build.py','application-spec.md','quality-review.md','handoff.md','assets/canonical-symbol.svg',
          'assets/manrope-normal-latin.woff2','assets/manrope-normal-latin-ext.woff2','assets/source-serif-4-normal-latin.woff2','assets/source-serif-4-normal-latin-ext.woff2','assets/manrope-OFL.txt','assets/sourceserif4-OFL.txt']
m={'version':1,'brand':'cin-egitim','status':'PRODUCED / APPLICATION REVIEW','canonical_logo_sha256':SHA,
   'canonical_seal_sha256':SHA,'canonical_lockup_id':'P-01/light','canonical_lockup_sha256':digest(OUT/'assets/primary-logo.svg'),
   'source_lockups_manifest_sha256':digest(ROOT/'brands/cin-egitim/assets/lockups/canonical-lockups.json') if ROOT else None,
   'toolchain':{'python':sys.version.split()[0],'rasterizer':subprocess.check_output(['rsvg-convert','--version'],text=True).strip(),'execution':'local macOS native vector recipe; no image model'},
   'exports':records,'package_file':'cin-egitim-social-avatars.zip'}
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
if ROOT:
    policy_path=ROOT/'studio/cloud/policy.json';policy=json.loads(policy_path.read_text())
    contract={'path':'docs/cin-egitim/social-avatars-02','format':'symbol-avatars','manifest':'manifest.json','canonical_logo_file':'brands/cin-egitim/assets/symbol.svg','canonical_logo_sha256':SHA,'required_files':required,'exports':specs}
    previous=next((b for b in policy['bundles'] if b['path']==contract['path']),None)
    if previous: assert previous==contract,'Existing contract cannot be changed'
    else:
        raw=policy_path.read_text();marker='\n  ]\n}'
        assert raw.count(marker)==1,'Unexpected policy layout'
        policy_path.write_text(raw.replace(marker,',\n'+textwrap.indent(json.dumps(contract,ensure_ascii=False,indent=2),'    ')+marker))
with zipfile.ZipFile(OUT/m['package_file'],'w',zipfile.ZIP_DEFLATED) as z:
    for name in required+['manifest.json']+[r[k] for r in records for k in ['svg_file','png_file']]:
        z.write(OUT/name,name)
print(f'Exported {len(records)} SVG + PNG pairs to {OUT}')

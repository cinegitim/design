#!/usr/bin/env python3
"""Independent checks on published final SVG files, not builder measurement masks.

These checks verify geometry/content, not visual approval or exact fidelity.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'brands/asyada-egitim/explorations/wordmark-ref/weight-study'
OUT=ROOT/'docs/asyada-seal/typography-weights/assets'
NS='http://www.w3.org/2000/svg'
SEAL=ROOT/'brands/asyada-egitim/assets/v01-canonical.svg'
SHA='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'

def signature(el):
    return (el.tag.split('}')[-1],tuple(sorted(el.attrib.items())),tuple(signature(c) for c in el))

def counter_count(m):
    _,lab,_,_=cv2.connectedComponentsWithStats((~np.pad(m,1)).astype('uint8'),8)
    outside=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])).tolist())
    return len(set(np.unique(lab))-outside-{0})

def main():
    assert hashlib.sha256(SEAL.read_bytes()).hexdigest()==SHA
    src=ET.fromstring(SEAL.read_bytes()); expected=[signature(c) for c in src if c.tag!=f'{{{NS}}}title']
    seal_checks=0
    for f in sorted(OUT.glob('tr*-en*-horizontal.svg'))+sorted(OUT.glob('tr*-en*-stacked.svg')):
        root=ET.fromstring(f.read_bytes())
        groups=[g for g in root.iter() if g.get('data-canonical-sha256')]
        assert len(groups)==1 and groups[0].get('data-canonical-sha256')==SHA,f
        assert [signature(c) for c in groups[0]]==expected,f'Canonical geometry changed: {f}'
        scale=groups[0].get('transform').split('scale(')[1].split(')')[0]
        assert ',' not in scale and len(scale.split())==1,f'Nonuniform seal scaling: {f}'
        seal_checks+=1
    assert seal_checks==48
    # Independently verify every offset changes the relative placement, not the
    # entire lockup or the seal. These alternatives are NOT alignment decisions.
    alignment_checks=0
    for f in sorted(OUT.glob('tr*-en*-*-align-*.svg')):
        root=ET.fromstring(f.read_bytes()); stem=f.name.split('-align-')[0]
        base=ET.fromstring((OUT/(stem+'.svg')).read_bytes())
        seal=[g for g in root.iter() if g.get('data-canonical-sha256')][0]
        bseal=[g for g in base.iter() if g.get('data-canonical-sha256')][0]
        assert signature(seal)==signature(bseal),f
        g=[g for g in root.iter() if g.get('data-wordmark')][0]
        bg=[g for g in base.iter() if g.get('data-wordmark')][0]
        def xy(el): return [float(v) for v in el.get('transform').removeprefix('translate(').removesuffix(')').split(',')]
        x,y=xy(g); bx,by=xy(bg); offset=int(g.get('data-native-offset'))
        assert x==bx and abs(y-by-offset)<1e-9,(f.name,'wrong relative offset')
        assert [signature(c) for c in g]==[signature(c) for c in bg],f
        assert [signature(c) for c in seal]==expected,f
        alignment_checks+=1
    assert alignment_checks==192
    original=ROOT/'brands/asyada-egitim/explorations/wordmark-ref/reference.jpg'
    assert original.read_bytes()==(OUT/'reference.jpg').read_bytes()
    counts={'tr1':7,'tr2':9,'en':15}; holes={'tr1':4,'tr2':0,'en':5}
    reports={}
    with tempfile.TemporaryDirectory(prefix='type-check-',dir=Path.home()/'.cache/brand-studio') as tmp:
        tmp=Path(tmp)
        for f in sorted(OUT.glob('tr*-en*-wordmark.svg')):
            root=ET.fromstring(f.read_bytes())
            letters=[p for p in root.iter(f'{{{NS}}}path') if p.get('data-glyph')]
            assert ''.join(p.get('data-glyph') for p in letters)=='ASYA’DAEĞİTİMEDUCATIONINASIA',f
            assert len([p for p in letters if p.get('fill')=='#BD2120'])==1,f
            assert not list(root.iter(f'{{{NS}}}text')),f
            # All glyph placement is translation only; outline scale is uniform
            # upstream. There is no late horizontal squash or shear.
            assert all(p.get('transform').startswith('translate(') and 'scale' not in p.get('transform') for p in letters),f
            # Rewrite root to EXPAND its actual final geometry into an independent
            # padded canvas. Exactly 25px + 1000px text measure + 25px.
            W=881; factor=1000/W; pad=25/factor; x0=42-pad
            root.set('viewBox',f'{x0} 40 {W+2*pad} 480')
            root.set('width','1050'); root.set('height',str(480*factor))
            svg=tmp/'actual.svg'; png=tmp/'actual.png'
            svg.write_bytes(ET.tostring(root)); subprocess.run(['rsvg-convert','-w','1050',str(svg),'-o',str(png)],check=True,capture_output=True)
            im=Image.open(png).convert('RGBA'); bg=Image.new('RGBA',im.size,(247,243,233,255)); bg.alpha_composite(im)
            rgb=np.array(bg.convert('RGB')).astype(float); mask=rgb@np.array([.2126,.7152,.0722])<140
            rows={}
            for key,lo,hi in [('tr1',55,220),('tr2',225,425),('en',450,510)]:
                m=mask[round((lo-40)*factor):round((hi-40)*factor)]
                yy,xx=np.where(m); left=int(xx.min())-25; right=int(xx.max())-25
                cc=cv2.connectedComponentsWithStats(m.astype('uint8'),8)[2][1:]
                cc=[c for c in cc if c[4]>=2]
                assert len(cc)==counts[key],(f.name,key,len(cc),'component/diacritic loss or collision')
                h=counter_count(m); assert h==holes[key],(f.name,key,h,'counter loss')
                assert abs(left)<=1 and abs(right-999)<=1,(f.name,key,left,right)
                rows[key]={'left_at_1000':left,'right_at_1000':right,'components':len(cc),'counters':h,
                           'edge_error':max(abs(left),abs(right-999))}
            reports[f.name]=rows
    assert len(reports)==24
    a={'status':'Technical verification only; HUMAN TYPOGRAPHY REVIEW PENDING',
       'canonical_logo_sha256':SHA,'canonical_geometry_comparisons':seal_checks,
       'relative_wordmark_offset_alternatives_checked':alignment_checks,
       'reference_bytes_unchanged':True,'rendered_final_pairings':reports,
       'worst_edge_error':max(v['edge_error'] for r in reports.values() for v in r.values()),
       'limits':'Does not establish glyph-shape fidelity, curvature quality, legibility approval, or a winner. Visual differences remain explicitly documented.'}
    (RUN/'verification.json').write_text(json.dumps(a,indent=2));(OUT/'verification.json').write_text(json.dumps(a,indent=2))
    print(json.dumps({k:v for k,v in a.items() if k!='rendered_final_pairings'},indent=2))

if __name__=='__main__': main()

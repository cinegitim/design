#!/usr/bin/env python3
"""Independent checks of final serialized review assets, never logo approval."""
from pathlib import Path
import copy
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/asyada-seal/final-lockups'
RUN=ROOT/'brands/asyada-egitim/explorations/final-lockup-family'
SOURCE=ROOT/'docs/asyada-seal/typography-weights/assets/tr550-en350-wordmark.svg'
SEAL=ROOT/'brands/asyada-egitim/assets/v01-canonical.svg'
NS='http://www.w3.org/2000/svg'
SHA='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
def hashof(data):return hashlib.sha256(data).hexdigest()
def xy(el):return [float(n) for n in re.search(r'translate\(([^)]+)\)',el.get('transform')).group(1).split(',')]
def triples(paths):return [(p.get('data-glyph'),p.get('d'),p.get('transform')) for p in paths]
def geometry(el):return (el.tag,{k:v for k,v in el.attrib.items() if k not in ['fill','mask']})
def bounds(el):
    x,y=xy(el);p=BoundsPen(None);parse_path(el.get('d'),TransformPen(p,(1,0,0,1,x,y)));return p.bounds
def merge(b):return [min(p[0] for p in b),min(p[1] for p in b),max(p[2] for p in b),max(p[3] for p in b)]
def count_holes(m):
    _,lab,_,_=cv2.connectedComponentsWithStats((~np.pad(m,1)).astype('uint8'),8)
    outside=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])).tolist())
    return len(set(np.unique(lab))-outside-{0})
def luminance(h):
    a=np.array([int(h[i:i+2],16)/255 for i in [1,3,5]])
    return float(np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722]))
def contrast(a,b):
    a,b=sorted([luminance(a),luminance(b)]);return (b+.05)/(a+.05)

def main():
    manifest=json.loads((RUN/'manifest.json').read_text()); seal=ET.fromstring(SEAL.read_bytes())
    assert hashof(SEAL.read_bytes())==SHA==manifest['canonical_logo_sha256']
    source=[p for p in ET.fromstring(SOURCE.read_bytes()).iter(f'{{{NS}}}path') if p.get('data-glyph')]
    assert manifest['source_wordmark_sha256']==hashof(SOURCE.read_bytes())
    original=[e for e in seal if e.tag!=f'{{{NS}}}title']
    variants={v['id']:v for v in manifest['variants']};report={};counts=0
    with tempfile.TemporaryDirectory(prefix='family-verify-',dir=Path.home()/'.cache/brand-studio') as td:
        td=Path(td)
        for name,item in manifest['outputs'].items():
            if name.endswith('.html'):
                data=(DOC/'assets'/name).read_bytes();assert hashof(data)==item['sha256']
                assert f'name="canonical_logo_sha256" content="{SHA}"'.encode() in data
                continue
            f=DOC/'assets'/name;raw=f.read_bytes();assert hashof(raw)==item['sha256']
            assert raw==(RUN/'assets'/name).read_bytes()
            root=ET.fromstring(raw)
            assert not list(root.iter(f'{{{NS}}}text')) and not list(root.iter(f'{{{NS}}}image')),name
            marks=[g for g in root.iter(f'{{{NS}}}svg') if g.get('data-canonical-logo-sha256')]
            assert len(marks)==1;mark=marks[0];assert mark.get('viewBox')=='0 0 400 370' and mark.get('overflow')=='hidden'
            assert abs(float(mark.get('width'))/float(mark.get('height'))-400/370)<1e-10
            if item['tone'].startswith('mono'):
                mask=next(mark.iter(f'{{{NS}}}mask'));features=list(mask)
                assert [geometry(e) for e in features]==[geometry(e) for e in original],name
                assert features[0].get('fill')=='#FFFFFF' and all(e.get('fill')=='#000000' for e in features[1:])
                paint=list(mark)[-1];assert geometry(paint)==geometry(original[0])
            else:
                features=[e for e in mark if e.tag!=f'{{{NS}}}title']
                assert [ET.tostring(e).strip() for e in features]==[ET.tostring(e).strip() for e in original],name
            counts+=1
            if 'companion' in item['variant']:continue
            v=variants[item['variant']]
            group=[g for g in root.iter(f'{{{NS}}}g') if g.get('data-wordmark')][0]; paths=list(group)
            expected=source if v['bilingual'] else source[:13]
            assert triples(paths)==triples(expected),(name,'changed glyph/position')
            tx,ty=xy(group);assert abs(tx-v['wordmark_translate'][0])<1e-7
            assert abs(ty-v['wordmark_translate'][1]-item['offset_native'])<1e-7
            # Every variant's seal stays at the same location for every offset.
            assert [float(mark.get(k)) for k in ['x','y','width','height']]==v['seal_box'],name
            view=[float(n) for n in root.get('viewBox').split()];vx,vy,vw,vh=view
            groups=[paths[:7],paths[7:13]]+([paths[13:]] if v['bilingual'] else [])
            b=merge([bounds(p) for p in paths]);text=[b[0]+tx,b[1]+ty,b[2]+tx,b[3]+ty]
            sx,sy,sw,sh=v['seal_box'];ink=merge([text,[sx,sy,sx+sw,sy+sh]])
            clear=min(ink[0]-vx,ink[1]-vy,vx+vw-ink[2],vy+vh-ink[3]);assert clear>=70-1e-6,(name,clear)
            widths=[merge([bounds(p) for p in row])[2]-merge([bounds(p) for p in row])[0] for row in groups]
            assert max(abs(w-881) for w in widths)<1e-5,(name,widths)
            tone=manifest['tones'][item['tone']]
            assert all(p.get('fill')==(tone['accent'] if p.get('data-glyph')=='’' else tone['type']) for p in paths)
            # Render this actual final SVG's text group at the proposed 1x minimum.
            # Removing seal for this measurement isolates lettering; full final
            # seal+text proof is separately rendered and visually inspected.
            probe=copy.deepcopy(root);probe.remove(next(g for g in list(probe) if g.get('data-canonical-logo-sha256')))
            s=td/'final.svg';p=td/'final.png';s.write_bytes(ET.tostring(probe))
            subprocess.run(['rsvg-convert','-w',str(v['min_px']),str(s),'-o',str(p)],check=True,capture_output=True)
            alpha=np.array(Image.open(p).convert('RGBA'))[:,:,3];m=alpha>=128;factor=v['min_px']/vw
            raster=[]
            for index,row in enumerate(groups):
                rb=merge([bounds(p) for p in row]);start=max(0,int(np.floor((rb[1]+ty-vy)*factor))-2);stop=min(m.shape[0],int(np.ceil((rb[3]+ty-vy)*factor))+2)
                band=m[start:stop]; yy,xx=np.where(band)
                components=cv2.connectedComponentsWithStats(band.astype('uint8'),8)[2][1:]
                meaningful=[c for c in components if c[4]>=1]
                holes=count_holes(band);expected_components=[7,9,15][index];expected_holes=[4,0,5][index]
                # Record native-resolution diagnostics, never hide sampling loss.
                raster.append({'line':['TR1','TR2','EN'][index],'components':len(meaningful),'expected_components':expected_components,
                               'enclosed_counters':holes,'expected_counters':expected_holes,'components_and_counters_preserved':len(meaningful)==expected_components and holes==expected_holes,
                               'visible_width_px':int(xx.max()-xx.min()+1),'cap_height_px':[140,139,35][index]*factor})
            report[name]={'source_glyph_geometry_identical':True,'seal_geometry_identical':True,'clearspace_min_native':round(clear,5),
                          'common_measure_native':widths,'minimum_canvas_width_px':v['min_px'],'native_raster_lines':raster}
            # 4x device-pixel render at the SAME CSS minimum distinguishes
            # valid enclosed outlines from 1x alpha-threshold hairline breaks.
            subprocess.run(['rsvg-convert','-w',str(v['min_px']*4),str(s),'-o',str(p)],check=True,capture_output=True)
            a=np.array(Image.open(p).convert('RGBA'))[:,:,3]; m4=a>=128;checks4=[]
            for index,row in enumerate(groups):
                rb=merge([bounds(p) for p in row]);start=max(0,int(np.floor((rb[1]+ty-vy)*factor*4))-3);stop=min(m4.shape[0],int(np.ceil((rb[3]+ty-vy)*factor*4))+3)
                band=m4[start:stop];cc=cv2.connectedComponentsWithStats(band.astype('uint8'),8)[2][1:];holes=count_holes(band)
                checks4.append({'line':['TR1','TR2','EN'][index],'components':len(cc),'enclosed_counters':holes})
                assert len(cc)==[7,9,15][index] and holes==[4,0,5][index],(name,'4x render lost a component/counter',index,len(cc),holes)
            report[name]['four_device_pixels_per_css_pixel']=checks4
            report[name]['native_sampling_caveat']='At 1x, light English contours can fall below 50% alpha at isolated pixels; keep antialiasing. Geometry/counters preserved at 4x. Native proofs require visual review.'
    assert counts==84 and len(report)==80
    problems=[(k,[r for r in v['native_raster_lines'] if not r['components_and_counters_preserved']]) for k,v in report.items() if any(not r['components_and_counters_preserved'] for r in v['native_raster_lines'])]
    pairs={k:round(contrast(a,b),2) for k,a,b in [('ink_on_paper','#1D2027','#F7F3E9'),('paper_on_ink','#F7F3E9','#1D2027'),('red_on_paper','#BD2120','#F7F3E9'),('red_on_ink','#BD2120','#1D2027'),('seal_white_on_red','#FFFFFF','#BD2120')]}
    validation={'status':'HUMAN FINAL LOCKUP APPROVAL PENDING','technical_checks_not_approval':True,'canonical_logo_sha256':SHA,
                'source_wordmark_sha256':hashof(SOURCE.read_bytes()),'outline_assets_checked':counts,'lockup_variants_checked':80,
                'typography_weights':{'tr':550,'en':350},'alignment_selected':None,'text_elements':0,'image_elements':0,'image_generation_calls':0,
                'source_lettering_unchanged':True,'seal_source_bytes_unchanged':True,'minimum_native_raster_diagnostics':problems,
                'four_device_pixel_counter_component_checks_passed':True,
                'contrast_ratios':pairs,'checks':report,'limits':['Proposed minimum sizes visually inspected, not human approved.','Native counter/component tests are not an OCR or clinical readability guarantee.','Red apostrophe remains original selected accent on dark backgrounds; logo marks are not normal body text.','D-04 is Turkish-only; English omission requires human confirmation.']}
    for directory in [RUN,DOC/'assets']:(directory/'validation.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False))
    summary={k:v for k,v in validation.items() if k not in ['checks','minimum_native_raster_diagnostics']}
    summary['native_alpha_threshold_diagnostic_asset_count']=len(problems)
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Reference-first Jost weight study. Measurements only, never raster tracing.

Every new letter comes from real OFL font outlines. No custom alphabet, image
generation, clipping-to-measure, or automatic winner selection.
"""
from pathlib import Path
import base64
import hashlib
import json
import statistics
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'brands/asyada-egitim/explorations/wordmark-ref/weight-study'
DOC = ROOT / 'docs/asyada-seal/typography-weights'
OUT = DOC / 'assets'
REF = ROOT / 'brands/asyada-egitim/explorations/wordmark-ref/reference.jpg'
FONT = RUN / 'sources/Jost-VF.ttf'
if not FONT.exists(): FONT = Path.home() / '.cache/brand-studio/fonts/shortlist/Jost-VF.ttf'
SEAL = ROOT / 'brands/asyada-egitim/assets/v01-canonical.svg'
SHA = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
TR = [400,450,500,550,600,650]
EN = [200,250,300,350]
INK, RED, PAPER = '#1D2027', '#BD2120', '#F7F3E9'
WIDTH, LEFT = 881.0, 42.0
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
TMP = Path(tempfile.mkdtemp(prefix='typography-', dir=str(Path.home()/'.cache/brand-studio')))
FONTS = {}

def doc(body, vb=(0,0,1012,558), background=False):
    x,y,w,h = vb
    bg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}"/>' if background else ''
    return f'<svg xmlns="{NS}" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}"><title>ASYA’DA EĞİTİM / EDUCATION IN ASIA — human typography review pending</title>{bg}{body}</svg>'

def render(svg, scale=1):
    root = ET.fromstring(svg); vb = [float(v) for v in root.attrib['viewBox'].split()]
    f = TMP / 'render.svg'; p = TMP / 'render.png'; f.write_text(svg)
    subprocess.run(['rsvg-convert','-w',str(round(vb[2]*scale)),str(f),'-o',str(p)],check=True,capture_output=True)
    return Image.open(p).convert('RGBA').copy()

def save(name, svg): (OUT/name).write_text(svg)

def mask_of(im):
    # Transparent pixels never count as black ink.
    bg = Image.new('RGBA', im.size, (247,243,233,255)); bg.alpha_composite(im.convert('RGBA'))
    return np.array(bg.convert('RGB')).astype(float) @ np.array([.2126,.7152,.0722]) < 140

def components(mask, lo, hi, area=20):
    _,_,stats,_ = cv2.connectedComponentsWithStats(mask[lo:hi].astype('uint8'),8)
    return [{'x':int(x),'y':int(y+lo),'w':int(w),'h':int(h),'area':int(a)}
            for x,y,w,h,a in sorted(stats[1:],key=lambda v:v[0]) if a>area]

def runs(arr):
    d=np.diff(np.pad(arr.astype('int8'),(1,1)))
    return list(zip(np.where(d==1)[0].tolist(),np.where(d==-1)[0].tolist()))

def metric(mask, char, cap, scale=1):
    yy,xx=np.where(mask); x0,x1,y0,y1=int(xx.min()),int(xx.max()+1),int(yy.min()),int(yy.max()+1)
    m=mask[y0:y1,x0:x1]; H,W=m.shape; vertical=[]; horizontal=[]
    if char in 'DEITMNU':
        for f in (.58,.64,.70,.76,.82):
            r=runs(m[min(H-1,round(H*f))])
            if not r: continue
            if char=='T': r=[min(r,key=lambda p:abs((p[0]+p[1])/2-W/2))]
            vertical.append((r[0][1]-r[0][0])/scale)
    if char in 'ETA':
        # T crossbar probes must be OUTSIDE its central vertical stem. Otherwise
        # a joined top-to-bottom run is the whole cap height, not bar thickness.
        for f in ((.20,.25,.30) if char=='T' else (.40,.45,.50)):
            r=runs(m[:,min(W-1,round(W*f))])
            if char=='A': r=[p for p in r if p[0]>.40*H and p[1]<.92*H]
            elif char=='E': r=[r[0],r[-1]] if r else []
            elif char=='T': r=r[:1]
            horizontal.extend((b-a)/scale for a,b in r)
    _,lab,stats,_=cv2.connectedComponentsWithStats((~np.pad(m,1)).astype('uint8'),8)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])).tolist()); holes=[]
    for i,(_,_,w,h,a) in enumerate(stats):
        if i and i not in edge and a>max(2,scale*scale):
            holes.append({'w':round(w/scale,3),'h':round(h/scale,3),'area':round(a/scale**2,3)})
    return {'width':round(W/scale,3),'height':round(H/scale,3),'width_cap_ratio':round(W/scale/cap,4),'width_height_ratio':round(W/H,4),
            'ink_fraction':round(float(m.mean()),4),'v_stem':round(statistics.median(vertical),3) if vertical else None,
            'h_stem':round(statistics.median(horizontal),3) if horizontal else None,'counters':holes}

def measure_reference():
    im=Image.open(REF).convert('RGB'); a=np.array(im).astype(float)
    lum=a@np.array([.2126,.7152,.0722]); neutral=(lum<140)&((a[:,:,0]-a[:,:,1])<25)
    ref={'method':'Original JPEG; neutral-ink threshold L<140 (roughly 50% edge coverage), red excluded; +/-1 native pixel uncertainty. No upscaling for measurements.',
         'lines':{},'glyphs':{},'diacritics':components(neutral,225,265),'source_sha256':hashlib.sha256(REF.read_bytes()).hexdigest()}
    for key,text,lo,hi in [('tr1','ASYADA',55,220),('tr2','EGITIM',265,420),('en','EDUCATIONINASIA',450,505)]:
        cc=components(neutral,lo,hi); assert len(cc)==len(text),(key,len(cc),text)
        flat=[c for ch,c in zip(text,cc) if ch not in 'SGOC']
        cap=int(statistics.median(c['h'] for c in flat)); baseline=int(statistics.median(c['y']+c['h'] for c in flat))
        data=[]
        for index,(ch,c) in enumerate(zip(text,cc)):
            m=neutral[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']]
            g={**c,**metric(m,ch,cap),'char':ch,'index':index}; data.append(g); ref['glyphs'][f'{key}-{index}']=g
        gaps=[cc[i+1]['x']-(c['x']+c['w']) for i,c in enumerate(cc[:-1])]
        vs=[g['v_stem'] for g in data if g['v_stem'] is not None]; hs=[g['h_stem'] for g in data if g['h_stem'] is not None]
        ref['lines'][key]={'cap':cap,'cap_top':baseline-cap,'baseline':baseline,
            'bbox_width':cc[-1]['x']+cc[-1]['w']-cc[0]['x'],'components':data,'visible_gaps':gaps,
            'v_stem_median':statistics.median(vs),'h_stem_median':statistics.median(hs),
            'v_ratio':statistics.median(vs)/cap,'h_ratio':statistics.median(hs)/cap,
            'glyph_ink_fraction_mean':statistics.mean(g['ink_fraction'] for g in data if g['char']!='I')}
    red=(a[:,:,0]-a[:,:,1]>40)&(a[:,:,0]-a[:,:,2]>40)&(lum<180)
    ref['apostrophe']=components(red,55,130)[0]; ref['threshold_sensitivity']={}
    for threshold in [110,140,170]:
        m=(lum<threshold)&((a[:,:,0]-a[:,:,1])<25)
        ref['threshold_sensitivity'][str(threshold)]=[metric(m[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']],'I',139)['v_stem']
                for c in ref['lines']['tr2']['components'] if c['char']=='I']
    return ref,im

def font(weight):
    if weight not in FONTS: FONTS[weight]=instantiateVariableFont(TTFont(FONT),{'wght':weight},inplace=False)
    return FONTS[weight]

def glyph(ch,weight,cap):
    f=font(weight); gs=f.getGlyphSet(); cmap=f.getBestCmap()
    bp=BoundsPen(gs); gs[cmap[ord('E')]].draw(bp); k=cap/(bp.bounds[3]-bp.bounds[1])
    b=BoundsPen(gs); gs[cmap[ord(ch)]].draw(b); x0,y0,x1,y1=b.bounds
    p=SVGPathPen(gs); gs[cmap[ord(ch)]].draw(TransformPen(p,(k,0,0,-k,-x0*k,0)))
    return {'d':p.getCommands(),'w':(x1-x0)*k,'top':-y1*k,'bottom':-y0*k,'scale':k}

def glyph_metrics(ch,weight,cap):
    g=glyph(ch,weight,cap)
    svg=doc(f'<path d="{g["d"]}" fill="{INK}"/>',(-12,g['top']-12,g['w']+24,g['bottom']-g['top']+24))
    return metric(mask_of(render(svg,4)),ch,cap,4)

def apostrophe(ref):
    # Source-matched punctuation correction only, not a custom alphabet.
    # Jost U+2019 is a diagonal slab: visibly incompatible with the original
    # rounded comma. Five intentional cubics retain the source's measured
    # 30x49 envelope, bulb and descending tail. No tracing or fit is performed.
    c=ref['apostrophe']; w,h=c['w'],c['h']
    d=(f'M {w*.5} 0 '
       f'C {w*.22} 0 0 {h*.13} 0 {h*.31} '
       f'C 0 {h*.45} {w*.13} {h*.54} {w*.4} {h*.57} '
       f'C {w*.4} {h*.71} {w*.26} {h*.85} {w*.13} {h} '
       f'C {w*.55} {h*.94} {w} {h*.60} {w} {h*.31} '
       f'C {w} {h*.10} {w*.80} 0 {w*.5} 0 Z')
    return {'d':d,'w':w,'h':h,'top':c['y']}

def build_line(key,weight,ref):
    r=ref['lines'][key]; chars={'tr1':'ASYA’DA','tr2':'EĞİTİM','en':'EDUCATIONINASIA'}[key]
    cap=r['cap']; base=r['baseline']; objs=[(ch,apostrophe(ref) if ch=='’' else glyph(ch,weight,cap)) for ch in chars]
    orig=r['components']; positions=orig[:4]+[ref['apostrophe']]+orig[4:] if key=='tr1' else orig
    gaps=[positions[i+1]['x']-p['x']-p['w'] for i,p in enumerate(positions[:-1])]
    delta=(WIDTH-sum(g['w'] for ch,g in objs)-sum(gaps))/(len(objs)-1)
    x=LEFT; bodies=[]; placed=[]
    for i,(ch,g) in enumerate(objs):
        y=g['top'] if ch=='’' else base
        bodies.append(f'<path data-glyph="{ch}" d="{g["d"]}" transform="translate({x:.6f},{y:.6f})" fill="{RED if ch=="’" else INK}"/>')
        placed.append({'char':ch,'x':x,'width':g['w'],'y':y,'top':y if ch=='’' else y+g['top'],
                       'bottom':y+g['h'] if ch=='’' else y+g['bottom']})
        x+=g['w']+(gaps[i]+delta if i<len(gaps) else 0)
    return ''.join(bodies),{'left':LEFT,'right':x,'visible_width':x-LEFT,'tracking_delta':delta,
                           'visible_gaps':[v+delta for v in gaps],'glyphs':placed}

def line_tile(key,weight,ref):
    lo,hi={'tr1':(55,220),'tr2':(225,420),'en':(450,505)}[key]
    body,placement=build_line(key,weight,ref); view=(0,lo,1012,hi-lo)
    r=ref['lines'][key]
    guides=''.join(f'<line x1="34" x2="937" y1="{y}" y2="{y}" stroke="#bfb8a7" stroke-width="0.5" stroke-dasharray="4 4"/>' for y in [r['cap_top'],r['baseline']])
    save(f'{key}-{weight}.svg',doc(guides+body,view,True))
    encoded=base64.b64encode(REF.read_bytes()).decode()
    overlay=doc(f'<image href="data:image/jpeg;base64,{encoded}" x="0" y="0" width="1012" height="558"/>'
                +guides+f'<g opacity="0.5">{body.replace(INK,"#0074BC").replace(RED,"#0074BC")}</g>',view)
    save(f'{key}-{weight}-overlay.svg',overlay)
    return placement

def seal_at(x,y,k):
    assert hashlib.sha256(SEAL.read_bytes()).hexdigest()==SHA
    src=ET.fromstring(SEAL.read_bytes())
    inner=''.join(ET.tostring(c,encoding='unicode') for c in src if c.tag!=f'{{{NS}}}title')
    return f'<g data-canonical-sha256="{SHA}" transform="translate({x},{y}) scale({k})">{inner}</g>'

def wordmark(tr,en,ref):
    return ''.join(build_line(key,tr if key!='en' else en,ref)[0] for key in ['tr1','tr2','en'])

def lockups(tr,en,ref):
    body=wordmark(tr,en,ref); top,bottom=68.0,495.0; block=bottom-top; gap,pad=85.0,44.0
    # Real 400:370 aspect, established spacing and seal sizes. Fixed across trials.
    for kind in ['horizontal','stacked']:
        if kind=='horizontal':
            k=426/370; sw=400*k; W=pad*2+sw+gap+WIDTH; H=pad*2+block
            mark=seal_at(pad,pad,k); tx=pad+sw+gap-LEFT; ty=pad-top
        else:
            k=370/400; sh=370*k; W=pad*2+WIDTH; H=pad*2+sh+gap+block
            mark=seal_at(pad+(WIDTH-370)/2,pad,k); tx=pad-LEFT; ty=pad+sh+gap-top
        save(f'tr{tr}-en{en}-{kind}.svg',doc(mark+f'<g data-wordmark="review" transform="translate({tx},{ty})">{body}</g>',(0,0,W,H),True))
        # Genuine relative-alignment alternatives: only the wordmark moves,
        # vertically by native units. The seal and all glyph geometry stay fixed.
        for offset,label in [(-4,'m4'),(0,'0'),(4,'p4'),(8,'p8')]:
            save(f'tr{tr}-en{en}-{kind}-align-{label}.svg',doc(
                mark+f'<g data-wordmark="review" data-native-offset="{offset}" transform="translate({tx},{ty+offset})">{body}</g>',(0,0,W,H),True))
    save(f'tr{tr}-en{en}-wordmark.svg',doc(body,(LEFT,45,WIDTH,465),True))

def closeups(ref,im):
    specs=[('A','tr1',0),('S','tr1',1),('D','tr1',4),('G','tr2',1),('M','tr2',5),('Ğ','tr2',1),('İ','tr2',2)]
    enc=base64.b64encode(REF.read_bytes()).decode()
    for ch,key,idx in specs:
        r=ref['lines'][key]; c=r['components'][idx]; baseline=r['baseline']; cap=r['cap']
        top=min(c['y'],234) if ch in 'Ğİ' else c['y']
        source_box=[c['x'],c['y'],c['x']+c['w'],c['y']+c['h']]
        if ch in 'Ğİ':
            accent=min(ref['diacritics'],key=lambda d:abs(d['x']+d['w']/2-c['x']-c['w']/2))
            source_box=[min(source_box[0],accent['x']),min(source_box[1],accent['y']),
                        max(source_box[2],accent['x']+accent['w']),max(source_box[3],accent['y']+accent['h'])]
        glyphs={w:glyph(ch,w,cap) for w in TR}
        y0=min(top-12,min(baseline+g['top']-12 for g in glyphs.values()))
        # One identical canvas per glyph, shared by original and all six weights.
        # Display zoom multiplies native dimensions, not a normalized tile height.
        vb=(c['x']-12,y0,max(c['w'],max(g['w'] for g in glyphs.values()))+24,baseline-y0+12)
        # Isolate this source glyph with 2px of antialiasing clearance. Wider
        # common canvases must not accidentally include its next neighbour.
        x0,y0,x1,y1=source_box
        clip=f'<defs><clipPath id="source-glyph"><rect x="{x0-2}" y="{y0-2}" width="{x1-x0+4}" height="{y1-y0+4}"/></clipPath></defs>'
        image=clip+f'<image clip-path="url(#source-glyph)" href="data:image/jpeg;base64,{enc}" x="0" y="0" width="1012" height="558"/>'
        save(f'glyph-{ch}-reference.svg',doc(image,vb,True))
        for w in TR:
            g=glyphs[w]
            path=f'<path d="{g["d"]}" fill="{INK}" transform="translate({c["x"]},{baseline})"/>'
            save(f'glyph-{ch}-{w}.svg',doc(path,vb,True))
            save(f'glyph-{ch}-{w}-overlay.svg',doc(image+f'<g opacity="0.5">{path.replace(INK,"#0074BC")}</g>',vb,True))

def final_checks(tr,en,ref):
    body=wordmark(tr,en,ref); result={}
    # Padded canvas allows overflow to be detected. Width is NOT enforced by clipping.
    scale=1000/WIDTH; pad=24/scale
    # Exact integer 24px padding + 1000px ink measure + 24px padding.
    view=(LEFT-pad,40,WIDTH+2*pad,480)
    im=render(doc(body,view),scale); mask=mask_of(im)
    for key,lo,hi in [('tr1',55,220),('tr2',225,425),('en',450,510)]:
        a=round((lo-view[1])*scale); b=round((hi-view[1])*scale)
        _,x=np.where(mask[a:b]); left=(x.min()/scale+view[0]-LEFT)*scale; right=(x.max()/scale+view[0]-LEFT)*scale
        result[key]={'left_at_1000':round(left,3),'right_at_1000':round(right,3),
                     'max_edge_error':round(max(abs(left),abs(right-999)),3)}
    im.save(RUN/f'tr{tr}-en{en}-actual-final.png')
    return result

def inspection_plates(ref,im):
    """Direct final-SVG renders for visible, not prompt-based, review."""
    rows=[]
    for weight in [None]+TR:
        image=im.crop((0,55,1012,425)) if weight is None else render(doc(
            build_line('tr1',weight,ref)[0]+build_line('tr2',weight,ref)[0],(0,55,1012,370),True)).convert('RGB')
        row=Image.new('RGB',(1012,396),'white'); ImageDraw.Draw(row).text((12,8),'ORIGINAL' if weight is None else f'JOST {weight} / same cap height / unified width',fill='black'); row.paste(image,(0,26)); rows.append(row)
    plate=Image.new('RGB',(1012,sum(i.height for i in rows)),'white'); y=0
    for row in rows: plate.paste(row,(0,y)); y+=row.height
    plate.save(RUN/'turkish-actual-comparison.png')
    rows=[]
    for weight in [None]+EN:
        image=im.crop((0,450,1012,505)) if weight is None else render((OUT/f'en-{weight}.svg').read_text()).convert('RGB')
        row=Image.new('RGB',(1012,86),'white'); ImageDraw.Draw(row).text((12,6),'ORIGINAL EN' if weight is None else f'JOST EN {weight}',fill='black'); row.paste(image,(0,25)); rows.append(row)
    plate=Image.new('RGB',(1012,sum(i.height for i in rows)),'white'); y=0
    for row in rows: plate.paste(row,(0,y)); y+=row.height
    plate.save(RUN/'english-actual-comparison.png')
    rows=[]
    for ch in ['A','S','D','G','M','Ğ','İ']:
        tiles=[]
        for label,name in [('Original',f'glyph-{ch}-reference.svg')]+[(f'Jost {w}',f'glyph-{ch}-{w}.svg') for w in [500,550,600]]:
            image=render((OUT/name).read_text(),2).convert('RGB')
            tile=Image.new('RGB',(max(360,image.width),image.height+26),'white'); ImageDraw.Draw(tile).text((6,6),f'{ch} / {label}',fill='black'); tile.paste(image,(0,26)); tiles.append(tile)
        row=Image.new('RGB',(sum(i.width for i in tiles),max(i.height for i in tiles)),'white'); x=0
        for tile in tiles: row.paste(tile,(x,0)); x+=tile.width
        rows.append(row)
    plate=Image.new('RGB',(max(i.width for i in rows),sum(i.height for i in rows)),'white'); y=0
    for row in rows: plate.paste(row,(0,y)); y+=row.height
    plate.save(RUN/'glyphs-actual-comparison.png')
    render((OUT/'tr550-en350-horizontal.svg').read_text()).save(RUN/'horizontal-actual.png')
    render((OUT/'tr550-en350-stacked.svg').read_text()).save(RUN/'stacked-actual.png')

def build():
    RUN.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    (RUN/'sources').mkdir(exist_ok=True)
    if FONT != RUN/'sources/Jost-VF.ttf': (RUN/'sources/Jost-VF.ttf').write_bytes(FONT.read_bytes())
    if (OUT/'OFL.txt').exists(): (RUN/'sources/OFL.txt').write_bytes((OUT/'OFL.txt').read_bytes())
    for note in ['muse-review.md','visual-review.md']:
        if (RUN/note).exists(): (OUT/note).write_bytes((RUN/note).read_bytes())
    # Remove early unused raster crops; the published originals now share the
    # exact same SVG viewBox as each corresponding weight comparison.
    for old in OUT.glob('glyph-*-reference.png'): old.unlink()
    ref,im=measure_reference(); (OUT/'reference.jpg').write_bytes(REF.read_bytes())
    experiments={}; placement={}
    for key in ['tr1','tr2','en']:
        cap=ref['lines'][key]['cap']; weights=EN if key=='en' else TR
        for w in weights:
            mets=[glyph_metrics(c['char'],w,cap) for c in ref['lines'][key]['components']]
            vs=[m['v_stem'] for m in mets if m['v_stem'] is not None]; hs=[m['h_stem'] for m in mets if m['h_stem'] is not None]
            v=statistics.median(vs); h=statistics.median(hs)
            experiments[f'{key}-{w}']={'weight':w,'cap':cap,'v_stem':v,'h_stem':h,'v_ratio':v/cap,'h_ratio':h/cap,
                'glyph_ink_fraction_mean':statistics.mean(m['ink_fraction'] for c,m in zip(ref['lines'][key]['components'],mets) if c['char']!='I'),
                'v_error':v-ref['lines'][key]['v_stem_median'],'h_error':h-ref['lines'][key]['h_stem_median'],'glyphs':mets}
            placement[f'{key}-{w}']=line_tile(key,w,ref)
    closeups(ref,im)
    scores={w:sum((abs(experiments[f'{k}-{w}']['v_error'])+abs(experiments[f'{k}-{w}']['h_error']))/ref['lines'][k]['cap'] for k in ['tr1','tr2']) for w in TR}
    tr_review=sorted(sorted(TR,key=lambda w:scores[w])[:2])
    en_review=sorted(sorted(EN,key=lambda w:abs(experiments[f'en-{w}']['v_error'])+abs(experiments[f'en-{w}']['h_error']))[:2])
    checks={}
    for tr in TR:
        for en in EN: lockups(tr,en,ref); checks[f'tr{tr}-en{en}']=final_checks(tr,en,ref)
    inspection_plates(ref,im)
    audit={'status':'HUMAN TYPOGRAPHY REVIEW PENDING','candidate_B':'REJECTED; not regenerated','winner':None,'alignment_selected':None,
        'reference':ref,'experiments':experiments,'placement':placement,
        'advisory_review_subset':{'turkish':tr_review,'english':en_review,'basis':'Two closest flat-stem matches among requested values. Advisory only; all values visible. Not approval.'},
        'render_checks':checks,'canonical_logo_sha256':SHA,'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),
        'font_source':'https://github.com/google/fonts/tree/main/ofl/jost',
        'apostrophe':'One independent punctuation correction, drawn with five intentional cubic segments to the original measured envelope. Shared unchanged across all weights. Not Candidate B geometry; no custom alphabet.',
        'limitations':['JPEG edge uncertainty approximately +/-1 px.','Weight match does not establish glyph-shape fidelity.',
             'No raster curvature-sign-flip or IoU score used as approval criterion.','Full overlays expose required common-width spacing changes as well as shape differences.']}
    (RUN/'measurement.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)); (OUT/'measurement.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False))
    page(audit)
    print(json.dumps({'reference':{k:{f:r[f] for f in ['cap','v_stem_median','h_stem_median','v_ratio','h_ratio','glyph_ink_fraction_mean']} for k,r in ref['lines'].items()},
        'review_subset':audit['advisory_review_subset'],'experiment_stems':{k:[r['v_stem'],r['h_stem']] for k,r in experiments.items()},
        'worst_edge_error':max(v['max_edge_error'] for c in checks.values() for v in c.values())},indent=2))

def page(a):
    r=a['reference']; e=a['experiments']; subset=a['advisory_review_subset']; chunks=[HEADER]
    chunks.append('<section id="reference"><p class="eyebrow">01 / VISUAL AUTHORITY</p><h2>The original. Not a font specimen.</h2><p>This JPEG governs weight, proportions, counters and spacing. B is rejected. Previous A at 700 is unapproved and superseded by these experiments.</p><figure class="source"><img src="assets/reference.jpg" width="1012" height="558" alt="Original supplied typography reference"><figcaption>Original file, unchanged · 1012 × 558 · no enhancement.</figcaption></figure></section>')
    chunks.append('<section><p class="eyebrow">02 / ORIGINAL MEASUREMENTS</p><h2>Two weight roles, measured separately.</h2><div class="scroll"><table><tr><th>Line</th><th>Flat cap</th><th>Vertical stem</th><th>V / cap</th><th>Horizontal stem</th><th>H / cap</th><th>Glyph ink density</th></tr>')
    for k,label in [('tr1','ASYA’DA'),('tr2','EĞİTİM'),('en','EDUCATION IN ASIA')]:
        m=r['lines'][k]; chunks.append(f'<tr><th>{label}</th><td>{m["cap"]} px</td><td>{m["v_stem_median"]:.2f} px</td><td>{m["v_ratio"]:.3f}</td><td>{m["h_stem_median"]:.2f} px</td><td>{m["h_ratio"]:.3f}</td><td>{100*m["glyph_ink_fraction_mean"]:.1f}%</td></tr>')
    chunks.append('</table></div><p class="caption">Neutral ink L&lt;140, approximately 50% edge coverage; original pixels, no interpolation. Approximately ±1 native pixel uncertainty, especially significant on 35px English caps. Vertical probes: D/E/I/T/M/N/U stems. Horizontal probes: E arms, T bar (off-centre), A crossbar. Density is mean filled fraction inside non-I glyph ink boxes (I is excluded because its filled rectangle always reads 100%), not an approval score.</p><details><summary>Glyph proportions, counters and measured gaps</summary><div class="scroll"><table><tr><th>Glyph / row</th><th>Width / cap</th><th>Width / height</th><th>Counter bounds (px)</th><th>Ink density</th></tr>')
    for k,m in r['glyphs'].items():
        holes='; '.join(f'{h["w"]:.1f} × {h["h"]:.1f}' for h in m['counters']) or 'No enclosed counter'
        chunks.append(f'<tr><th>{m["char"]} / {k}</th><td>{m["width_cap_ratio"]:.3f}</td><td>{m["width_height_ratio"]:.3f}</td><td>{holes}</td><td>{100*m["ink_fraction"]:.1f}%</td></tr>')
    chunks.append('</table></div>')
    for k,m in r['lines'].items(): chunks.append(f'<p><b>{k.upper()} visible gaps:</b> {", ".join(str(g) for g in m["visible_gaps"])} px. Original ink measure {m["bbox_width"]} px.</p>')
    chunks.append('<p>Requested common width: 881px. Original TR2 and English measures differ, so unified specimens necessarily change spacing; the glyphs never stretch. A negative Y/A bounding-box gap need not mean actual ink collision.</p></details></section>')
    chunks.append('<section><p class="eyebrow">03 / TURKISH · ONE TYPEFACE, SIX WEIGHTS</p><h2>Compare the weight, then the shape.</h2><p>Same source flat cap heights: '+str(r['lines']['tr1']['cap'])+'px / '+str(r['lines']['tr2']['cap'])+'px. Guides mark the shared flat-cap and baseline. Jost’s pointed A/M overshoots are retained and reported, not compressed. Every original/candidate pair uses the identical pixel scale; scroll horizontally on narrow screens. Blue ink overlays the unchanged original at exactly 50% opacity.</p>')
    for w in TR:
        chunks.append(f'<article class="experiment"><h3>Jost {w}<span>Turkish experiment · not selected</span></h3>')
        for k in ['tr1','tr2']:
            lo,hi=(55,220) if k=='tr1' else (225,420); h=hi-lo
            chunks.append(f'<div class="native"><div class="label">ORIGINAL / {k.upper()}</div><div class="refstrip" style="height:{h}px"><img src="assets/reference.jpg" alt="Original {k}" style="top:-{lo}px"></div><div class="label">JOST {w} / COMMON WIDTH 881</div><img src="assets/{k}-{w}.svg" width="1012" height="{h}" alt="Jost {w}, {k}, identical cap height"><details><summary>Show 50% transparent overlay · same scale</summary><img src="assets/{k}-{w}-overlay.svg" width="1012" height="{h}" alt="50 percent blue Jost {w} over original {k}"></details></div>')
            m=e[f'{k}-{w}']; chunks.append(f'<p class="caption">{k.upper()}: vertical {m["v_stem"]:.2f}px ({m["v_error"]:+.2f} vs source), horizontal {m["h_stem"]:.2f}px ({m["h_error"]:+.2f}), glyph density {100*m["glyph_ink_fraction_mean"]:.1f}%.</p>')
        chunks.append('</article>')
    chunks.append('</section><section><p class="eyebrow">04 / ENGLISH · SEPARATE LIGHT-WEIGHT STUDY</p><h2>A distinct, lighter role.</h2><p>200 / 250 / 300 / 350. All 35px caps, identical scale. If the measured source lies outside this range, it is reported—not forced to fit.</p>')
    for w in EN:
        m=e[f'en-{w}']; chunks.append(f'<article class="experiment"><h3>Jost {w}<span>English experiment · not selected</span></h3><div class="native"><div class="label">ORIGINAL ENGLISH</div><div class="refstrip" style="height:55px"><img src="assets/reference.jpg" style="top:-450px" alt="Original English"></div><div class="label">JOST {w} / CAP 35 PX</div><img src="assets/en-{w}.svg" width="1012" height="55" alt="English Jost {w}"><details><summary>Show 50% transparent overlay · same scale</summary><img src="assets/en-{w}-overlay.svg" width="1012" height="55" alt="English Jost {w} overlay"></details></div><p class="caption">Vertical {m["v_stem"]:.2f}px ({m["v_error"]:+.2f}); horizontal {m["h_stem"]:.2f}px ({m["h_error"]:+.2f}); density {100*m["glyph_ink_fraction_mean"]:.1f}%.</p></article>')
    chunks.append('</section><section><p class="eyebrow">05 / GLYPH FIDELITY</p><h2>Changing weight cannot change every letterform.</h2><p>Original first, then six Turkish weights. G: body alone; Ğ: original breve included. Left-ink/baseline aligned at source cap height, no width normalization. Zoom uses real outlines, not upscaled tracing.</p><label class="zoom">Close-up size <select id="zoom"><option value="1">100%</option><option value="4" selected>400%</option><option value="8">800%</option></select></label>')
    for ch in ['A','S','D','G','M','Ğ','İ']:
        chunks.append(f'<details class="glyph" open><summary>{ch} · original / 400 / 450 / 500 / 550 / 600 / 650</summary><div class="glyphstrip"><figure><span>Original</span><img class="glyphimg" src="assets/glyph-{ch}-reference.svg" alt="Original {ch}"></figure>')
        for w in TR: chunks.append(f'<figure><span>Jost {w}</span><img class="glyphimg" src="assets/glyph-{ch}-{w}.svg" alt="Jost {w} {ch}"><a href="assets/glyph-{ch}-{w}-overlay.svg" target="_blank">50% overlay ↗</a></figure>')
        chunks.append('</div></details>')
    chunks.append('</section><section><p class="eyebrow">06 / REVIEW-ONLY LOCKUPS</p><h2>Strong Turkish. Lighter English.</h2>')
    chunks.append(f'<p>Measured-stem review subset: Turkish {subset["turkish"]}; English {subset["english"]}. Two closest sampled stem matches per role—not approved candidates. Shape fidelity remains unresolved. All 24 pairings remain available; changing a preview is not a selection.</p>')
    chunks.append('<div class="controls"><label>Turkish preview <select id="trweight">'+''.join(f'<option value="{w}">{w}</option>' for w in TR)+'</select></label><label>English preview <select id="enweight">'+''.join(f'<option value="{w}">{w}</option>' for w in EN)+'</select></label><label>Relative vertical offset <select id="alignment"><option value="m4">−4 native px</option><option value="0" selected>0 · comparison baseline</option><option value="p4">+4 native px</option><option value="p8">+8 native px</option></select></label></div><p id="previewnote" class="caption">Preview only; no winner selected.</p><div class="lockup"><img id="horizontal" alt="Unselected horizontal lockup with canonical seal"></div><div class="lockup stacked"><img id="stacked" alt="Unselected stacked lockup with canonical seal"></div><p><a id="svgdownload">Open vector wordmark ↗</a></p><div class="smalluses" id="smalluses"></div><p class="caption">Exact 400:370 seal geometry, fixed across trials. Established 85px gap / 44px padding. Offset previews move only the wordmark relative to the fixed seal; positive values move it downward. The previous alternatives stay untouched: <a href="../smooth/">historical alignment review</a>. No alignment chosen.</p></section>')
    chunks.append('<section><p class="eyebrow">07 / LIMITATIONS & VERIFICATION</p><h2>No claim of exact fidelity.</h2><div id="differences">'+FINDINGS+'</div><p><b>Muse multimodal advisory review:</b> independently flagged A/M/G structure, weight mismatch and English underweight after inspecting the actual rendered comparisons. Not approval. <a href="assets/muse-review.md">Review and factual reconciliation</a>.</p>')
    chunks.append('<h3>Body proportions: original / review samples</h3><div class="scroll"><table><tr><th>Glyph</th><th>Source W/H</th><th>Jost 500 W/H</th><th>Jost 550 W/H</th><th>Source counter</th><th>Jost 500 counter</th></tr>')
    for ch,k,idx in [('A','tr1',0),('S','tr1',1),('D','tr1',4),('G','tr2',1),('M','tr2',5)]:
        m=r['lines'][k]['components'][idx]; q=e[f'{k}-500']['glyphs'][idx]; q2=e[f'{k}-550']['glyphs'][idx]
        def holes(v): return '; '.join(f'{h["w"]:.1f} × {h["h"]:.1f}' for h in v['counters']) or 'open'
        chunks.append(f'<tr><th>{ch}</th><td>{m["width_height_ratio"]:.3f}</td><td>{q["width_height_ratio"]:.3f}</td><td>{q2["width_height_ratio"]:.3f}</td><td>{holes(m)}</td><td>{holes(q)}</td></tr>')
    worst=max(v['max_edge_error'] for c in a['render_checks'].values() for v in c.values())
    chunks.append('</table></div><p class="caption">Widths and heights are actual ink bounds at the shared flat-cap scale, not normalized square glyphs. Jost’s A/M pointed overshoots remain visible; they have not been flattened or compressed.</p>')
    chunks.append('<div class="status">HUMAN TYPOGRAPHY REVIEW PENDING</div><ul><li>B rejected and untouched; A not approved.</li><li>Separate variable-font instances for Turkish and English. No heavy-700 production default.</li><li>All letters: real Jost outlines. One source-matched red comma correction, five deliberate cubic segments in the measured 30×49px envelope, shared unchanged across trials. Not a custom alphabet and not B geometry.</li><li>Common 881px vector measure; independently tested with a padded 1000px wordmark render, not clipping. Worst measured edge error: '+str(worst)+'px across all 24 pairings.</li><li>Canonical seal SHA-256: <code>'+SHA+'</code>.</li><li>No canonical files updated, no winner or alignment selected.</li></ul><p><a href="assets/measurement.json">Full measurements, gaps, ratios and manifests (JSON)</a> · <a href="assets/verification.json">Independent final-SVG verification (JSON)</a> · <a href="assets/OFL.txt">Jost SIL OFL licence</a> · <a href="../vector-review/">Historical rejected/unapproved study</a></p></section>')
    chunks.append(FOOTER.replace('@TR@',str(subset['turkish'][0])).replace('@EN@',str(subset['english'][0])))
    (DOC/'index.html').write_text(''.join(chunks))

FINDINGS='''<p><b>Jost cannot reproduce this reference by weight changes alone.</b> The actual rendered comparisons show:</p>
<ul><li><b>A:</b> Jost has a pointed, taller apex instead of the source’s small flat top; the triangular counter is larger/taller at 500. The source counter is 34×39px versus 38×44px at 500. The crossbar thickness/height also differs.</li>
<li><b>S:</b> Jost is wider and its upper/lower bowl balance and terminal cuts differ. The source is compact, with a fuller spine; increasing weight changes density but not the same silhouette.</li>
<li><b>D:</b> Jost’s bowl/counter is more open. At 500 the counter is about 69×96px versus the source’s 57×87px. The source stem is 28px; Jost 500 is about 24px.</li>
<li><b>G:</b> decisive structural mismatch: the source has a squared return and vertical inner edge below the bar; Jost continues around a circular lower-right bowl. Jost’s body is also wider: about 141px at 500 versus 128px.</li>
<li><b>M:</b> decisive structural mismatch: the source has upright outer stems, flat shoulders and a blunt central junction. Jost has splayed sides, pointed high shoulders and a sharp lower V. At 500 it is about 153px wide versus 138px.</li>
<li><b>Ğ:</b> inherits G’s mismatch. Jost’s breve is deeper and sits higher than the shallow source cup; its dimensions change with weight.</li>
<li><b>İ:</b> the dot is real and present, but its size and clearance differ by weight. Around 500 the dot is roughly 27×26px versus about 24×24px in the thresholded source.</li></ul>
<p><b>English:</b> all requested samples remain thinner than the original under the same measurement method. Jost 350 is closest within this set (vertical ≈3.5px vs source ≈5px; horizontal ≈3.25px vs ≈4px), but is not an exact weight match. This is visible as well as measured. The source is still lighter than Turkish in stem/cap ratio and apparent size; that does not mean its font weight number must be 200–350 in Jost.</p>
<p><b>No single sampled Turkish weight matches both rows perfectly.</b> The source’s D stem in TR1 is about 28px; its E/I/T/M stems in TR2 are about 23px. The 500/550 subset is only an advisory compromise, not a winner. Clean font contours are necessary but do not establish fidelity.</p>'''

HEADER='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Asya’da Eğitim · Reference-first typography weight review</title><style>
:root{--paper:#F7F3E9;--ink:#1D2027;--red:#BD2120;--muted:#625d53;--line:#d9d1bf}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,sans-serif}main{max-width:1120px;margin:auto;padding:48px 28px 100px}h1{font-size:clamp(34px,5vw,60px);line-height:1.1;letter-spacing:-.04em;max-width:15ch;margin:18px 0}h2{font-size:30px;line-height:1.2;letter-spacing:-.025em;margin:10px 0 18px}h3{font-size:22px;margin:0 0 16px}h3 span{font-size:13px;font-weight:400;display:block;color:var(--muted)}p{max-width:78ch}.eyebrow,.label{font:11px/1.4 ui-monospace,monospace;letter-spacing:.1em;color:var(--muted)}section{border-top:1px solid var(--line);padding-top:30px;margin-top:54px}.status{border-left:4px solid var(--red);background:white;padding:18px 20px;font-weight:700;letter-spacing:.04em;font-size:13px;margin:24px 0}.source img{width:100%;max-width:1012px;height:auto}.source{margin:24px 0}.caption,figcaption{font-size:13px;color:var(--muted)}.experiment{padding:24px 18px;border:1px solid var(--line);margin-top:28px;background:#fffcf5}.native{width:100%;overflow-x:auto;margin:12px 0}.native>img,.native details>img{display:block;max-width:none;width:1012px}.refstrip{position:relative;overflow:hidden;width:1012px}.refstrip img{position:absolute;width:1012px;height:558px;left:0;max-width:none}.label{margin:14px 0 8px}summary{cursor:pointer;padding:10px 0;min-height:44px}a{color:#9d1919;text-underline-offset:3px}table{border-collapse:collapse;width:100%;font-size:13px;white-space:nowrap}th,td{text-align:left;border-bottom:1px solid var(--line);padding:12px 14px}th{font-weight:600}.scroll{overflow:auto}code{overflow-wrap:anywhere}.glyphstrip{display:flex;gap:24px;overflow:auto;padding:12px 0 24px}.glyphstrip figure{margin:0;flex:none}.glyphstrip span{display:block;font:12px ui-monospace,monospace;margin-bottom:16px}.glyphstrip a{display:block;font-size:12px}.glyphimg{width:auto;max-width:none;height:640px;object-fit:contain;object-position:left bottom}.controls{display:flex;gap:24px;flex-wrap:wrap}.controls label,.zoom{font-size:13px}select{font:inherit;padding:10px;margin-left:8px;min-height:44px;background:white;color:var(--ink);border:1px solid var(--line)}.lockup img{display:block;width:100%;height:auto}.stacked img{max-width:520px;margin:auto}.smalluses{display:flex;flex-wrap:wrap;align-items:start;gap:22px}.smalluses figure{margin:0}.smalluses img{display:block}.smalluses figcaption{font-size:11px}.lockup{border:1px solid var(--line);padding:18px;margin:20px 0}footer{margin-top:60px;font-size:13px}@media(max-width:640px){main{padding:28px 16px 60px}.experiment{padding:16px 10px}h2{font-size:26px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
</style></head><body><main><p class="eyebrow">ASYA’DA EĞİTİM / TYPOGRAPHY FIDELITY STUDY</p><h1>Reference first.<br>Weight second.</h1><p>One typeface, not new brand directions. Six Turkish weights and four English weights, independently measured against the original.</p><div class="status">B REJECTED · A NOT APPROVED · NO WINNER SELECTED</div><nav><a href="#reference">Original</a> · <a href="../">Seal gallery</a></nav>'''
FOOTER='''<footer>Inspection only. No approval, canonicalization or alignment decision.</footer></main><script>
const tr=document.getElementById('trweight'),en=document.getElementById('enweight'),alignment=document.getElementById('alignment');tr.value='@TR@';en.value='@EN@';
function update(){const stem=`assets/tr${tr.value}-en${en.value}`;for(const kind of ['horizontal','stacked'])document.getElementById(kind).src=`${stem}-${kind}-align-${alignment.value}.svg`;const a=document.getElementById('svgdownload');a.href=`${stem}-wordmark.svg`;a.target='_blank';document.getElementById('previewnote').textContent=`Preview TR ${tr.value} / EN ${en.value}; offset ${alignment.options[alignment.selectedIndex].text}. Not selected or approved. Small sizes are diagnostic stress tests, not approved minimum sizes.`;document.getElementById('smalluses').innerHTML=[320,200,120].map(w=>`<figure><img src="${stem}-wordmark.svg" width="${w}" alt="Current preview at ${w} px"><figcaption>${w}px visible wordmark width</figcaption></figure>`).join('')}
tr.addEventListener('change',update);en.addEventListener('change',update);alignment.addEventListener('change',update);update();
const zoom=document.getElementById('zoom');function sizeGlyphs(){document.querySelectorAll('.glyphimg').forEach(el=>{if(el.naturalWidth){el.style.width=(el.naturalWidth*Number(zoom.value))+'px';el.style.height=(el.naturalHeight*Number(zoom.value))+'px'}})}zoom.addEventListener('change',sizeGlyphs);document.querySelectorAll('.glyphimg').forEach(el=>el.addEventListener('load',sizeGlyphs));sizeGlyphs();
</script></body></html>'''

if __name__=='__main__': build()

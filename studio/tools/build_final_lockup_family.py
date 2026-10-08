#!/usr/bin/env python3
"""Compose review-only lockups from the selected existing paths. No typesetting.

No font loading, glyph editing, image generation or canonicalization. SVG
rasterization is used only for deterministic inspection/minimum-size proofs.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from PIL import Image, ImageDraw
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'brands/asyada-egitim/explorations/final-lockup-family'
DOC=ROOT/'docs/asyada-seal/final-lockups'
SOURCE=ROOT/'docs/asyada-seal/typography-weights/assets/tr550-en350-wordmark.svg'
SEAL=ROOT/'brands/asyada-egitim/assets/v01-canonical.svg'
SHA='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
NS='http://www.w3.org/2000/svg'; ET.register_namespace('',NS)
INK,PAPER,RED='#1D2027','#F7F3E9','#BD2120'
TONES={'light':{'type':INK,'accent':RED,'background':PAPER},
       'dark':{'type':PAPER,'accent':RED,'background':INK},
       'mono-ink':{'type':INK,'accent':INK,'background':PAPER},
       'mono-paper':{'type':PAPER,'accent':PAPER,'background':INK}}
OFFSETS={'m4':-4,'0':0,'p4':4,'p8':8}
FAMILY=[
 {'id':'P-01','name':'Primary stacked','mode':'stacked','seal_width':370,'gap':85,'bilingual':True,'min_px':352,'min_mm':75,'use':'Covers · general brand signature'},
 {'id':'H-02','name':'Primary horizontal','mode':'horizontal','seal_height':426,'gap':85,'bilingual':True,'min_px':528,'min_mm':110,'use':'Wide mastheads · institutional headers'},
 {'id':'C-03','name':'Compact','mode':'horizontal','seal_height':260,'gap':56,'bilingual':True,'min_px':448,'min_mm':95,'use':'Tighter bilingual signatures · email'},
 {'id':'D-04','name':'Small-use / digital','mode':'horizontal','seal_height':220,'gap':56,'bilingual':False,'min_px':200,'min_mm':45,'use':'Mobile navigation · small Turkish signatures'},
 {'id':'F-05','name':'Formal bilingual','mode':'stacked','seal_width':500,'gap':140,'bilingual':True,'min_px':352,'min_mm':75,'use':'Certificates · ceremonial documents'},
]

def sha(data): return hashlib.sha256(data).hexdigest()
def xml(el): return ET.tostring(el,encoding='unicode')
def translate(s): return tuple(float(v) for v in re.search(r'translate\(([^)]+)\)',s).group(1).split(','))
def bounds(path):
    p=BoundsPen(None); x,y=translate(path.get('transform'))
    parse_path(path.get('d'),TransformPen(p,(1,0,0,1,x,y)))
    return list(p.bounds)
def union(boxes): return [min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
def shifted(b,x,y): return [b[0]+x,b[1]+y,b[2]+x,b[3]+y]

def inputs():
    assert sha(SEAL.read_bytes())==SHA,'Canonical seal checksum changed'
    root=ET.fromstring(SOURCE.read_bytes())
    paths=[copy.deepcopy(p) for p in root.iter(f'{{{NS}}}path') if p.get('data-glyph')]
    assert ''.join(p.get('data-glyph') for p in paths)=='ASYA’DAEĞİTİMEDUCATIONINASIA'
    return paths,ET.fromstring(SEAL.read_bytes())

def layout(v,paths):
    selected=paths if v['bilingual'] else paths[:13]
    body=union([bounds(p) for p in selected]); gap=v['gap']
    if v['mode']=='stacked':
        sw=v['seal_width']; sh=sw*370/400
        sx=(881-sw)/2; sy=0; tx=-42; ty=sh+gap-68
    else:
        sh=v['seal_height']; sw=sh*400/370
        sx=sy=0; tx=sw+gap-42
        # Keep the previous zero comparison baseline, not a selected optical nudge.
        ty=sh/2-(68+(495 if v['bilingual'] else 409))/2+(0.5 if v['bilingual'] else 0)
    all_ink=union([[sx,sy,sx+sw,sy+sh]]+[shifted(body,tx,ty+o) for o in OFFSETS.values()])
    frame=[all_ink[0]-70,all_ink[1]-70,all_ink[2]-all_ink[0]+140,all_ink[3]-all_ink[1]+140]
    return {**v,'seal_box':[sx,sy,sw,sh],'wordmark_translate':[tx,ty],
            'body_bounds':body,'frame':frame,'clearspace_native':70,
            'english_cap_at_min_px':35/frame[2]*v['min_px'] if v['bilingual'] else None,
            'turkish_cap_at_min_px':140/frame[2]*v['min_px'],
            'seal_height_at_min_px':sh/frame[2]*v['min_px'],
            'english_cap_at_min_mm':35/frame[2]*v['min_mm'] if v['bilingual'] else None}

def seal_element(source,box,tone,prefix):
    sx,sy,sw,sh=box
    # Nested original viewport retains canonical edge clipping. No edited paths.
    seal=copy.deepcopy(source)
    seal.set('x',str(sx)); seal.set('y',str(sy)); seal.set('width',str(sw));seal.set('height',str(sh));seal.set('overflow','hidden')
    seal.set('data-canonical-logo-sha256',SHA);seal.set('data-seal-tone',tone)
    if tone.startswith('mono'):
        original=[c for c in seal if c.tag!=f'{{{NS}}}title']
        for c in original: seal.remove(c)
        defs=ET.SubElement(seal,f'{{{NS}}}defs')
        mask=ET.SubElement(defs,f'{{{NS}}}mask',{'id':prefix+'-knockout','maskUnits':'userSpaceOnUse','x':'0','y':'0','width':'400','height':'370','style':'mask-type:luminance'})
        for c in original:
            c.set('fill','#FFFFFF' if c.tag==f'{{{NS}}}rect' else '#000000');mask.append(c)
        painting=copy.deepcopy(original[0]);painting.set('fill',TONES[tone]['type']);painting.set('mask',f'url(#{prefix}-knockout)');seal.append(painting)
    return seal

def asset(v,paths,seal,tone,offset,label):
    prefix=f'{v["id"]}-{tone}-{label}'
    frame=v['frame']; x,y,w,h=frame
    root=ET.Element(f'{{{NS}}}svg',{'viewBox':' '.join(f'{n:.8f}' for n in frame),'width':f'{w:.8f}','height':f'{h:.8f}','role':'img','aria-labelledby':prefix+'-title'})
    ET.SubElement(root,f'{{{NS}}}title',{'id':prefix+'-title'}).text=f"Asya’da Eğitim — {v['id']} {v['name']}; {tone}; vertical comparison offset {offset}; approval pending"
    ET.SubElement(root,f'{{{NS}}}metadata').text=json.dumps({'status':'HUMAN FINAL LOCKUP APPROVAL PENDING','canonical_logo_sha256':SHA,'source_wordmark_sha256':sha(SOURCE.read_bytes()),'tr_weight':550,'en_weight':350,'offset_native':offset,'alignment_approved':False})
    root.append(seal_element(seal,v['seal_box'],tone,prefix))
    tx,ty=v['wordmark_translate']
    group=ET.SubElement(root,f'{{{NS}}}g',{'data-wordmark':'selected-550-350','data-offset-native':str(offset),'transform':f'translate({tx:.8f},{ty+offset:.8f})'})
    for p in paths if v['bilingual'] else paths[:13]:
        p=copy.deepcopy(p);p.set('fill',TONES[tone]['accent'] if p.get('data-glyph')=='’' else TONES[tone]['type']);group.append(p)
    return xml(root)

def render(svg,width,background):
    with tempfile.TemporaryDirectory(prefix='lockup-proof-',dir=Path.home()/'.cache/brand-studio') as td:
        s=Path(td)/'proof.svg';p=Path(td)/'proof.png';s.write_text(svg)
        subprocess.run(['rsvg-convert','-w',str(width),str(s),'-o',str(p)],check=True,capture_output=True)
        im=Image.open(p).convert('RGBA'); bg=Image.new('RGBA',im.size,background);bg.alpha_composite(im)
        return bg.convert('RGB')

def inline(svg,prefix):
    # HTML SVG IDs are document-global; uniquify mask/title IDs, never geometry.
    ids=re.findall(r' id="([^"]+)"',svg)
    for old in ids:
        new=prefix+'-'+old
        svg=svg.replace(f'id="{old}"',f'id="{new}"').replace(f'url(#{old})',f'url(#{new})').replace(f'aria-labelledby="{old}"',f'aria-labelledby="{new}"')
    return svg

def inspection(vs):
    rows=[];minrows=[]
    for v in vs:
        row=Image.new('RGB',(1500,500),PAPER); draw=ImageDraw.Draw(row)
        draw.text((20,12),f'{v["id"]} — {v["name"]} / same TR550 EN350 paths / offset 0 is NOT selected',fill=INK)
        for j,tone in enumerate(['light','dark','mono-ink']):
            s=(RUN/'assets'/f'{v["id"]}-{tone}-0.svg').read_text(); image=render(s,460,TONES[tone]['background'])
            if image.height>450: image=image.resize((round(image.width*450/image.height),450),Image.Resampling.LANCZOS)
            row.paste(image,(j*500+20,40))
        rows.append(row)
        # Native 1x minimum: never enlarge the logo to claim small-size readability.
        native_height=round(v['min_px']*v['frame'][3]/v['frame'][2])+1
        cell_height=native_height+38
        row=Image.new('RGB',(1500,cell_height*2+30),PAPER);draw=ImageDraw.Draw(row)
        draw.text((20,10),f'{v["id"]} exact minimum-canvas width {v["min_px"]}px; each proof is 1 CSS px per raster px',fill=INK)
        for j,tone in enumerate(['light','dark','mono-ink','mono-paper']):
            image=render((RUN/'assets'/f'{v["id"]}-{tone}-0.svg').read_text(),v['min_px'],TONES[tone]['background'])
            # Two columns, two rows, preserve exact pixels.
            row.paste(image,((j%2)*750+20,(j//2)*cell_height+30))
        row.save(RUN/f'minimum-{v["id"]}.png')
        minrows.append(row)
    for name,data in [('family-inspection.png',rows),('minimum-inspection.png',minrows)]:
        out=Image.new('RGB',(1500,sum(r.height for r in data)),PAPER);y=0
        for r in data:out.paste(r,(0,y));y+=r.height
        out.save(RUN/name)
    icons=Image.new('RGB',(400,400),PAPER);draw=ImageDraw.Draw(icons)
    for j,tone in enumerate(TONES):
        draw.text((10,j*100+5),tone+' / exact seal-only at 32 / 48 / 64 px',fill=INK)
        x=12
        for w in [32,48,64]:
            image=render((RUN/'assets'/f'D-04-seal-only-{tone}.svg').read_text(),w,TONES[tone]['background'])
            icons.paste(image,(x,j*100+25));x+=w+30
    icons.save(RUN/'seal-only-minimum.png')

def build():
    (RUN/'assets').mkdir(parents=True,exist_ok=True);(DOC/'assets').mkdir(parents=True,exist_ok=True)
    paths,seal=inputs();vs=[layout(v,paths) for v in FAMILY]; outputs={}
    for v in vs:
        for tone in TONES:
            for label,offset in OFFSETS.items():
                name=f'{v["id"]}-{tone}-{label}.svg';s=asset(v,paths,seal,tone,offset,label)
                for directory in [RUN/'assets',DOC/'assets']:(directory/name).write_text(s)
                outputs[name]={'sha256':sha(s.encode()),'canonical_logo_sha256':SHA,'source_wordmark_sha256':sha(SOURCE.read_bytes()),'variant':v['id'],'tone':tone,'offset_native':offset,'approval':'pending'}
    # Below full-logo minimum: exact seal only, never redrawn simplified art.
    for tone in TONES:
        s=seal_element(seal,[40,40,400,370],tone,'digital-icon-'+tone)
        wrapper=ET.Element(f'{{{NS}}}svg',{'viewBox':'0 0 480 450','width':'480','height':'450','role':'img','aria-label':'Asya’da Eğitim exact seal only; small-use companion; approval pending'})
        wrapper.append(s);text=xml(wrapper);name=f'D-04-seal-only-{tone}.svg'
        for directory in [RUN/'assets',DOC/'assets']:(directory/name).write_text(text)
        outputs[name]={'sha256':sha(text.encode()),'canonical_logo_sha256':SHA,'variant':'D-04 companion','tone':tone,'approval':'pending'}
    manifest={'status':'HUMAN FINAL LOCKUP APPROVAL PENDING','typography_selected_by_human':{'turkish':'Jost 550','english':'Jost 350'},'alignment_selected':None,
        'canonical_logo_sha256':SHA,'source_wordmark_sha256':sha(SOURCE.read_bytes()),'source_wordmark_path':str(SOURCE.relative_to(ROOT)),
        'variants':vs,'offsets':OFFSETS,'tones':TONES,'outputs':outputs,'clearspace_native':70,'minimums':'Proposed pending visual approval; width includes SVG clearspace.',
        'wordmark_hash_method':'Ordered exact data-glyph/d/transform triples; no glyph regeneration.',
        'wordmark_geometry_sha256':sha(json.dumps([(p.get('data-glyph'),p.get('d'),p.get('transform')) for p in paths],ensure_ascii=False).encode()),
        'digital_exception':'D-04 carries the two unchanged Turkish rows only. English omitted explicitly for small-use, pending human confirmation.'}
    for directory in [RUN,DOC/'assets']:
        (directory/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    for name,original in [('selected-wordmark.svg',SOURCE),('canonical-seal.svg',SEAL)]:
        (DOC/'assets'/name).write_bytes(original.read_bytes())
    (DOC/'assets'/'lockup-spec.md').write_bytes((RUN/'lockup-spec.md').read_bytes())
    license_file=ROOT/'docs/asyada-seal/typography-weights/assets/OFL.txt'
    if license_file.exists():
        (DOC/'assets'/'OFL.txt').write_bytes(license_file.read_bytes())
        (RUN/'assets'/'OFL.txt').write_bytes(license_file.read_bytes())
    if (RUN/'visual-review.md').exists(): (DOC/'assets'/'visual-review.md').write_bytes((RUN/'visual-review.md').read_bytes())
    proofs=page(vs)
    for name,text in proofs.items():
        outputs[name]={'sha256':sha(text.encode()),'canonical_logo_sha256':SHA,'source_wordmark_sha256':sha(SOURCE.read_bytes()),'variant':name[:4]+' application','approval':'pending'}
    for directory in [RUN,DOC/'assets']:
        (directory/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    inspection(vs)
    print(json.dumps({'variants':[(v['id'],[round(n,2) for n in v['frame']],v['min_px'],round(v['english_cap_at_min_px'] or v['turkish_cap_at_min_px'],2)) for v in vs],'svg_assets':84,'application_proofs':len(proofs),'status':manifest['status']},indent=2))

def page(vs):
    parts=[HEADER]
    parts.append('<section class="family-intro"><div><p class="eyebrow">01 / ONE FAMILY, FIVE ROLES</p><h2>The arrangement changes.<br>The lettering never does.</h2></div><p>Jost 550 Turkish. Jost 350 English. The exact seal, the retained red apostrophe and the selected outline paths flow through every member. No new type design, no image generation.</p></section><div class="overview">')
    for v in vs:
        s=(RUN/'assets'/f'{v["id"]}-light-0.svg').read_text()
        parts.append(f'<a class="overview-card" href="#{v["id"]}"><span>{v["id"]}</span><div>{inline(s,"overview-"+v["id"])}</div><b>{v["name"]}</b></a>')
    parts.append('</div><aside class="notice"><b>Alignment remains open.</b> Zero is the existing comparison baseline—not a silently selected optical alignment. Inspect −4 / 0 / +4 / +8 side by side below. Each offset moves only the wordmark; the seal stays fixed.</aside>')
    for v in vs:
        i=v['id']; cap=v['english_cap_at_min_px']
        desc={'P-01':'A centered signature with the familiar seal-to-wordmark relationship. The measured three-line block stays intact beneath the crest.',
              'H-02':'The broad signature: a full-height seal beside the unified bilingual block. Use an expanded masthead rather than shrinking its English line into a thin navbar.',
              'C-03':'A tighter horizontal footprint with a smaller seal. Bilingual content is unchanged: compact placement, not condensed letters.',
              'D-04':'A purposeful small-use exception. Two unchanged Turkish rows; English omitted, never enlarged or re-tracked. Where English is mandatory, use C-03 at its larger minimum.',
              'F-05':'A ceremonial centered signature with a larger crest and greater vertical separation. The three text rows remain exactly the same as P/H/C.'}[i]
        parts.append(f'<section class="variant" id="{i}"><div class="variant-head"><div><p class="eyebrow">{i} / {v["use"]}</p><h2>{v["name"]}</h2><p>{desc}</p></div><div class="size-token"><b>{v["min_px"]}px</b><span>proposed minimum canvas width</span><b>{v["min_mm"]}mm</b><span>proposed print minimum</span></div></div><div class="usage-grid">')
        for tone,label in [('light','Light / full colour'),('dark','Dark / reversed lettering'),('mono-ink','Monochrome / ink')]:
            s=(RUN/'assets'/f'{i}-{tone}-0.svg').read_text()
            parts.append(f'<figure class="usage {tone}"><div class="mark-view">{inline(s,i+tone)}</div><figcaption>{label} · baseline 0 for comparison</figcaption></figure>')
        parts.append('</div><details class="mono-inverse"><summary>One-colour reverse / transparent seal cutouts</summary><figure class="usage mono-paper"><div class="mark-view">'+inline((RUN/'assets'/f'{i}-mono-paper-0.svg').read_text(),i+'inverse')+'</div><figcaption>Mono paper · same geometry, genuine transparent negative space</figcaption></figure></details>')
        parts.append(f'<div class="proof-heading"><h3>Read it at its proposed minimum.</h3><p>{"English cap ≈ "+str(round(cap,1))+"px." if cap else "Turkish cap ≈ "+str(round(v["turkish_cap_at_min_px"],1))+"px; no micro-English."} Rendered at actual CSS size, not fitted to the card. Scroll on a narrow screen; use 100% browser zoom.</p></div><div class="minimum-scroll"><div class="native-mark" style="width:{v["min_px"]}px" data-native-width="{v["min_px"]}">'+inline((RUN/'assets'/f'{i}-light-0.svg').read_text(),i+'minimum')+'</div></div>')
        parts.append(f'<details class="alignment-details"><summary>Compare all four relative alignments · no selection</summary><div class="align-grid">')
        for label,offset in OFFSETS.items():
            s=(RUN/'assets'/f'{i}-light-{label}.svg').read_text()
            parts.append(f'<figure><div class="alignment-mark">{inline(s,i+"align"+label)}</div><figcaption>{offset:+d} native units'+(' · prior comparison baseline' if offset==0 else '')+f'</figcaption><a href="assets/{i}-light-{label}.svg" target="_blank">Outlined SVG ↗</a></figure>')
        parts.append('</div><p class="caption">Same canvas, same seal position, same glyph paths. Positive values move the lettering down. Clearspace includes the furthest extent of all four alternatives.</p></details>')
        parts.append(f'<div class="downloads"><span>Review vectors / baseline 0:</span>'+''.join(f'<a href="assets/{i}-{t}-0.svg" target="_blank">{t} ↗</a>' for t in TONES)+'</div></section>')
    parts.append('<section id="applications"><p class="eyebrow">02 / ACTUAL-SIZE APPLICATION PROOFS</p><h2>Built to be used.<br>Not just viewed large.</h2><p>Flat HTML/SVG proofs, not image-generated mockups. Screen frames retain their exact pixel dimensions; print frames retain CSS millimeters. Horizontal scrolling is intentional. Physical dimensions are reliable when printed at actual size, not from a monitor ruler.</p>')
    def mark(i,tone='light',label='app'):
        return inline((RUN/'assets'/f'{i}-{tone}-0.svg').read_text(),label+i)
    parts.append('<h3>P-01 / A5 introduction cover · 148 × 210mm</h3><div class="application-scroll"><div class="a5 application"><div class="cover-mark" style="width:82mm">'+mark('P-01')+'</div><div class="cover-copy"><p class="eyebrow">STUDY IN ASIA</p><h4>Your next<br>chapter.</h4><p>A clear path from aspiration<br>to your university application.</p></div><span class="proof-label">REVIEW-ONLY COPY / 82mm LOGO</span></div></div>')
    parts.append('<h3>H-02 / desktop brand masthead · 1100 × 240px</h3><div class="application-scroll"><div class="masthead application"><div style="width:528px">'+mark('H-02')+'</div><div class="masthead-nav">Universities <span>How we help</span> <b>Start a conversation ↗</b></div></div></div>')
    parts.append('<h3>C-03 / email introduction masthead · 600 × 256px</h3><div class="application-scroll"><div class="email application"><div style="width:448px">'+mark('C-03')+'</div><span class="proof-label">YOUR UNIVERSITY JOURNEY / 448px LOGO</span></div></div>')
    parts.append('<h3>D-04 / mobile navigation · 375 × 112px</h3><div class="application-scroll"><div class="mobile application"><div style="width:200px">'+mark('D-04')+'</div><button aria-label="Menu" class="menu-button"><span></span><span></span></button></div></div><div class="icon-proof"><span class="eyebrow">BELOW FULL-LOGO MINIMUM / EXACT SEAL ONLY</span>')
    for w in [32,48,64]:
        parts.append(f'<figure><div style="width:{w}px">'+inline((RUN/'assets'/'D-04-seal-only-light.svg').read_text(),'icon'+str(w))+f'</div><figcaption>{w}px canvas</figcaption></figure>')
    parts.append('</div><p class="caption">32px is the proposed seal-only minimum; at 16px the fine internal detail is unreliable. No simplified or redrawn favicon is introduced.</p>')
    parts.append('<h3>F-05 / formal A4 landscape certificate · 297 × 210mm</h3><div class="application-scroll"><div class="certificate application"><div style="width:75mm;margin:auto">'+mark('F-05')+'</div><div class="certificate-copy"><p class="eyebrow">A NEW CHAPTER</p><h4>Certificate of participation</h4><p>Presented to <b>Student Name</b><br>for completing the university preparation programme.</p><div class="signatures"><span>Programme advisor</span><span>Date</span></div></div><span class="proof-label">ILLUSTRATIVE CONTENT / NOT AN ISSUED CERTIFICATE</span></div></div></section>')
    parts.append('<nav class="downloads" aria-label="Standalone application proofs"><span>Open exact-size HTML proofs:</span>'+''.join(f'<a href="assets/{v["id"]}-application.html" target="_blank">{v["id"]} ↗</a>' for v in vs)+'</nav>')
    parts.append('<section id="technical"><p class="eyebrow">03 / PRODUCTION EVIDENCE</p><h2>One outline source.<br>No hidden typography changes.</h2><div class="technical-grid"><div><h3>What remains identical</h3><ul><li>Exact selected glyph path data and translations.</li><li>Jost 550 / 350 and unchanged red punctuation in full colour.</li><li>881-unit shared measure and 140 / 139 / 35 cap rhythm.</li><li>Canonical seal geometry, 400:370 aspect and original edge clipping.</li><li>Four genuine relative alignment alternatives.</li></ul></div><div><h3>What is proposed</h3><ul><li>Seal scale, composition and gap for each role.</li><li>70-unit clearspace, outside all offset extremes.</li><li>Intended minimum sizes tested at native raster resolution.</li><li>D-04 Turkish-only / seal-only fallback.</li><li>Light/dark and approved monochrome colour variants.</li></ul></div></div><p class="caption">All monochrome seal features are transparent knockouts, not white paint baked onto a paper rectangle. All full-colour seal paths and fills come from the original canonical SVG. The selected typography retains its known differences from the original JPEG; this task does not redesign those letters.</p><aside class="notice"><b>Minimum-size caveat:</b> the 11.5–12.1px English caps are visibly readable in the native antialiased proofs, but light contours can break under a hard 50% alpha threshold on a 1× display. Component/counter diagnostics are published—not claimed as perfect 1× pixel topology. At 4× device resolution the same minimum-size outlines retain all counters. Do not disable antialiasing, shrink further or force bilingual lockups into a small navbar. On dark fields the unchanged red apostrophe has lower contrast (2.64:1); use mono paper when a high-contrast small signature is required.</aside><p><a href="assets/validation.json">Independent technical validation ↗</a> · <a href="assets/manifest.json">Output/source hashes and construction manifest ↗</a> · <a href="assets/lockup-spec.md">Draft lockup specification ↗</a> · <a href="../typography-weights/">Preserved typography & alignment study ↗</a></p><div class="status"><span>HUMAN FINAL LOCKUP APPROVAL PENDING</span><b>No lockups or alignment canonicalized.</b></div><p class="caption">Seal SHA-256: <code>'+SHA+'</code></p></section><footer>Asya’da Eğitim / five-member lockup family / human approval review.</footer></main></body></html>')
    text=''.join(parts)
    (DOC/'index.html').write_text(text);(RUN/'review.html').write_text(text)
    # Same DOM and CSS as the review, isolated for actual-size export/inspection.
    capture=ApplicationCapture();capture.feed(text)
    assert len(capture.items)==5
    style=re.search(r'<style>(.*?)</style>',text,re.S).group(1)
    proofs={}
    for v,body in zip(vs,capture.items):
        proof=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{v["id"]} actual-size application proof</title><meta name="canonical_logo_sha256" content="{SHA}"><style>{style}\nbody{{margin:0}}.application{{box-shadow:none}}</style></head><body>{body}</body></html>'
        name=v['id']+'-application.html';proofs[name]=proof
        (DOC/'assets'/name).write_text(proof)
        (RUN/'applications').mkdir(exist_ok=True);(RUN/'applications'/name).write_text(proof)
    return proofs

class ApplicationCapture(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=False);self.items=[];self.depth=0;self.chunks=[]
    def handle_starttag(self,tag,attrs):
        classes=dict(attrs).get('class','').split()
        if not self.depth and tag=='div' and 'application' in classes:self.depth=1;self.chunks=[self.get_starttag_text()];return
        if self.depth:
            self.chunks.append(self.get_starttag_text())
            if tag=='div':self.depth+=1
    def handle_endtag(self,tag):
        if self.depth:
            self.chunks.append(f'</{tag}>')
            if tag=='div':
                self.depth-=1
                if not self.depth:self.items.append(''.join(self.chunks));self.chunks=[]
    def handle_startendtag(self,tag,attrs):
        if self.depth:self.chunks.append(self.get_starttag_text())
    def handle_data(self,data):
        if self.depth:self.chunks.append(data)
    def handle_entityref(self,name):
        if self.depth:self.chunks.append('&'+name+';')
    def handle_charref(self,name):
        if self.depth:self.chunks.append('&#'+name+';')

HEADER='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Asya’da Eğitim — Final lockup family review</title><style>
:root{--ink:#1D2027;--paper:#F7F3E9;--red:#BD2120;--line:#d9d4c8;--muted:#65625a}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}main{max-width:1240px;margin:auto;padding:48px 32px 96px}a{color:inherit;text-underline-offset:4px}button{font:inherit}p{max-width:70ch}h1,h2,h3,h4{margin:0;font-weight:550}h1{font-size:clamp(44px,7vw,84px);line-height:1.03;letter-spacing:-.055em;text-wrap:balance;max-width:14ch}h2{font-size:clamp(28px,4vw,44px);line-height:1.13;letter-spacing:-.035em;text-wrap:balance}h3{font-size:20px;letter-spacing:-.015em}.eyebrow{font:11px/1.45 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}.header-top{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:72px}.header-top a{font-size:13px}.hero{display:grid;grid-template-columns:1.25fr 1fr;gap:60px;align-items:end}.hero p{margin:0}.status{border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:16px 0;margin:36px 0;display:flex;gap:20px;justify-content:space-between;flex-wrap:wrap;font-size:12px}.status span{font:11px ui-monospace,monospace;letter-spacing:.05em;color:var(--red)}.status b{font-weight:500}.family-intro,.variant-head{display:grid;grid-template-columns:1.4fr 1fr;gap:50px;align-items:start;margin:64px 0 30px}.family-intro p{margin-top:20px}.overview{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}.overview-card{display:flex;flex-direction:column;text-decoration:none;background:#eee9dd;border:1px solid var(--line);padding:16px 12px;min-width:0}.overview-card span{font:12px ui-monospace,monospace}.overview-card div{height:180px;display:grid;place-items:center}.overview-card svg{width:100%;height:100%;max-height:170px}.overview-card b{font-size:12px;font-weight:500;margin-top:12px}.notice{font-size:14px;max-width:90ch;border-left:3px solid var(--red);padding:4px 0 4px 20px;margin:36px 0 64px}.variant{border-top:1px solid var(--ink);padding-top:34px;margin-top:64px;scroll-margin-top:30px}.variant-head{margin:0 0 26px}.variant-head p{font-size:15px}.size-token{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;max-width:360px;margin-left:auto;border-left:1px solid var(--line);padding-left:20px}.size-token b{font-size:26px;letter-spacing:-.025em}.size-token span{font-size:12px;color:var(--muted);align-self:center}.usage-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.usage{margin:0;border:1px solid var(--line);padding:22px 14px 12px}.usage.dark,.usage.mono-paper{background:var(--ink);color:var(--paper);border-color:var(--ink)}.mark-view{height:300px;display:grid;place-items:center}.mark-view svg{width:100%;height:100%;max-height:280px}figcaption,.caption{font-size:12px;color:var(--muted)}.dark figcaption,.mono-paper figcaption{color:#cfc8b9}.mono-inverse{margin-top:14px}.mono-inverse .usage{max-width:400px}summary{cursor:pointer;min-height:44px;padding:10px 0;font-size:14px}svg{display:block;width:100%;height:auto}.proof-heading{margin-top:34px;display:flex;gap:32px;justify-content:space-between;align-items:start}.proof-heading p{font-size:13px;margin:0;max-width:50ch}.minimum-scroll,.application-scroll{overflow-x:auto;max-width:100%;margin:16px 0 24px;border:1px solid var(--line);padding:18px}.native-mark{flex:none}.align-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.align-grid figure{margin:0;background:#eee9dd;padding:12px}.alignment-mark{height:200px;display:grid;place-items:center}.alignment-mark svg{height:100%;max-height:200px;width:100%}.align-grid a{font-size:12px}.downloads{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;margin-top:22px}.downloads span{color:var(--muted)}#applications,#technical{margin-top:80px;padding-top:36px;border-top:1px solid var(--ink)}#applications h3{margin-top:38px}.application-scroll{padding:24px;background:#e8e3d7}.application{flex:none;background:var(--paper);color:var(--ink);position:relative;box-shadow:0 1px 5px #00000015}.application h4{font-size:36px;line-height:1.05;letter-spacing:-.035em}.application p{font-size:14px}.a5{width:148mm;height:210mm;padding:25mm 18mm}.cover-mark{margin:auto}.cover-copy{margin-top:12mm}.cover-copy h4{font-size:52px}.cover-copy p:last-child{line-height:1.6}.proof-label{position:absolute;bottom:16px;left:24px;font:9px ui-monospace,monospace;letter-spacing:.05em;color:var(--muted)}.masthead{width:1100px;height:240px;display:flex;align-items:center;justify-content:space-between;padding:16px 32px}.masthead-nav{display:flex;gap:26px;align-items:center;font-size:13px}.masthead-nav b{font-weight:500;color:var(--red)}.email{width:600px;height:256px;padding:20px 24px}.email .proof-label{bottom:14px}.mobile{width:375px;height:112px;display:flex;justify-content:space-between;align-items:center;padding:16px 24px}.menu-button{border:0;background:transparent;width:44px;height:44px;padding:12px;display:grid;align-content:center;gap:6px}.menu-button span{height:2px;width:20px;background:var(--ink);display:block}.icon-proof{display:flex;align-items:center;gap:30px;flex-wrap:wrap;margin:24px 0}.icon-proof figure{margin:0}.certificate{width:297mm;height:210mm;padding:15mm 20mm;text-align:center}.certificate:before{content:'';position:absolute;inset:8mm;border:1px solid var(--line);pointer-events:none}.certificate-copy{margin-top:7mm}.certificate-copy h4{font-size:34px;font-weight:400}.certificate-copy p{margin:14px auto}.signatures{margin:12mm auto 0;max-width:185mm;display:flex;justify-content:space-between;font-size:11px}.signatures span{border-top:1px solid var(--line);padding-top:8px;width:65mm}.technical-grid{display:grid;grid-template-columns:1fr 1fr;gap:50px;margin-top:32px}.technical-grid li{font-size:14px;margin:8px 0}code{overflow-wrap:anywhere}footer{margin-top:60px;font:11px ui-monospace,monospace;color:var(--muted)}@media(max-width:850px){.overview{grid-template-columns:repeat(3,minmax(0,1fr))}.hero{grid-template-columns:1fr;gap:28px}.header-top{margin-bottom:42px}.usage-grid{grid-template-columns:1fr}.usage .mark-view{height:260px}.family-intro,.variant-head{grid-template-columns:1fr;gap:22px}.size-token{margin-left:0}.align-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.proof-heading{display:block}.proof-heading p{margin-top:12px}}@media(max-width:500px){main{padding:28px 16px 64px}.overview{grid-template-columns:repeat(2,minmax(0,1fr))}.overview-card div{height:150px}.technical-grid{grid-template-columns:1fr;gap:24px}.minimum-scroll,.application-scroll{padding:12px}.status{display:block}.status b{display:block;margin-top:8px}.align-grid{grid-template-columns:1fr}.alignment-mark{height:240px}.size-token b{font-size:24px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}@media print{main{max-width:none}.application-scroll{overflow:visible;border:0;padding:0;background:none}.application{box-shadow:none}.usage-grid,.overview,.alignment-details,.downloads{break-inside:avoid}.application{break-inside:avoid}.header-top,.notice{display:none}}
</style></head><body><main><header><div class="header-top"><span class="eyebrow">ASYA’DA EĞİTİM / IDENTITY REVIEW</span><a href="../">Back to the seal gallery ↗</a></div><div class="hero"><h1>Five forms.<br>One signature.</h1><p>The selected typography direction becomes a coherent lockup family. Five outlined arrangements, reviewed in light, dark and monochrome—and in the sizes where they need to work.</p></div><div class="status"><span>HUMAN FINAL LOCKUP APPROVAL PENDING</span><b>Jost 550 / 350 selected · lockups and alignment not approved</b></div></header>'''

if __name__=='__main__':build()

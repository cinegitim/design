#!/usr/bin/env python3
"""Phase-local deterministic editable HTML reconstruction. No image-model calls."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json, shutil, hashlib, subprocess, tempfile, os, signal, html, concurrent.futures, zipfile, sys

ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
DOC=ROOT/'docs/instagram/phase-2b'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CONTENT=json.loads((BASE/'content.json').read_text())
LOCK=json.loads((ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
RECORDS={r['canonical_lockup_id']:r for r in LOCK['records']}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def esc(s):return html.escape(str(s)).replace('\n','<br>')
def box(x,y,w,text,size=40,weight=400,color='var(--ink)',extra=''):
    return f'<div class="txt" style="left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;font-weight:{weight};color:{color};{extra}">{esc(text)}</div>'
def rect(x,y,w,h,c):return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{c}"></div>'
def photo(name,x,y,w,h,pos='center'):
    return f'<img class="photo" src="assets/{name}.jpg" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;object-position:{pos}" alt="Yapay zekâ illüstrasyonu">'
def line(x,y,w,c='var(--red)'):return rect(x,y,w,3,c)
def svgpath(d,c='var(--red)',width=4):return f'<svg class="device" width="1080" height="1080" viewBox="0 0 1080 1080"><path d="{d}" fill="none" stroke="{c}" stroke-width="{width}"/></svg>'

CSS='''@font-face{font-family:Jost;src:url(assets/Jost-VF.ttf);font-weight:100 900}*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#F7F3E9}body{--ink:#1D2027;--paper:#F7F3E9;--red:#BD2120;font-family:Jost,sans-serif}.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:var(--paper)}.txt{position:absolute;line-height:1.17;letter-spacing:-.015em;white-space:normal}.photo{position:absolute;object-fit:cover;display:block}.device{position:absolute;left:0;top:0;pointer-events:none}.logo{position:absolute}.logo svg{width:100%;height:auto;display:block}.serif{font-family:Georgia,serif}'''

def layout(s,c,i):
    typ=s['layout'];title=s['title'];body=s.get('body','');note=s.get('note','');img=s.get('image','').removesuffix('.png')
    top=box(64,42,860,f'{c["id"][0].upper()} / '+c['title'],24,500)
    p=[]
    if typ=='cover-a':
        p=[box(54,88,980,title,330,800,'var(--red)',extra='line-height:.8;letter-spacing:-.06em'),photo(img,344,395,672,624),box(64,395,275,s['subtitle'],50,600),rect(64,570,5,292,'var(--red)'),box(84,904,240,body,33,500)]
    elif typ=='cover-b':
        p=[line(64,113,952),box(64,128,952,title,126,400,extra='font-family:Georgia;letter-spacing:-.06em'),box(64,270,952,'28',525,400,'var(--red)',extra='font-family:Georgia;line-height:1'),line(64,803,952),box(64,832,952,s['subtitle'],85,400,extra='font-family:Georgia'),box(64,957,920,body,34,500),box(690,274,326,'17.00 JST',32,600)]
        p += [rect(64+j*40,244,2,14+(j%5==0)*14,'var(--ink)') for j in range(24)]
        p += [box(736,515,280,'SON TARİH',26,600,'var(--red)'),box(736,570,280,'28 OCAK\n17.00 JST',35,500)]
    elif typ=='cover-c':
        p=[photo(img,0,0,1080,1050),rect(0,0,1080,390,'var(--ink)'),box(54,118,980,title,236,800,'var(--paper)',extra='letter-spacing:-.06em;line-height:.95'),rect(64,360,454,58,'var(--red)'),box(84,369,420,s['subtitle'],30,600,'var(--paper)'),rect(64,874,760,144,'var(--ink)'),box(88,897,712,body,34,400,'var(--paper)'),svgpath('M 70 460 H 370 Q 430 460 430 520 V 600 Q 430 650 510 650 H 900','var(--paper)',4)]
        top=box(64,42,880,'C / TOKYO · ŞEHİR REHBERİ',24,500,'var(--paper)')
    elif typ=='cover-d':
        p=[box(64,92,430,'6',580,400,extra='font-family:Georgia;line-height:1'),box(510,212,510,s['subtitle'],86,400,extra='font-family:Georgia'),svgpath('M 970 92 C 860 210 1020 410 850 530 S 640 670 490 760 S 200 850 108 940'),box(510,920,506,body,35,500),box(64,1030,952,note,25)]
        for j,(x,y) in enumerate([(922,380),(862,530),(672,650),(490,760),(290,850),(110,940)]):p += [box(x-20,y-20,70,str(j+1),40,600,'var(--red)')]
    elif typ=='rank':
        p=[box(64,128,952,s['subtitle'],60,500),box(44,315,990,title,510,800,'var(--red)',extra='line-height:1;letter-spacing:-.07em'),line(64,897,952),box(64,929,930,body,39,500)]
    elif typ=='collage':
        p=[box(64,112,952,title,88,600),photo(img,342,342,674,470,'center 32%'),rect(64,360,4,413,'var(--red)'),box(90,833,886,body,40),box(64,1014,940,note,28,500)]
    elif typ=='photo-top':
        p=[photo(img,0,104,1080,535,'center 60%'),rect(64,548,952,147,'var(--paper)'),box(86,567,910,title,65,600),box(64,749,952,body,41)]
        if note:p += [box(64,989,952,note,28,500)]
    elif typ=='photo-side':
        p=[photo(img,615,116,465,890,'center'),box(64,140,540,title,64,600),line(64,351,500),box(64,405,490,body,36)]
        if note:p += [box(64,951,520,note,27,500)]
    elif typ=='summary':
        p=[box(64,116,952,title,80,600)]
        for j,t in enumerate(s['items']):
            yy=390+j*180;p += [box(64,yy-22,125,f'0{j+1}',92,400,'var(--red)',extra='font-family:Georgia'),box(222,yy,774,t,40,500),line(222,yy+132,794,'#d2c9b5')]
        p += [box(222,994,794,body,30,500)]
    elif typ=='window':
        p=[box(64,125,952,title,190,400,'var(--red)',extra='font-family:Georgia'),box(64,363,952,s['subtitle'],82,400,extra='font-family:Georgia'),line(64,508,952),box(64,581,952,body,47,500,extra='line-height:1.65'),box(64,949,930,note,30)]
    elif typ in ('dossier','timeline'):
        p=[box(64,123,952,title,84,500,extra='font-family:Georgia' if typ=='timeline' else '')]
        for j,t in enumerate(s['items']):
            yy=391+j*174
            if typ=='timeline':
                dt,desc=t.split(' · ',1)
                p += [rect(70,yy+8,3,165,'var(--red)'),box(102,yy,914,dt,43,500,'var(--red)',extra='font-family:Georgia'),box(102,yy+70,914,desc,36,500)]
            else:p += [rect(70,yy+8,12,90,'var(--red)'),box(112,yy,900,t,40,500),line(112,yy+129,904,'#d2c9b5')]
        p += [box(112,964,904,body,30)]
    elif typ=='rail':
        p=[rect(0,100,1080,980,'var(--ink)'),box(64,144,952,title,84,600,'var(--paper)'),svgpath('M 80 420 H 400 Q 500 420 500 520 V 590 Q 500 650 600 650 H 940','var(--paper)',5),box(64,737,952,body,41,400,'var(--paper)'),box(64,976,952,note,28,500,'var(--paper)')]
        for x,y,label in [(80,420,'EV'),(500,550,'AKTARMA'),(940,650,'KAMPÜS')]:p += [rect(x-7,y-7,14,14,'var(--red)'),box(max(64,x-85),y+26,190,label,24,500,'var(--paper)')]
    elif typ=='housing':
        p=[box(64,125,952,title,84,600),photo(img,64,363,420,479),box(530,381,486,body,38),line(64,900,952),box(64,942,952,note,33,500)]
    elif typ=='step-photo':
        p=[photo(img,448,105,632,516),box(64,123,390,s['step'],172,400,'var(--red)',extra='font-family:Georgia'),box(64,656,952,title,90,600),line(64,903,952),box(64,935,952,body,36)]
    elif typ=='step-type':
        p=[box(52,96,970,s['step'],272,400,'var(--red)',extra='font-family:Georgia;line-height:1'),svgpath('M 968 152 C 880 292 970 393 802 464 H 64'),box(64,466,952,title,100,600),box(64,756,952,body,40),box(64,997,952,note,28,500)]
    elif typ=='cta':
        p=[rect(64,151,9,254,'var(--red)'),box(108,144,906,title,83,600),line(108,416,908),box(108,486,856,body,43),box(108,869,856,note,29,500)]
        if c['id'].startswith('d'):p += [box(900,960,116,'→',80,500,'var(--red)')]
    else:raise ValueError(typ)
    # Every final artifact includes exact COMPLETE approved SVG, never pieces.
    full=typ.startswith('cover') or typ=='cta'; lid='H-02/light' if full else 'D-04/light'
    rec=RECORDS[lid];raw=(ROOT/rec['canonical_file_path']).read_text()
    footer=rect(0,1080,1080,270,'var(--paper)')+line(64,1080,952,'#d2c9b5')
    if img:footer += box(64,1091,952,'Yapay zekâ illüstrasyonu · Gerçek kampüs / öğrenci fotoğrafı değil',22,400)
    footer+=f'<div class="logo" data-canonical-id="{lid}" style="left:64px;top:{1120 if full else 1190}px;width:{600 if full else 320}px">{raw}</div>'
    footer+=box(724,1154,292,f'{i+1:02d} / {len(c["slides"]):02d}',30,500)
    footer+=box(724,1210,292,'Kaynak: '+', '.join(s['sources']),22)
    footer+=box(724,1270,292,'Kontrol · 08.10.2026',22)
    return top+''.join(p)+footer,lid

def export(task):
    src,out=task
    with tempfile.TemporaryDirectory(prefix='phase2b-',dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as profile:
        args=[CHROME,'--headless','--disable-gpu','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--no-first-run','--no-default-browser-check','--hide-scrollbars','--force-device-scale-factor=1',f'--user-data-dir={profile}','--window-size=1080,1350','--virtual-time-budget=2500',f'--screenshot={out}',src.as_uri()]
        p=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        try:p.wait(timeout=22)
        except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=5)
    assert out.exists(),out
    assert Image.open(out).size==(1080,1350),out
    return out

def main():
    subprocess.run(['python3',str(ROOT/'studio/tools/verify_asyada_canonical_lockups.py')],check=True,stdout=subprocess.DEVNULL)
    DOC.mkdir(parents=True,exist_ok=True)
    tasks=[];manifest={'status':CONTENT['status'],'checked_on':CONTENT['checked_on'],'successful_chatgpt_image_generations':37,'original_explorations':27,'corrective_generations':6,'complete_composition_generations':4,'backend':'gpt-image-2 via connected ChatGPT subscription','dimensions':[1080,1350],'canonical_seal_sha256':LOCK['canonical_seal_sha256'],'carousels':[]}
    for c in CONTENT['carousels']:
        dst=DOC/c['id'];assets=dst/'editable/assets';assets.mkdir(parents=True,exist_ok=True);(dst/'png').mkdir(exist_ok=True)
        shutil.copy2(ROOT/'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf',assets/'Jost-VF.ttf')
        for lid in ['H-02/light','D-04/light']:
            r=RECORDS[lid];shutil.copy2(ROOT/r['canonical_file_path'],assets/Path(r['canonical_file_path']).name)
        for s in c['slides']:
            if s.get('image'):
                n=s['image'];p=BASE/n if n.endswith('.png') else next((BASE/n).glob('*.png'))
                im=Image.open(p).convert('RGB');im.save(assets/(n.removesuffix('.png')+'.jpg'),quality=93)
        cm={'id':c['id'],'title':c['title'],'character':c['character'],'slides':[]}
        for i,s in enumerate(c['slides']):
            art,lid=layout(s,c,i);f=dst/'editable'/f'{i+1:02d}.html';out=dst/'png'/f'{i+1:02d}.png'
            f.write_text(f'<!doctype html><html lang="tr"><meta charset="utf-8"><title>{esc(c["title"])} / {i+1}</title><style>{CSS}</style><body><main class="slide">{art}</main></body></html>')
            r=RECORDS[lid];cm['slides'].append({'index':i+1,'file':f'{c["id"]}/png/{i+1:02d}.png','editable':f'{c["id"]}/editable/{i+1:02d}.html','layout':s['layout'],'canonical_lockup_id':lid,'canonical_lockup_sha256':r['sha256'],'canonical_seal_sha256':LOCK['canonical_seal_sha256'],'lockup_width_px':600 if lid.startswith('H') else 320,'sources':s['sources'],'ai_imagery':bool(s.get('image'))})
            tasks.append((f,out))
        manifest['carousels'].append(cm)
        (dst/'content-and-sources.json').write_text(json.dumps({'checked_on':CONTENT['checked_on'],'sources':CONTENT['sources'],'carousel':c},ensure_ascii=False,indent=2))
        shutil.copy2(BASE/'production-notes.md',dst/'production-notes.md');shutil.copy2(Path(__file__),dst/'build-workspace-reference.py')
    if '--package-only' not in sys.argv:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for p in pool.map(export,tasks):print(p.relative_to(DOC),flush=True)
    else:
        for _,out in tasks:assert out.exists() and Image.open(out).size==(1080,1350)
    covers=[]
    for c in manifest['carousels']:
        dst=DOC/c['id'];N=len(c['slides']);sheet=Image.new('RGB',(min(N,4)*270,((N+3)//4)*374),'#F7F3E9');d=ImageDraw.Draw(sheet)
        for i,s in enumerate(c['slides']):
            p=DOC/s['file'];s['sha256']=sha(p);im=Image.open(p);im.thumbnail((262,328));x=i%4*270+4;y=i//4*374+30;sheet.paste(im,(x,y));d.text((x,y-22),f'{i+1:02d} / {N:02d}',fill='#1D2027')
        sheet.save(dst/'contact-sheet.jpg',quality=95);covers.append(Image.open(dst/'png/01.png'))
        (dst/'manifest.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
        for supporting in ['export-editable.py','quality-review.md']:
            if (DOC/supporting).exists():shutil.copy2(DOC/supporting,dst/supporting)
        with zipfile.ZipFile(DOC/(c['id']+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(dst.rglob('*')):
                if p.is_file():z.write(p,Path(c['id'])/p.relative_to(dst))
    grid=Image.new('RGB',(1080,1350),'#F7F3E9')
    for i,im in enumerate(covers):im=im.resize((540,675),Image.Resampling.LANCZOS);grid.paste(im,(i%2*540,i//2*675))
    grid.save(DOC/'four-covers.jpg',quality=95)
    manifest['derived_outputs']=[{'file':p.relative_to(DOC).as_posix(),'sha256':sha(p),'canonical_lockup_ids':['H-02/light','D-04/light'],'canonical_lockup_sha256':{lid:RECORDS[lid]['sha256'] for lid in ['H-02/light','D-04/light']},'canonical_seal_sha256':LOCK['canonical_seal_sha256'],'derivation':'Exact final slide pixels or packaged editable sources'} for p in [DOC/'four-covers.jpg',*[DOC/(c['id']+'.zip') for c in manifest['carousels']],*[DOC/c['id']/'contact-sheet.jpg' for c in manifest['carousels']]]]
    manifest['image_generation_archive']=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'actual_size':list(Image.open(p).size),'backend':'gpt-image-2 via connected ChatGPT subscription','final_artwork':False} for p in sorted(BASE.rglob('*.png'))]
    assert len(manifest['image_generation_archive'])==37
    (DOC/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    shutil.copy2(BASE/'content.json',DOC/'content.json');shutil.copy2(BASE/'production-notes.md',DOC/'production-notes.md')
    print('COMPLETE: 4 carousels / 28 branded 1080×1350 PNG / 4 ZIP',flush=True)

if __name__=='__main__':main()

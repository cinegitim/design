#!/usr/bin/env python3
"""Build Phase 2C separately; Phase 2B remains an immutable factual source."""
from pathlib import Path
from PIL import Image
import concurrent.futures, hashlib, html, json, os, shutil, signal, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / 'brands/asyada-egitim/applications/instagram-phase-2b'
DOC = ROOT / 'docs/instagram/phase-2c'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CONTENT = json.loads((SOURCE / 'content.json').read_text())
LOCK = json.loads((ROOT / 'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
RECORDS = {r['canonical_lockup_id']: r for r in LOCK['records']}
PAPER, INK, RED = '#F7F3E9', '#1D2027', '#BD2120'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def esc(value):
    return html.escape(str(value)).replace('\n', '<br>')

def image_name(slide, carousel, index):
    """Pick genuinely photographic Phase 2B generated illustrations for collages."""
    name = slide.get('image')
    if name:
        p = SOURCE / (name if name.endswith('.png') else name)
        if p.is_dir():
            p = next(p.glob('*.png'))
        if p.exists():
            return p.name
    candidates = [s.get('image') for s in carousel['slides'] if s.get('image')]
    for candidate in candidates:
        p = SOURCE / candidate
        if p.is_dir():
            p = next(p.glob('*.png'))
        if p.exists():
            return p.name
    return None

def art(slide, carousel, index, n, lockup):
    title, body = slide['title'], slide.get('body', '')
    images = [s.get('image') for s in carousel['slides'] if s.get('image')]
    paths = []
    for candidate in images:
        p = SOURCE / candidate
        if p.is_dir(): p = next(p.glob('*.png'))
        if p.exists() and p not in paths: paths.append(p)
    if len(paths) < 2:
        for other in CONTENT['carousels']:
            for item in other['slides']:
                candidate = item.get('image')
                if not candidate: continue
                p = SOURCE / candidate
                if p.is_dir(): p = next(p.glob('*.png'))
                if p.exists() and p not in paths: paths.append(p)
    if not paths: paths = [SOURCE / 'a1-cover.png']
    p1, p2 = paths[index % len(paths)], paths[(index + 1) % len(paths)]
    im1, im2 = p1.name, p2.name
    note = slide.get('note', '')
    srcs = ' · '.join(slide.get('sources', []))
    kind = slide['layout'].replace('-', ' ').upper()
    # Alternate compositions to make the series feel authored, not stamped.
    mode = index % 4
    if mode == 0:
        collage = f'<img class="hero" src="assets/{im1}"><img class="inset" src="assets/{im2}">'
        text = f'<div class="copy light"><div class="eyebrow">{esc(kind)}　/　{esc(srcs)}</div><h1>{esc(title)}</h1><p>{esc(body)}</p></div>'
    elif mode == 1:
        collage = f'<img class="hero tall" src="assets/{im1}"><img class="inset lower" src="assets/{im2}">'
        text = f'<div class="copy side"><div class="eyebrow">{esc(kind)}　/　{esc(srcs)}</div><h1>{esc(title)}</h1><p>{esc(body)}</p></div>'
    elif mode == 2:
        collage = f'<img class="tile left" src="assets/{im1}"><img class="tile right" src="assets/{im2}">'
        text = f'<div class="copy split"><div class="eyebrow">{esc(kind)}　/　{esc(srcs)}</div><h1>{esc(title)}</h1><p>{esc(body)}</p></div>'
    else:
        collage = f'<img class="hero" src="assets/{im2}"><img class="inset inset-left" src="assets/{im1}">'
        text = f'<div class="copy light low"><div class="eyebrow">{esc(kind)}　/　{esc(srcs)}</div><h1>{esc(title)}</h1><p>{esc(body)}</p></div>'
    # D-04 is the only approved lockup small enough for these interiors (>=200px).
    # Keep it on clear paper and vary alignment/vertical placement rather than inventing a
    # new signature or repeating a single bottom-left footer.
    logo_pos = [
        'left:64px;top:1080px;width:236px',
        'right:62px;top:1080px;width:236px',
        'left:62px;top:1090px;width:236px',
        'right:64px;top:1090px;width:236px',
    ][mode]
    logo = (ROOT / RECORDS[lockup]['canonical_file_path']).read_text()
    disclosure = '<span>Yapay zekâ illüstrasyonu · Gerçek kampüs/öğrenci fotoğrafı değildir</span>'
    note_html = f'<div class="note">{esc(note)}</div>' if note else ''
    text = text.replace('</p></div>', f'</p>{note_html}</div>')
    return f'''<!doctype html><html lang="tr"><meta charset="utf-8"><title>{esc(carousel['title'])} / {index+1:02d}</title>
<style>
@font-face{{font-family:Jost;src:url(assets/Jost-VF.ttf);font-weight:100 900}}*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:{PAPER};font-family:Jost,Arial,sans-serif;color:{INK}}}
.slide{{position:relative;width:1080px;height:1350px;overflow:hidden;background:{PAPER}}}.hero{{position:absolute;left:0;top:0;width:1080px;height:740px;object-fit:cover}}.hero.tall{{height:940px;width:660px;left:420px}}.inset{{position:absolute;right:62px;top:420px;width:390px;height:350px;object-fit:cover;border:12px solid {PAPER};box-shadow:0 18px 50px #17171733}}.inset.lower{{top:680px;right:46px;width:310px;height:360px}}.inset-left{{left:38px;right:auto;top:570px;width:320px;height:280px}}.tile{{position:absolute;top:0;width:53%;height:650px;object-fit:cover}}.tile.left{{left:0;clip-path:polygon(0 0,100% 0,80% 100%,0 100%)}}.tile.right{{right:0;top:100px;height:590px;clip-path:polygon(20% 0,100% 0,100% 100%,0 100%)}}
.copy{{position:absolute;z-index:2;padding:38px 48px;background:{PAPER};box-shadow:0 18px 45px #17171716}}.copy.light{{left:54px;top:630px;width:720px}}.copy.side{{left:52px;top:140px;width:440px}}.copy.split{{left:70px;top:590px;width:800px}}.copy.low{{top:570px}}.eyebrow{{font-size:22px;letter-spacing:.12em;text-transform:uppercase;color:{RED};font-weight:700}}h1{{font-size:70px;line-height:.99;letter-spacing:-.045em;margin:20px 0 24px;font-weight:650}}p{{font-size:31px;line-height:1.28;margin:0;max-width:890px}}.note{{position:static;font-size:20px;line-height:1.25;border-left:4px solid {RED};padding:10px 14px;margin-top:20px}}.meta{{position:absolute;left:64px;right:64px;bottom:88px;border-top:1px solid #c9c0ad;padding-top:14px;font-size:20px;display:flex;justify-content:space-between}}.logo{{position:absolute;z-index:4}}.logo svg{{display:block;width:100%;height:auto}}.disclosure{{position:absolute;right:60px;bottom:22px;font-size:17px;text-align:right;max-width:500px;color:#504d47}}
</style><body><main class="slide">{collage}{text}<div class="meta"><b>{esc(carousel['title'])}</b><span>{index+1:02d} / {n:02d}</span></div><div class="logo" data-canonical-id="{lockup}" style="{logo_pos}">{logo}</div><div class="disclosure">{disclosure}</div></main></body></html>''', [p1,p2]

def export(task):
    src, out = task
    with tempfile.TemporaryDirectory(prefix='phase2c-', dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as profile:
        args = [CHROME,'--headless','--disable-gpu','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--no-first-run','--no-default-browser-check','--hide-scrollbars','--force-device-scale-factor=1',f'--user-data-dir={profile}','--window-size=1080,1350','--virtual-time-budget=2500',f'--screenshot={out}',src.as_uri()]
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try: proc.wait(timeout=25)
        except subprocess.TimeoutExpired: os.killpg(proc.pid, signal.SIGTERM); proc.wait(timeout=5)
    if not out.exists() or Image.open(out).size != (1080,1350): raise RuntimeError(f'Bad export: {out}')
    return out

def main():
    subprocess.run(['python3',str(ROOT/'studio/tools/verify_asyada_canonical_lockups.py')],check=True,stdout=subprocess.DEVNULL)
    DOC.mkdir(parents=True,exist_ok=True)
    manifest={'phase':'2C','status':'HUMAN FULL-CAROUSEL APPROVAL PENDING','factual_base':'Phase 2B content.json copied unchanged','dimensions':[1080,1350],'concept_generation_calls':20,'image_backend':'gpt-image-2','interior_concepts':12,'feed_cover_concepts':8,'canonical_seal_sha256':LOCK['canonical_seal_sha256'],'carousels':[],'explorations':[]}
    tasks=[]
    for carousel in CONTENT['carousels']:
        dst=DOC/carousel['id']; (dst/'png').mkdir(parents=True,exist_ok=True); (dst/'editable/assets').mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf',dst/'editable/assets/Jost-VF.ttf')
        cm={'id':carousel['id'],'title':carousel['title'],'slides':[]}
        for i,slide in enumerate(carousel['slides']):
            out=dst/'png'/f'{i+1:02d}.png'; edit=dst/'editable'/f'{i+1:02d}.html'
            if i == 0:
                # Preserve existing Phase 2B cover pixels and copy only into this isolated deliverable.
                src=ROOT/'docs/instagram/phase-2b'/carousel['id']/'png'/'01.png'; shutil.copy2(src,out)
                layout='Phase 2B cover retained unchanged'
                lockup=next((r['canonical_lockup_id'] for r in json.loads((ROOT/'docs/instagram/phase-2b'/carousel['id']/'manifest.json').read_text())['slides'] if r['index']==1),'H-02/light')
            else:
                lockup='D-04/light'
                doc, imgs=art(slide,carousel,i,len(carousel['slides']),lockup);edit.write_text(doc)
                for p in imgs: shutil.copy2(p,dst/'editable/assets'/p.name)
                tasks.append((edit,out));layout='Phase 2C editorial photo collage'
            r=RECORDS[lockup]
            cm['slides'].append({'index':i+1,'file':f'{carousel["id"]}/png/{i+1:02d}.png','editable':None if i==0 else f'{carousel["id"]}/editable/{i+1:02d}.html','layout':layout,'canonical_lockup_id':lockup,'canonical_lockup_sha256':r['sha256'],'canonical_seal_sha256':LOCK['canonical_seal_sha256'],'sources':slide.get('sources',[]),'ai_imagery':bool(slide.get('image'))})
        (dst/'manifest.json').write_text(json.dumps(cm,ensure_ascii=False,indent=2))
        manifest['carousels'].append(cm)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for p in pool.map(export,tasks): print(p.relative_to(DOC),flush=True)
    # Concept sources are preserved as explorations, never used as final branded artwork.
    exp_root=BASE/'explorations'
    thumb_root=DOC/'assets/explorations'; thumb_root.mkdir(parents=True,exist_ok=True)
    for p in sorted(exp_root.glob('*/*.png')):
        im=Image.open(p)
        thumb=thumb_root/f'{p.parent.name}.jpg'
        preview=im.convert('RGB'); preview.thumbnail((640,800),Image.Resampling.LANCZOS); preview.save(thumb,quality=86,optimize=True)
        manifest['explorations'].append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'dimensions':list(im.size),'preview':thumb.relative_to(DOC).as_posix(),'preview_sha256':sha(thumb),'type':'feed-cover-concept' if p.parent.name.startswith('feed-') else 'interior-concept','usage':'exploration only; generated lettering/claims are not production copy'})
    for c in manifest['carousels']:
        for s in c['slides']:
            p=DOC/s['file'];s['sha256']=sha(p)
        (DOC/c['id']/'manifest.json').write_text(json.dumps(c,ensure_ascii=False,indent=2))
    manifest['total_final_pngs']=sum(len(c['slides']) for c in manifest['carousels'])
    (DOC/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    shutil.copy2(SOURCE/'content.json',DOC/'content.json')
    shutil.copy2(SOURCE/'production-notes.md',DOC/'phase-2b-factual-base-notes.md')
    print(f"COMPLETE: {manifest['total_final_pngs']} final PNGs; {len(manifest['explorations'])} archived explorations")

if __name__=='__main__': main()

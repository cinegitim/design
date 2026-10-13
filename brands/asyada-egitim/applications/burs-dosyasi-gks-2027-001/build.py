#!/usr/bin/env python3
"""
Burs Dosyası / 001 — GKS 2027 · Asya'da Eğitim Instagram campaign builder.

Produces six 1080x1350 PNG slides from deterministic HTML/CSS/SVG sources:
  1. renders each source with headless Chromium (Jost variable font, real metrics)
  2. runs an in-page geometry/copy QA harness (bounds, safe area, clipping, overlap)
  3. validates the exact locked copy against copy-manifest.json
  4. builds contact sheet, mobile previews, Instagram feed preview and manifests

Usage:  python3 build.py [--only 03] [--skip-qa]
"""
import json, shutil, hashlib, subprocess, tempfile, os, signal, time, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

APP   = Path(__file__).resolve().parent           # brands/asyada-egitim/applications/burs-dosyasi-gks-2027-001
ROOT  = APP.parents[3]                             # repo root
SRC   = APP / 'source'; SRC.mkdir(parents=True, exist_ok=True)
EXPORT= APP / 'export'; EXPORT.mkdir(parents=True, exist_ok=True)
QA    = APP / 'qa';     QA.mkdir(parents=True, exist_ok=True)
MOB   = APP / 'mobile-preview'; MOB.mkdir(parents=True, exist_ok=True)
LOCK  = ROOT / 'brands/asyada-egitim/assets/lockups'
CHROME= '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PALETTE = {'paper':'#F7F3E9','ink':'#1D2027','red':'#BD2120'}
A = 'assets'                                       # relative from source/*.html -> ../assets/...

# ---------------------------------------------------------------- locked copy
COPY = {
 '01': ["BURS DOSYASI / 001",
        "Kore devlet bursunu kaçırdın mı?",
        "30 Eylül’de büyükelçilik başvuruları kapandı.",
        "Ama üniversite yolunda Ekim son tarihleri var.",
        "GKS-UIC 2027",
        "Türkiye’den başvuru mümkün."],
 '02': ["GKS-UIC’de üç üniversitenin başvurusu sürüyor.",
        "23 EKİM 2026","KOREATECH","Bilgisayar / Makine Mühendisliği",
        "30 EKİM 2026","Ajou University","Yapay Zekâ ve Bilgisayar Mühendisliği",
        "30 EKİM 2026","Kookmin University","Yazılım",
        "Son tarihler Kore saatine göredir. Belge teslim yöntemleri üniversiteye göre değişir.",
        "13 Ekim 2026 itibarıyla."],
 '03': ["100 burs kontenjanı. Dünya genelinden başvuru.",
        "13 kurum · Lisans ve ön lisans",
        "7 KONTENJAN","Ajou — Yapay Zekâ ve Bilgisayar Mühendisliği",
        "7 KONTENJAN","Kookmin — Yazılım",
        "5 + 5 KONTENJAN","KOREATECH — Bilgisayar ve Makine Mühendisliği",
        "Kontenjanlar uluslararası adaylara açık. Türkiye’ye özel kota değil."],
 '04': ["Türkiye’den kimler GKS-UIC’ye başvurabilir?",
        "TÜRK VATANDAŞLARI","Başvurabilir.",
        "YAŞ","1 Mart 2002’den sonra doğmuş olmak.",
        "MEZUNİYET","Lise veya ön lisans mezunu olmak ya da en geç 31 Aralık 2026’da mezun olmak.",
        "AKADEMİK BAŞARI","80/100 veya sınıfın ilk %20’si veya kabul edilen eşdeğer not ortalaması.",
        "Adayın ve ebeveynlerinin Kore vatandaşlığı olmamalı. Lisans diploması sahipleri uygun değil. Bölüme özel şartlar ayrıca geçerli."],
 '05': ["GKS 2027 bursu ne kadar?",
        "14.400.000 KRW* / yıl",
        "≈ 9.675 € / yıl",
        "Lisans eğitimi döneminde verilen yaşam desteği.",
        "Ayrıca karşılananlar:",
        "Öğrenim ücreti","Korece hazırlık eğitimi (gerektiğinde)","Uygun adaylar için ekonomi sınıfı uçak bileti",
        "Yaşam desteğine barınma, sağlık sigortası ve ilgili ödenekler dahildir.",
        "Avro karşılığı 12 Ekim 2026 kuru üzerinden yaklaşık hesaplanmıştır."],
 '06': ["BURS DOSYASI / 001",
        "GKS-UIC’de ikinci üniversite tercihi yok.",
        "1 ÜNİVERSİTE","1 BÖLÜM",
        "Birden fazla üniversiteye başvurmak GKS değerlendirmesinden çıkarılmana neden olabilir.",
        "Türkiye’den başvurabileceğin programları, gerekli belgeleri ve son tarihleri birlikte kontrol edelim.",
        "Ücretsiz ön görüşme"],
}
(APP / 'copy-manifest.json').write_text(json.dumps(
    {'campaign':'BURS DOSYASI / 001 — GKS 2027','locked':True,
     'note':'Exact on-slide copy. Apostrophes are U+2019. Decorative background numerals, lockup artwork and SVG icons are not copy.',
     'slides':COPY}, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- QA harness (runs in page)
QA_JS = r"""
(function () {
  const out = { errors: [], rects: [], copy: [], metrics: {} };
  const vis = el => { let s='';
    for (const n of el.childNodes){
      if (n.nodeType === 3) s += n.textContent;
      else if (n.nodeType === 1) s += ' ' + vis(n) + ' ';
    }
    return s.replace(/\s+/g,' ').trim(); };
  function measure() {
    try {
      for (const el of document.querySelectorAll('[data-copy]')) {
        out.copy.push({ claim: el.dataset.copy, visible: vis(el) });
      }
      for (const el of document.querySelectorAll('[data-qa]')) {
        const r = el.getBoundingClientRect();
        const rec = { id: el.dataset.qa, zone: el.dataset.zone || 'txt',
          x:+r.x.toFixed(2), y:+r.y.toFixed(2), w:+r.width.toFixed(2), h:+r.height.toFixed(2),
          right:+r.right.toFixed(2), bottom:+r.bottom.toFixed(2),
          clipX: el.scrollWidth  > el.clientWidth  + 1,
          clipY: el.scrollHeight > el.clientHeight + 1 };
        if (rec.x < -0.5 || rec.y < -0.5 || rec.right > 1080.5 || rec.bottom > 1350.5)
          out.errors.push({ type:'out-of-canvas', id:rec.id, rect:rec });
        if (rec.zone === 'txt' && (rec.x < 63.5 || rec.y < 63.5 || rec.right > 1016.5 || rec.bottom > 1286.5))
          out.errors.push({ type:'outside-safe-area', id:rec.id, rect:rec });
        if (rec.zone === 'logo' && (rec.x < 63.5 || rec.y < 63.5 || rec.right > 1016.5 || rec.bottom > 1286.5))
          out.errors.push({ type:'logo-outside-safe-area', id:rec.id, rect:rec });
        const cs = getComputedStyle(el);
        const reallyClipsX = cs.overflowX !== 'visible' && rec.clipX;
        const reallyClipsY = cs.overflowY !== 'visible' && rec.clipY;
        if (reallyClipsX || reallyClipsY) out.errors.push({ type:'text-clipped', id:rec.id, clipX:reallyClipsX, clipY:reallyClipsY });
        const lines = [];
        try {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          let node;
          while ((node = walker.nextNode())) {
            if (!node.textContent.trim()) continue;
            const text = node.textContent;
            const rectAt = i => { const r2 = document.createRange(); r2.setStart(node,i); r2.setEnd(node,i); return r2.getBoundingClientRect(); };
            let lineStart = 0, prevTop = null;
            const push = (a,b) => { const rr = document.createRange(); rr.setStart(node,a); rr.setEnd(node,b);
              const rb = rr.getBoundingClientRect();
              if (rb.width > 0.5 || rb.height > 0.5)
                lines.push({ x:+rb.x.toFixed(2), y:+rb.y.toFixed(2), w:+rb.width.toFixed(2), h:+rb.height.toFixed(2),
                             text: text.slice(a,b).replace(/\s+$/,'') }); };
            for (let i = 0; i <= text.length; i++) {
              const b2 = rectAt(Math.min(i, text.length));
              if (b2.top > 0 || b2.height > 0) {
                if (prevTop !== null && Math.abs(b2.top - prevTop) > 2) { push(lineStart, i); lineStart = i; }
                prevTop = b2.top;
              }
            }
            push(lineStart, text.length);
          }
        } catch (e) {}
        rec.lines = lines;
        const cs2 = getComputedStyle(el);
        const fs = cs2.fontSize, fw = cs2.fontWeight;
        try {
          const c = document.createElement('canvas').getContext('2d');
          c.font = fw + ' ' + fs + ' Jost';
          const m = c.measureText('ÃÃgy');
          out.metrics[fs] = { asc:+m.fontBoundingBoxAscent.toFixed(2), desc:+m.fontBoundingBoxDescent.toFixed(2) };
        } catch (e) {}
        out.rects.push(rec);
      }
      const fg = out.rects.filter(r => r.zone === 'txt' || r.zone === 'logo');
      for (let i = 0; i < fg.length; i++) for (let j = i+1; j < fg.length; j++) {
        const a = fg[i], b = fg[j];
        const ox = Math.min(a.right,b.right) - Math.max(a.x,b.x);
        const oy = Math.min(a.bottom,b.bottom) - Math.max(a.y,b.y);
        if (ox > 1 && oy > 1) out.errors.push({ type:'overlap', a:a.id, b:b.id, ox:+ox.toFixed(1), oy:+oy.toFixed(1) });
      }
    } catch (e) { out.errors.push({ type:'js-error', message: String(e) }); }
    out.jostLoaded = !!(document.fonts && document.fonts.status === 'loaded');
    const pre = document.createElement('pre'); pre.id = 'qa-result';
    pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
  }
  function tick() {
    if (document.fonts && document.fonts.status !== 'loaded') { setTimeout(tick, 50); return; }
    measure();
  }
  if (document.readyState === 'complete') tick(); else window.addEventListener('load', tick);
})();
"""

def render_html(body_extra_css, body_html, qa_mode=False):
    font_face = "@font-face{font-family:Jost;src:url(../assets/Jost-VF.ttf) format('truetype');font-weight:100 900}"
    qa = f"<script>{QA_JS}</script>" if qa_mode else ""
    return ("<!doctype html><html lang=\"tr\"><head><meta charset=\"utf-8\">"
            f"<style>{font_face}*{{box-sizing:border-box;margin:0;padding:0}}"
            "html,body{width:1080px;height:1350px;overflow:hidden;background:#1D2027}"
            "body{font-family:Jost,'Jost',Arial,sans-serif;-webkit-font-smoothing:antialiased}"
            f"{body_extra_css}</style></head><body>{body_html}{qa}</body></html>")

def shot(url, png, mode):
    """Render with headless Chrome. Screenshot: spawn+poll+kill (Chrome may linger on virtual time)."""
    with tempfile.TemporaryDirectory(prefix='bursdosyasi-', dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as prof:
        cmd = [CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
               '--force-device-scale-factor=1','--window-size=1080,1350',
               '--virtual-time-budget=12000','--default-background-color=FF1D2027',
               f'--user-data-dir={prof}']
        if mode == 'screenshot':
            cmd.append(f'--screenshot={png}')
            cmd.append(url)
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline and proc.poll() is None:
                if png and os.path.exists(png) and os.path.getsize(png) > 10000: break
                time.sleep(.2)
            if proc.poll() is None:
                try: os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try: os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    proc.wait(timeout=5)
            return ''
        cmd.append(url); cmd.append('--dump-dom')
        for attempt in range(5):
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                if 'qa-result' in proc.stdout: return proc.stdout
            except subprocess.TimeoutExpired:
                pass
            time.sleep(3)
        print('   !! dump-dom failed for', url); return ''

def font(path,size): return ImageFont.truetype(str(path), size)

F = APP / 'assets/Jost-VF.ttf'
FD = font(F, 26)   # for PIL labels on contact sheet

def contact_sheet(pngs, out):
    W,H,colw,colh = 1080,1350,300,375
    pad,bg = 26,(216,210,199)
    cols,rows = 3,2
    sheet = Image.new('RGB',(cols*(colw+pad)+pad, rows*(colh+pad)+pad+86), bg)
    d = ImageDraw.Draw(sheet)
    d.text((pad,26),'BURS DOSYASI / 001 — GKS 2027  ·  6 slides  ·  1080 × 1350', font=font(F,30), fill=(29,32,39))
    for i,p in enumerate(pngs):
        im = Image.open(p).convert('RGB'); im.thumbnail((colw,colh))
        x = pad + (i%cols)*(colw+pad); y = 86 + (i//cols)*(colh+pad)
        d.rectangle([x-2,y-2,x+im.width+1,y+im.height+1], outline=(29,32,39), width=2)
        sheet.paste(im,(x,y))
        d.text((x, y+im.height+8), f'{i+1:02d}', font=font(F,24), fill=(189,33,32))
    sheet.save(out, quality=92)
    return out

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

# ================================================================ SLIDE 01 — hook
S1_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#101318}
.photo{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:center 62%}
.veil{position:absolute;inset:0;background:
  linear-gradient(180deg, rgba(13,15,20,.86) 0%, rgba(13,15,20,.52) 30%, rgba(13,15,20,.58) 58%, rgba(13,15,20,.93) 100%)}
.sid{position:absolute;left:72px;top:64px;font-size:30px;font-weight:600;letter-spacing:.14em;color:#F7F3E9;z-index:3}
.sid::before{content:'/';color:#BD2120;padding-right:10px}
.sid b{display:block;width:96px;height:5px;background:#BD2120;margin-top:16px}
.q{position:absolute;left:72px;top:176px;width:920px;z-index:3;font-size:78px;font-weight:600;line-height:1.04;letter-spacing:-.02em;color:#F7F3E9}
.q em{font-style:normal;color:#BD2120}
.p1{position:absolute;left:72px;top:404px;width:820px;z-index:3;font-size:35px;font-weight:500;line-height:1.25;color:rgba(247,243,233,.92)}
.p2{position:absolute;left:72px;top:496px;width:840px;z-index:3;font-size:47px;font-weight:600;line-height:1.14;letter-spacing:-.01em;color:#F7F3E9;
  border-left:10px solid #BD2120;padding-left:28px}
.deco-date{position:absolute;left:0;right:0;top:636px;z-index:2;text-align:center;font-size:212px;font-weight:650;
  letter-spacing:.02em;color:rgba(247,243,233,.13);line-height:1}
.strike{position:absolute;left:88px;width:904px;height:12px;background:#BD2120;top:744px;z-index:3;opacity:.85;
  transform:rotate(-1.6deg);border-radius:6px}
.bottom{position:absolute;left:72px;right:72px;bottom:76px;z-index:3;display:flex;justify-content:space-between;align-items:flex-end}
.gks{font-size:44px;font-weight:650;letter-spacing:.02em;color:#F7F3E9}
.tr{font-size:30px;font-weight:500;color:rgba(247,243,233,.85);margin-top:10px}
.logo{width:380px;height:auto;display:block}
"""
S1_HTML = """
<main class="slide">
  <img class="photo" src="../assets/photos/campus-hero-ewha.jpg" alt="">
  <div class="veil"></div>
  <div class="deco-date" data-qa="deco-date" data-zone="deco">30 EYLÜL</div>
  <div class="strike" data-qa="strike" data-zone="deco"></div>
  <div class="sid" data-qa="sid" data-zone="txt" data-copy="BURS DOSYASI / 001">BURS DOSYASI / 001<b></b></div>
  <h1 class="q" data-qa="question" data-zone="txt"><div data-copy="Kore devlet bursunu kaçırdın mı?">Kore devlet bursunu<br><em>kaçırdın mı?</em></div></h1>
  <p class="p1" data-qa="embassy-closed" data-zone="txt"><span data-copy="30 Eylül’de büyükelçilik başvuruları kapandı.">30 Eylül’de büyükelçilik başvuruları kapandı.</span></p>
  <p class="p2" data-qa="university-track" data-zone="txt"><span data-copy="Ama üniversite yolunda Ekim son tarihleri var.">Ama üniversite yolunda Ekim son tarihleri var.</span></p>
  <div class="bottom" data-qa="bottom" data-zone="wrap">
    <div>
      <div class="gks" data-qa="gks-uic" data-zone="txt"><span data-copy="GKS-UIC 2027">GKS-UIC 2027</span></div>
      <div class="tr" data-qa="tr-apply" data-zone="txt"><span data-copy="Türkiye’den başvuru mümkün.">Türkiye’den başvuru mümkün.</span></div>
    </div>
    <img class="logo" data-qa="logo" data-zone="logo" src="../assets/lockups/p-01-primary-stacked-dark.svg" alt="Asya’da Eğitim">
  </div>
</main>
"""

# ================================================================ SLIDE 02 — deadlines
S2_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F7F3E9;color:#1D2027;padding:64px 72px 0}
.head{position:relative;z-index:2;font-size:54px;font-weight:600;line-height:1.08;letter-spacing:-.015em;width:936px}
.rail{position:absolute;left:76px;top:237px;bottom:421px;width:3px;background:rgba(29,32,39,.22);z-index:1}
.dot{position:absolute;left:-8.5px;width:20px;height:20px;border-radius:50%;background:#1D2027}
.dot.hot{background:#BD2120;width:26px;height:26px;left:-11.5px}
.e1{position:relative;z-index:2;display:flex;justify-content:space-between;margin:22px 0 0 34px;height:436px}
.e1 .txt{width:490px;padding-top:6px}
.e1 .d{font-size:58px;font-weight:650;letter-spacing:-.01em;color:#BD2120;line-height:1}
.e1 .n{font-size:46px;font-weight:650;margin-top:14px;line-height:1.02}
.e1 .p{font-size:30px;font-weight:500;margin-top:14px;line-height:1.22;color:rgba(29,32,39,.88)}
.e1 img{width:400px;height:400px;object-fit:cover;object-position:center 38%;border-top:8px solid #BD2120}
.row{position:relative;z-index:2;display:flex;align-items:center;gap:34px;margin:26px 0 0 34px;height:196px;border-top:2px solid rgba(29,32,39,.16)}
.row img{width:250px;height:170px;object-fit:cover}
.row .d{font-size:44px;font-weight:650;color:#1D2027;line-height:1;letter-spacing:-.01em}
.row .n{font-size:37px;font-weight:600;margin-top:10px}
.row .p{font-size:28px;font-weight:500;margin-top:8px;color:rgba(29,32,39,.85)}
.row .txt{width:640px}
.foot{position:relative;z-index:2;margin:26px 0 0 34px;border-top:3px solid #1D2027;padding-top:20px;
  display:flex;justify-content:space-between;align-items:center;gap:40px}
.n1{font-size:24px;font-weight:500;line-height:1.32;color:rgba(29,32,39,.9);width:610px}
.n2{font-size:24px;font-weight:650;color:#BD2120;margin-top:10px}
.logo2{width:240px;height:auto;display:block;flex:0 0 auto}
"""
S2_HTML = """
<main class="slide">
  <div class="rail"><span class="dot hot" style="top:-13px"></span><span class="dot" style="top:460px"></span><span class="dot" style="top:682px"></span></div>
  <h1 class="head" data-qa="head" data-zone="txt"><span data-copy="GKS-UIC’de üç üniversitenin başvurusu sürüyor.">GKS-UIC’de üç üniversitenin<br>başvurusu sürüyor.</span></h1>
  <section class="e1" data-qa="entry-koreatech" data-zone="wrap">
    <div class="txt">
      <div class="d" data-qa="date-1" data-zone="txt"><span data-copy="23 EKİM 2026">23 EKİM 2026</span></div>
      <div class="n" data-qa="name-1" data-zone="txt"><span data-copy="KOREATECH">KOREATECH</span></div>
      <div class="p" data-qa="prog-1" data-zone="txt"><span data-copy="Bilgisayar / Makine Mühendisliği">Bilgisayar / Makine Mühendisliği</span></div>
    </div>
    <img src="../assets/photos/koreatech-hum.jpg" alt="KOREATECH kampüs">
  </section>
  <section class="row" data-qa="entry-ajou" data-zone="wrap">
    <img src="../assets/photos/ajou-campus.jpg" alt="Ajou University kampüs">
    <div class="txt">
      <div class="d" data-qa="date-2" data-zone="txt"><span data-copy="30 EKİM 2026">30 EKİM 2026</span></div>
      <div class="n" data-qa="name-2" data-zone="txt"><span data-copy="Ajou University">Ajou University</span></div>
      <div class="p" data-qa="prog-2" data-zone="txt"><span data-copy="Yapay Zekâ ve Bilgisayar Mühendisliği">Yapay Zekâ ve Bilgisayar Mühendisliği</span></div>
    </div>
  </section>
  <section class="row" data-qa="entry-kookmin" data-zone="wrap">
    <img src="../assets/photos/kookmain-10.jpg" alt="Kookmin University kampüs">
    <div class="txt">
      <div class="d" data-qa="date-3" data-zone="txt"><span data-copy="30 EKİM 2026">30 EKİM 2026</span></div>
      <div class="n" data-qa="name-3" data-zone="txt"><span data-copy="Kookmin University">Kookmin University</span></div>
      <div class="p" data-qa="prog-3" data-zone="txt"><span data-copy="Yazılım">Yazılım</span></div>
    </div>
  </section>
  <footer class="foot" data-qa="footer" data-zone="wrap">
    <div>
      <p class="n1" data-qa="note-1" data-zone="txt"><span data-copy="Son tarihler Kore saatine göredir. Belge teslim yöntemleri üniversiteye göre değişir.">Son tarihler Kore saatine göredir. Belge teslim yöntemleri üniversiteye göre değişir.</span></p>
      <p class="n2" data-qa="note-2" data-zone="txt"><span data-copy="13 Ekim 2026 itibarıyla.">13 Ekim 2026 itibarıyla.</span></p>
    </div>
    <img class="logo2" data-qa="logo" data-zone="logo" src="../assets/lockups/d-04-small-use-digital-light.svg" alt="Asya’da Eğitim">
  </footer>
</main>
"""

# ================================================================ SLIDE 03 — quotas
S3_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#ECE5D3;color:#1D2027}
.head{position:absolute;left:72px;top:64px;width:576px;z-index:3}
.head h1{font-size:48px;font-weight:600;line-height:1.12;letter-spacing:-.015em}
.head .sub{font-size:31px;font-weight:650;color:#BD2120;margin-top:18px;letter-spacing:.01em}
.logo3{position:absolute;right:72px;top:64px;width:352px;height:auto;z-index:3}
.photo3{position:absolute;right:72px;top:318px;width:462px;height:520px;object-fit:cover;object-position:center 42%;
  filter:saturate(.82) contrast(1.04)}
.photo3-veil{position:absolute;right:72px;top:318px;width:462px;height:520px;z-index:2;
  background:linear-gradient(180deg, rgba(29,32,39,.05), rgba(29,32,39,.42))}
.big100{position:absolute;left:58px;top:300px;z-index:4;font-size:300px;font-weight:650;color:#BD2120;line-height:.9;
  letter-spacing:-.03em}
.big100 small{display:block;font-size:30px;font-weight:650;color:#1D2027;letter-spacing:.02em;margin-top:6px}
.quotas{position:absolute;left:72px;right:72px;top:878px;z-index:3;display:flex;gap:0}
.qcol{flex:1;padding:0 26px 0 0}
.qcol + .qcol{border-left:2px solid rgba(29,32,39,.18);padding-left:26px}
.fig{font-size:86px;font-weight:650;color:#BD2120;line-height:1;letter-spacing:-.02em}
.lab{font-size:26px;font-weight:650;letter-spacing:.08em;color:#1D2027;margin-top:6px}
.att{font-size:25px;font-weight:500;line-height:1.28;margin-top:12px;color:rgba(29,32,39,.9)}
.strip{position:absolute;left:0;right:0;bottom:0;height:140px;background:#1D2027;color:#F7F3E9;z-index:3;
  display:flex;align-items:flex-start;padding:38px 72px 0;font-size:30px;font-weight:550;line-height:1.25}
"""
S3_HTML = """
<main class="slide">
  <div class="head" data-qa="head" data-zone="wrap">
    <h1 data-qa="headline" data-zone="txt"><span data-copy="100 burs kontenjanı. Dünya genelinden başvuru.">100 burs kontenjanı.<br>Dünya genelinden başvuru.</span></h1>
    <div class="sub" data-qa="institutions" data-zone="txt"><span data-copy="13 kurum · Lisans ve ön lisans">13 kurum · Lisans ve ön lisans</span></div>
  </div>
  <img class="logo3" data-qa="logo" data-zone="logo" src="../assets/lockups/p-01-primary-stacked-light.svg" alt="Asya’da Eğitim">
  <img class="photo3" src="../assets/photos/koreatech-eng4.jpg" alt="KOREATECH mühendislik binası">
  <div class="photo3-veil"></div>
  <div class="big100" data-qa="big100" data-zone="deco">100<small data-qa="big100-sub" data-zone="deco">DÜNYA GENELİNDEN BAŞVURU</small></div>
  <div class="quotas" data-qa="quotas" data-zone="wrap">
    <div class="qcol">
      <div data-copy="7 KONTENJAN">
        <div class="fig" data-qa="fig-ajou" data-zone="txt">7</div>
        <div class="lab" data-qa="lab-ajou" data-zone="txt">KONTENJAN</div>
      </div>
      <div class="att" data-qa="att-ajou" data-zone="txt"><span data-copy="Ajou — Yapay Zekâ ve Bilgisayar Mühendisliği">Ajou — Yapay Zekâ ve Bilgisayar Mühendisliği</span></div>
    </div>
    <div class="qcol">
      <div data-copy="7 KONTENJAN">
        <div class="fig" data-qa="fig-kookmin" data-zone="txt">7</div>
        <div class="lab" data-qa="lab-kookmin" data-zone="txt">KONTENJAN</div>
      </div>
      <div class="att" data-qa="att-kookmin" data-zone="txt"><span data-copy="Kookmin — Yazılım">Kookmin — Yazılım</span></div>
    </div>
    <div class="qcol">
      <div data-copy="5 + 5 KONTENJAN">
        <div class="fig" data-qa="fig-koreatech" data-zone="txt">5 + 5</div>
        <div class="lab" data-qa="lab-koreatech" data-zone="txt">KONTENJAN</div>
      </div>
      <div class="att" data-qa="att-koreatech" data-zone="txt"><span data-copy="KOREATECH — Bilgisayar ve Makine Mühendisliği">KOREATECH — Bilgisayar ve Makine Mühendisliği</span></div>
    </div>
  </div>
  <div class="strip" data-qa="strip" data-zone="wrap"><span data-qa="strip-t" data-zone="txt" data-copy="Kontenjanlar uluslararası adaylara açık. Türkiye’ye özel kota değil.">Kontenjanlar uluslararası adaylara açık. Türkiye’ye özel kota değil.</span></div>
</main>
"""

# ================================================================ SLIDE 04 — eligibility
S4_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F2ECDF;color:#1D2027}
.logo4{position:absolute;left:72px;top:64px;width:560px;height:auto;z-index:3}
.q4{position:absolute;left:72px;top:302px;width:936px;z-index:2;font-size:52px;font-weight:600;line-height:1.12;letter-spacing:-.015em}
.band{position:absolute;left:72px;right:72px;top:440px;z-index:2;background:#BD2120;color:#F7F3E9;padding:24px 40px;
  display:flex;align-items:baseline;gap:34px;height:104px}
.band .a{font-size:38px;font-weight:650;letter-spacing:.06em}
.band .b{font-size:46px;font-weight:700}
.photo4{position:absolute;left:72px;top:564px;width:936px;height:142px;object-fit:cover;object-position:center 46%;
  z-index:1;filter:saturate(.9)}
.groups{position:absolute;left:72px;right:72px;top:726px;z-index:2}
.grp{display:flex;gap:26px;padding:16px 0;border-top:2px solid rgba(29,32,39,.16)}
.grp:last-child{border-bottom:2px solid rgba(29,32,39,.16)}
.num{flex:0 0 118px;font-size:58px;font-weight:650;color:#BD2120;line-height:1;padding-top:2px}
.gtxt{flex:1}
.gh{display:flex;align-items:center;gap:16px;font-size:33px;font-weight:650;letter-spacing:.02em}
.gh svg{width:42px;height:42px}
.gb{font-size:26px;font-weight:500;line-height:1.32;margin-top:8px;color:rgba(29,32,39,.92)}
.disc{position:absolute;left:0;right:0;top:1181px;height:130px;background:#1D2027;color:#F7F3E9;z-index:3;
  padding:30px 72px 0}
.disc p{font-size:26px;font-weight:500;line-height:1.34;max-width:936px}
"""
S4_HTML = """
<main class="slide">
  <img class="logo4" data-qa="logo" data-zone="logo" src="../assets/lockups/h-02-primary-horizontal-light.svg" alt="Asya’da Eğitim">
  <h1 class="q4" data-qa="question" data-zone="txt"><span data-copy="Türkiye’den kimler GKS-UIC’ye başvurabilir?">Türkiye’den kimler GKS-UIC’ye başvurabilir?</span></h1>
  <div class="band" data-qa="answer" data-zone="wrap">
    <span class="a" data-qa="answer-a" data-zone="txt"><span data-copy="TÜRK VATANDAŞLARI">TÜRK VATANDAŞLARI</span></span>
    <span class="b" data-qa="answer-b" data-zone="txt"><span data-copy="Başvurabilir.">Başvurabilir.</span></span>
  </div>
  <img class="photo4" src="../assets/photos/kyunghee-library.jpg" alt="Üniversite kütüphanesi">
  <div class="groups" data-qa="groups" data-zone="wrap">
    <div class="grp" data-qa="grp-yas" data-zone="wrap">
      <div class="num" data-qa="num-1" data-zone="deco">01</div>
      <div class="gtxt">
        <div class="gh" data-qa="gh-1" data-zone="txt"><svg viewBox="0 0 48 48" fill="none" stroke="#1D2027" stroke-width="3" stroke-linecap="round"><rect x="7" y="11" width="34" height="30" rx="3"/><path d="M7 20h34M16 7v8M32 7v8"/><path d="M17 30h6"/></svg><span data-copy="YAŞ">YAŞ</span></div>
        <p class="gb" data-qa="gb-1" data-zone="txt"><span data-copy="1 Mart 2002’den sonra doğmuş olmak.">1 Mart 2002’den sonra doğmuş olmak.</span></p>
      </div>
    </div>
    <div class="grp" data-qa="grp-mezuniyet" data-zone="wrap">
      <div class="num" data-qa="num-2" data-zone="deco">02</div>
      <div class="gtxt">
        <div class="gh" data-qa="gh-2" data-zone="txt"><svg viewBox="0 0 48 48" fill="none" stroke="#1D2027" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19 24 9l20 10-20 10z"/><path d="M12 23.5V33c0 3.4 5.4 6 12 6s12-2.6 12-6V23.5"/><path d="M44 19v10"/></svg><span data-copy="MEZUNİYET">MEZUNİYET</span></div>
        <p class="gb" data-qa="gb-2" data-zone="txt"><span data-copy="Lise veya ön lisans mezunu olmak ya da en geç 31 Aralık 2026’da mezun olmak.">Lise veya ön lisans mezunu olmak ya da en geç 31 Aralık 2026’da mezun olmak.</span></p>
      </div>
    </div>
    <div class="grp" data-qa="grp-akademik" data-zone="wrap">
      <div class="num" data-qa="num-3" data-zone="deco">03</div>
      <div class="gtxt">
        <div class="gh" data-qa="gh-3" data-zone="txt"><svg viewBox="0 0 48 48" fill="none" stroke="#1D2027" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="31" r="12"/><path d="M17 19l-4-11 10 5zM31 19l4-11-10 5z"/></svg><span data-copy="AKADEMİK BAŞARI">AKADEMİK BAŞARI</span></div>
        <p class="gb" data-qa="gb-3" data-zone="txt"><span data-copy="80/100 veya sınıfın ilk %20’si veya kabul edilen eşdeğer not ortalaması.">80/100 veya sınıfın ilk %20’si veya kabul edilen eşdeğer not ortalaması.</span></p>
      </div>
    </div>
  </div>
  <div class="disc" data-qa="disclaimer" data-zone="wrap"><p data-qa="disc-p" data-zone="txt"><span data-copy="Adayın ve ebeveynlerinin Kore vatandaşlığı olmamalı. Lisans diploması sahipleri uygun değil. Bölüme özel şartlar ayrıca geçerli.">Adayın ve ebeveynlerinin Kore vatandaşlığı olmamalı. Lisans diploması sahipleri uygun değil. Bölüme özel şartlar ayrıca geçerli.</span></p></div>
</main>
"""

# ================================================================ SLIDE 05 — amount
S5_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#1D2027;color:#F7F3E9}
.logo5{position:absolute;right:72px;top:64px;width:352px;height:auto;z-index:3}
.q5{position:absolute;left:72px;top:64px;width:552px;font-size:58px;font-weight:600;line-height:1.08;letter-spacing:-.015em;z-index:3}
.krw{position:absolute;left:72px;top:452px;z-index:3;width:max-content}
.krw .amount{font-size:122px;font-weight:650;letter-spacing:-.025em;line-height:1;color:#F7F3E9}
.krw .cur{font-size:54px;font-weight:600;color:#BD2120;margin-left:14px}
.krw .yr{font-size:38px;font-weight:500;color:rgba(247,243,233,.66);margin-left:10px}
.eur{position:absolute;left:72px;top:640px;z-index:3;width:max-content;font-size:54px;font-weight:500;
  color:rgba(247,243,233,.74);letter-spacing:-.01em}
.life{position:absolute;left:72px;top:768px;z-index:3;width:max-content;font-size:32px;font-weight:550}
.also{position:absolute;left:72px;top:850px;z-index:3;width:max-content;font-size:30px;font-weight:650;letter-spacing:.02em}
.items{position:absolute;left:72px;right:72px;top:900px;z-index:3;display:flex;gap:26px}
.item{flex:1;border-top:3px solid rgba(247,243,233,.34);padding-top:18px}
.item svg{width:54px;height:54px;display:block;margin-bottom:14px}
.item p{font-size:28px;font-weight:500;line-height:1.3}
.noteA{position:absolute;left:72px;right:72px;top:1098px;z-index:3;border:2px solid rgba(247,243,233,.4);
  padding:18px 26px;font-size:27px;font-weight:550;line-height:1.3;width:max-content;max-width:936px}
.noteB{position:absolute;left:72px;top:1246px;z-index:3;width:max-content;font-size:24px;font-weight:400;
  color:rgba(247,243,233,.72);line-height:1.3}
.rule5{position:absolute;left:72px;right:72px;top:1230px;height:2px;background:rgba(247,243,233,.28);z-index:3}
"""
S5_HTML = """
<main class="slide">
  <img class="logo5" data-qa="logo" data-zone="logo" src="../assets/lockups/p-01-primary-stacked-dark.svg" alt="Asya’da Eğitim">
  <h1 class="q5" data-qa="question" data-zone="txt"><span data-copy="GKS 2027 bursu ne kadar?">GKS 2027 bursu ne kadar?</span></h1>
  <div class="krw" data-qa="krw" data-zone="wrap"><div data-copy="14.400.000 KRW* / yıl"><span class="amount" data-qa="krw-amount" data-zone="txt">14.400.000</span><span class="cur" data-qa="krw-cur" data-zone="txt">KRW*</span><span class="yr" data-qa="krw-yr" data-zone="txt">/ yıl</span></div></div>
  <div class="eur" data-qa="eur" data-zone="txt"><span data-copy="≈ 9.675 € / yıl">≈ 9.675 € / yıl</span></div>
  <p class="life" data-qa="life" data-zone="txt"><span data-copy="Lisans eğitimi döneminde verilen yaşam desteği.">Lisans eğitimi döneminde verilen yaşam desteği.</span></p>
  <div class="also" data-qa="also" data-zone="txt"><span data-copy="Ayrıca karşılananlar:">Ayrıca karşılananlar:</span></div>
  <div class="items" data-qa="items" data-zone="wrap">
    <div class="item" data-qa="item-1" data-zone="wrap">
      <svg viewBox="0 0 48 48" fill="none" stroke="#F7F3E9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19 24 9l20 10-20 10z"/><path d="M12 23.5V33c0 3.4 5.4 6 12 6s12-2.6 12-6V23.5"/><path d="M44 19v10"/></svg>
      <p data-qa="item-1-t" data-zone="txt"><span data-copy="Öğrenim ücreti">Öğrenim ücreti</span></p>
    </div>
    <div class="item" data-qa="item-2" data-zone="wrap">
      <svg viewBox="0 0 48 48" fill="none" stroke="#F7F3E9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8h30a4 4 0 0 1 4 4v14a4 4 0 0 1-4 4H16l-10 8z"/><path d="M15 17h12M15 24h8"/></svg>
      <p data-qa="item-2-t" data-zone="txt"><span data-copy="Korece hazırlık eğitimi (gerektiğinde)">Korece hazırlık eğitimi (gerektiğinde)</span></p>
    </div>
    <div class="item" data-qa="item-3" data-zone="wrap">
      <svg viewBox="0 0 48 48" fill="none" stroke="#F7F3E9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M43 4 6 20l11 4 4 11z"/><path d="M43 4 17 28"/></svg>
      <p data-qa="item-3-t" data-zone="txt"><span data-copy="Uygun adaylar için ekonomi sınıfı uçak bileti">Uygun adaylar için ekonomi sınıfı uçak bileti</span></p>
    </div>
  </div>
  <div class="noteA" data-qa="note-a" data-zone="txt"><span data-copy="Yaşam desteğine barınma, sağlık sigortası ve ilgili ödenekler dahildir.">Yaşam desteğine barınma, sağlık sigortası ve ilgili ödenekler dahildir.</span></div>
  <div class="rule5" data-qa="rule-5" data-zone="deco"></div>
  <div class="noteB" data-qa="note-b" data-zone="txt"><span data-copy="Avro karşılığı 12 Ekim 2026 kuru üzerinden yaklaşık hesaplanmıştır.">Avro karşılığı 12 Ekim 2026 kuru üzerinden yaklaşık hesaplanmıştır.</span></div>
</main>
"""

# ================================================================ SLIDE 06 — single choice / CTA
S6_CSS = """
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#101318}
.photo6{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:center 30%}
.veil6{position:absolute;inset:0;background:linear-gradient(180deg, rgba(13,15,20,.9) 0%, rgba(13,15,20,.62) 34%, rgba(13,15,20,.7) 62%, rgba(13,15,20,.94) 100%)}
.sid6{position:absolute;left:72px;top:64px;z-index:3;font-size:30px;font-weight:600;letter-spacing:.14em;color:#F7F3E9}
.sid6::before{content:'/';color:#BD2120;padding-right:10px}
.sid6 b{display:block;width:96px;height:5px;background:#BD2120;margin-top:16px}
.h6{position:absolute;left:72px;top:176px;width:700px;z-index:3;font-size:64px;font-weight:650;line-height:1.06;letter-spacing:-.02em;color:#F7F3E9}
.path{position:absolute;left:78px;top:420px;bottom:668px;width:4px;background:#BD2120;z-index:3;opacity:.9}
.node{position:absolute;left:-9px;bottom:-11px;width:22px;height:22px;border-radius:50%;background:#BD2120}
.choice{position:absolute;left:120px;top:404px;z-index:3;display:flex;flex-direction:column;gap:34px}
.choice div{font-size:92px;font-weight:650;letter-spacing:-.01em;color:#F7F3E9;line-height:1}
.warn{position:absolute;left:72px;top:716px;width:540px;z-index:3;border-left:8px solid #BD2120;padding-left:24px;
  font-size:31px;font-weight:500;line-height:1.34;color:rgba(247,243,233,.94)}
.srv{position:absolute;left:72px;top:886px;width:540px;z-index:3;font-size:31px;font-weight:500;line-height:1.34;color:rgba(247,243,233,.94)}
.cta{position:absolute;left:72px;top:1040px;z-index:3;background:#BD2120;color:#F7F3E9;font-size:40px;font-weight:650;
  padding:22px 40px;letter-spacing:.01em}
.logo6{position:absolute;right:72px;bottom:64px;width:380px;height:auto;z-index:3}
"""
S6_HTML = """
<main class="slide">
  <img class="photo6" src="../assets/photos/campus-skku.jpg" alt="">
  <div class="veil6"></div>
  <div class="sid6" data-qa="sid" data-zone="txt" data-copy="BURS DOSYASI / 001">BURS DOSYASI / 001<b></b></div>
  <h1 class="h6" data-qa="headline" data-zone="txt"><span data-copy="GKS-UIC’de ikinci üniversite tercihi yok.">GKS-UIC’de ikinci üniversite tercihi yok.</span></h1>
  <div class="path" data-qa="path" data-zone="deco"><span class="node" data-qa="node" data-zone="deco"></span></div>
  <div class="choice" data-qa="choice" data-zone="wrap">
    <div data-qa="one-uni" data-zone="txt"><span data-copy="1 ÜNİVERSİTE">1 ÜNİVERSİTE</span></div>
    <div data-qa="one-dept" data-zone="txt"><span data-copy="1 BÖLÜM">1 BÖLÜM</span></div>
  </div>
  <p class="warn" data-qa="warning" data-zone="txt"><span data-copy="Birden fazla üniversiteye başvurmak GKS değerlendirmesinden çıkarılmana neden olabilir.">Birden fazla üniversiteye başvurmak GKS değerlendirmesinden çıkarılmana neden olabilir.</span></p>
  <p class="srv" data-qa="service" data-zone="txt"><span data-copy="Türkiye’den başvurabileceğin programları, gerekli belgeleri ve son tarihleri birlikte kontrol edelim.">Türkiye’den başvurabileceğin programları, gerekli belgeleri ve son tarihleri birlikte kontrol edelim.</span></p>
  <div class="cta" data-qa="cta" data-zone="txt"><span data-copy="Ücretsiz ön görüşme">Ücretsiz ön görüşme</span></div>
  <img class="logo6" data-qa="logo" data-zone="logo" src="../assets/lockups/p-01-primary-stacked-dark.svg" alt="Asya’da Eğitim">
</main>
"""

SLIDES = [
 ('01','01-the-scholarship-hook',  S1_CSS, S1_HTML,  'P-01/dark'),
 ('02','02-three-deadlines',       S2_CSS, S2_HTML,  'D-04/light'),
 ('03','03-international-quotas',  S3_CSS, S3_HTML,  'P-01/light'),
 ('04','04-eligibility',           S4_CSS, S4_HTML,  'P-01/light'),
 ('05','05-scholarship-amount',    S5_CSS, S5_HTML,  'P-01/dark'),
 ('06','06-single-choice-cta',     S6_CSS, S6_HTML,  'P-01/dark'),
]

# ================================================================ pipeline
def norm(s): return ' '.join((s or '').replace('\u00A0',' ').split())

def run(only=()):
    man  = json.loads((LOCK/'canonical-lockups.json').read_text())
    recs = {r['canonical_lockup_id']: r for r in man['records']}
    seal_sha = man['canonical_seal_sha256']
    pngs, records, qa_all = [], [], {}
    ok_all = True
    for num, name, css, html, lid in SLIDES:
        if only and num not in only: continue
        src = SRC/f'{num}.html'
        if '--css' in sys.argv or not src.exists():
            src.write_text(render_html(css, html), encoding='utf-8')
        png = EXPORT/f'{num}.png'
        if png.exists(): png.unlink()
        t0=time.time()
        shot(src.as_uri(), png, 'screenshot')
        if not png.exists(): raise RuntimeError(f'render failed: {num}')
        qa_src = SRC/f'.qa-{num}.html'
        qa_src.write_text(render_html(css, html, qa_mode=True), encoding='utf-8')
        dom = shot(qa_src.as_uri(), None, 'dom')
        qa_src.unlink()
        m = re.search(r'<pre id="qa-result">(.*?)</pre>', dom, re.S)
        if not m: raise RuntimeError(f'qa harness produced no output: {num}')
        qa = json.loads(m.group(1).replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&quot;','"'))
        # exact-copy validation
        import html as _h
        claims, mism = [], []
        for c in qa.get('copy', []):
            claim = norm(_h.unescape(c['claim'])); visible = norm(_h.unescape(c['visible']))
            claims.append(claim)
            if visible != claim: mism.append({'claim': claim, 'visible': visible})
        from collections import Counter
        want, got = Counter(COPY[num]), Counter(claims)
        missing = list((want - got).elements()); extra = list((got - want).elements())
        copy_ok = not missing and not extra and not mism
        geo_ok = not qa['errors']
        ok_all &= copy_ok and geo_ok
        qa_all[num] = {'slide': name, 'geometry_ok': geo_ok, 'copy_ok': copy_ok, 'jost_loaded': qa.get('jostLoaded', False),
                       'metrics': qa.get('metrics', {}),
                       'errors': qa['errors'], 'copy_missing': missing, 'copy_extra': extra,
                       'copy_mismatch': mism, 'rects': qa['rects']}
        print(f"[{num}] {name:28s} geometry:{'PASS' if geo_ok else 'FAIL'} copy:{'PASS' if copy_ok else 'FAIL'} "
              f"({time.time()-t0:.1f}s) errors={len(qa['errors'])}")
        for e in qa['errors'][:8]: print('     !', e)
        pngs.append(png)
        rec = {'file': png.name, 'sha256': sha(png), 'source_html': f'source/{num}.html',
               'dimensions': [1080,1350]}
        if lid: rec.update({'canonical_lockup_id': lid,
                            'canonical_lockup_sha256': recs[lid]['sha256'],
                            'canonical_seal_sha256': seal_sha})
        records.append(rec)
    # contact sheet + mobile previews (always reflect the complete six-slide set)
    if only:
        pngs = sorted(EXPORT.glob('*.png'))
    if pngs:
        contact_sheet(pngs, APP/'contact-sheet.png')
        for p in pngs:
            im = Image.open(p).convert('RGB'); w=375; h=round(im.height*w/im.width)
            im.resize((w,h), Image.LANCZOS).save(MOB/p.name, optimize=True)
        tiles=[]; th=0
        for p_ in pngs:
            im = Image.open(p_).convert('RGB'); w=375; h=round(im.height*w/im.width)
            im = im.resize((w,h), Image.LANCZOS); tiles.append(im); th=max(th,h)
        strip = Image.new('RGB',(2*375+18, 3*th+4*8),(29,32,39))
        for i,im in enumerate(tiles):
            strip.paste(im,(8 + (i%2)*(375+8), 8 + (i//2)*(th+8)))
        strip.save(MOB/'mobile-strip.png')
    report = {'campaign':'BURS DOSYASI / 001 — GKS 2027','generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
              'slides': qa_all, 'overall_ok': ok_all}
    (QA/'geometry-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (APP/'render-records.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print('OVERALL', 'PASS' if ok_all else 'FAIL')
    return ok_all

import re  # noqa: E402

if __name__ == '__main__':
    only = tuple(a.lstrip('-') for a in sys.argv[1:] if a.lstrip('-').isdigit())
    sys.exit(0 if run(only) else 1)

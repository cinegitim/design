"""Build an exploratory, five-frame Instagram carousel in the visual language of a field dossier."""
from pathlib import Path
import json, shutil, hashlib, subprocess, tempfile, os, signal, time
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[4]
APP=Path(__file__).resolve().parent
OUT=ROOT/'docs/instagram/discovery-01'
AS=OUT/'assets'; SRC=OUT/'source'
AS.mkdir(parents=True,exist_ok=True); SRC.mkdir(parents=True,exist_ok=True)
LOCK=ROOT/'brands/asyada-egitim/assets/lockups'
lm=json.loads((LOCK/'canonical-lockups.json').read_text())
records={r['canonical_lockup_id']:r for r in lm['records']}
subprocess.run(['python3',str(ROOT/'studio/tools/verify_asyada_canonical_lockups.py')],check=True,stdout=subprocess.DEVNULL)
shutil.copy2(ROOT/records['P-01/light']['canonical_file_path'],AS/'p01-light.svg')
shutil.copy2(ROOT/records['P-01/dark']['canonical_file_path'],AS/'p01-dark.svg')
font=ROOT/'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf'
shutil.copy2(font,AS/'Jost-VF.ttf')
plates=ROOT/'brands/asyada-egitim/applications/instagram-carousel-01-v2/plates'
for src,name in [(next((plates/'01-social').glob('*.png')),'students.png'),(next((plates/'03-city').glob('*.png')),'study-worlds.png'),(next((plates/'04-paths').glob('*.png')),'campus.png')]:
 shutil.copy2(src,AS/name)

# Field-note visual grammar: numbered editorial sections, measured rules, filing labels,
# cropped documentary-style illustrations and handwritten-style annotation cues, without maps/flags/icons.
CSS='''
@font-face{font-family:Jost;src:url(../assets/Jost-VF.ttf);font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px;overflow:hidden}
body{font-family:Jost,Arial,sans-serif}.page{position:relative;width:1080px;height:1350px;overflow:hidden;padding:56px 64px}
.paper{background:#F7F3E9;color:#1D2027}.ink{background:#1D2027;color:#F7F3E9}.red{background:#BD2120;color:#F7F3E9}.s3:before{content:"";position:absolute;z-index:4;top:30px;right:52px;width:374px;height:374px;background:#1D2027}
.logo{position:absolute;z-index:10;top:46px;right:64px;width:352px;height:auto}
.kicker{font-size:23px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;line-height:1.2}
.redink{color:#BD2120}.paper .redink{color:#BD2120}.ink .redink,.red .redink{color:#BD2120}
.rule{height:2px;background:#1D2027}.paper .rule{background:#1D2027}.ink .rule{background:#F7F3E9}.red .rule{background:#F7F3E9}
.folio{position:absolute;right:64px;bottom:38px;font-size:22px;font-weight:700;letter-spacing:.12em}
.headline{font-weight:700;letter-spacing:-.055em;line-height:.93;text-wrap:balance;margin:0}
.photo{position:absolute;object-fit:cover;filter:saturate(.78) contrast(1.02)}
.stamp{display:inline-block;border:2px solid currentColor;padding:8px 12px;font-size:18px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;transform:rotate(-2deg)}
.index{font-size:19px;font-weight:700;letter-spacing:.12em}.annotation{font-size:22px;line-height:1.35;font-weight:500}
.hatch{background-image:repeating-linear-gradient(135deg,transparent 0 9px,#1D20271a 9px 11px)}
/* 01 / cover */
.s1 .kicker{position:absolute;left:64px;top:62px;width:450px}.s1 .section{position:absolute;left:64px;top:540px;color:#BD2120}
.s1 .headline{position:absolute;left:64px;top:592px;width:650px;font-size:112px}.s1 .headline em{font-style:normal;color:#BD2120}
.s1 .sub{position:absolute;left:68px;top:865px;width:560px;font-size:30px;line-height:1.22;font-weight:550}
.s1 .photo{left:650px;top:500px;width:430px;height:470px;object-position:center 48%;border-left:12px solid #BD2120}
.s1 .sidecode{position:absolute;right:66px;top:1000px;writing-mode:vertical-rl;font-size:17px;letter-spacing:.15em;font-weight:650}
/* 02 / range */
.s2 .kicker{position:absolute;left:64px;top:462px;color:#BD2120}
.s2 .headline{position:absolute;left:64px;top:510px;width:770px;font-size:91px}
.s2 .country-list{position:absolute;left:64px;top:815px;width:670px;display:grid;grid-template-columns:1fr 1fr;column-gap:28px}
.s2 .country{height:72px;border-top:2px solid #F7F3E9;display:flex;align-items:center;gap:20px;font-size:33px;font-weight:600}
.s2 .country small{font-size:17px;color:#BD2120;letter-spacing:.1em;font-weight:700}
.s2 .photo{right:0;top:740px;width:300px;height:340px;object-position:center;opacity:.8;border:8px solid #F7F3E9}
.s2 .note{position:absolute;left:64px;top:1190px;width:650px;font-size:23px;color:#F7F3E9b8}
/* 03 / goals */
.s3 .kicker{position:absolute;left:64px;top:475px;color:#F7F3E9}
.s3 .headline{position:absolute;left:64px;top:525px;width:580px;font-size:72px}
.s3 .target-list{position:absolute;left:64px;right:64px;top:850px;display:grid;grid-template-columns:1fr 1fr;gap:0 32px}
.s3 .target{min-height:80px;border-top:2px solid #F7F3E9;display:flex;align-items:center;gap:18px;font-size:30px;font-weight:600}
.s3 .target b{font-size:19px;font-weight:700;letter-spacing:.1em;color:#F7F3E9}
.s3 .note{position:absolute;left:64px;top:1085px;font-size:23px;max-width:730px;line-height:1.35}
/* 04 / method */
.s4 .kicker{position:absolute;left:64px;top:475px;color:#BD2120}
.s4 .headline{position:absolute;left:64px;top:525px;width:640px;font-size:84px}
.s4 .photo{right:0;top:690px;width:425px;height:400px;object-position:center 56%;border-left:10px solid #BD2120}
.s4 .steps{position:absolute;left:64px;top:795px;width:535px}
.s4 .step{display:grid;grid-template-columns:58px 1fr;align-items:start;padding:17px 0;border-top:2px solid #1D2027}
.s4 .step b{font-size:23px;color:#BD2120}.s4 .step span{font-size:28px;line-height:1.12;font-weight:600}
.s4 .annotation{position:absolute;left:64px;top:1115px;width:560px;font-size:21px}
/* 05 / invitation */
.s5 .kicker{position:absolute;left:64px;top:470px;color:#BD2120}
.s5 .headline{position:absolute;left:64px;top:525px;width:820px;font-size:104px}
.s5 .headline em{font-style:normal;color:#BD2120}
.s5 .cta{position:absolute;left:64px;top:895px;border:2px solid #BD2120;color:#F7F3E9;padding:18px 24px;font-size:30px;font-weight:650}
.s5 .annotation{position:absolute;left:64px;top:1000px;width:700px;font-size:25px}
.s5 .photo{right:0;bottom:135px;width:360px;height:220px;opacity:.6;object-position:center}
@media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''

SLIDES=[
 ('01-cover','paper','P-01/light','''<div class="kicker">ASYA’DA EĞİTİM　/　KEŞİF SERİSİ</div><div class="section index">SAHA DEFTERİ　·　01</div><h1 class="headline">Eğitim için<br><em>yeni bir yön.</em></h1><p class="sub">Bir ülke adıyla değil,<br>merak ettiğin gelecekle başla.</p><img class="photo" src="../assets/students.png"><div class="sidecode">KEŞİF　/　01</div>'''),
 ('02-worlds','ink','P-01/dark','''<div class="kicker">DOSYA 01　/　OLASILIKLAR</div><h1 class="headline">Beş ülke.<br><span class="redink">Birçok</span><br>başlangıç.</h1><div class="country-list"><div class="country"><small>01</small>Çin</div><div class="country"><small>02</small>Japonya</div><div class="country"><small>03</small>Güney Kore</div><div class="country"><small>04</small>Singapur</div><div class="country"><small>05</small>Hong Kong</div></div><img class="photo" src="../assets/study-worlds.png"><div class="note">Aynı rota herkese uymaz. Seçenekleri hedefinle birlikte düşün.</div>'''),
 ('03-goals','red','P-01/dark','''<div class="kicker">DOSYA 02　/　EĞİTİM HEDEFİ</div><h1 class="headline">Önce<br>ne öğrenmek<br>istediğini<br>keşfet.</h1><div class="target-list"><div class="target"><b>01</b>Lisans</div><div class="target"><b>02</b>Yüksek lisans</div><div class="target"><b>03</b>Dil programı</div><div class="target"><b>04</b>Yaz okulu</div></div><p class="note">Başlangıç noktası senin hedefin.</p>'''),
 ('04-route','paper','P-01/light','''<div class="kicker">DOSYA 03　/　KENDİ ROTAN</div><h1 class="headline">Kararı<br>hedefinle<br>başlat.</h1><div class="steps"><div class="step"><b>01</b><span>İlgi alanını<br>belirle</span></div><div class="step"><b>02</b><span>Eğitim hedefini<br>netleştir</span></div><div class="step"><b>03</b><span>Sana uyan seçenekleri<br>birlikte değerlendir</span></div></div><img class="photo" src="../assets/campus.png"><p class="annotation">Kişisel hedeflerinden başlayan bir keşif.</p>'''),
 ('05-cta','ink','P-01/dark','''<div class="kicker">KEŞİF SERİSİ　/　SONRAKİ ADIM</div><h1 class="headline">Merakın<br>bir <em>rotaya</em><br>dönüşsün.</h1><div class="cta">ÖN GÖRÜŞMENİ PLANLA　↗</div><p class="annotation">Asya’da eğitim seçeneklerini<br>birlikte konuşalım.</p><img class="photo" src="../assets/students.png">''')
]

CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
exported=[]
for n,(name,bg,lid,markup) in enumerate(SLIDES,1):
 logo='p01-light.svg' if lid.endswith('light') else 'p01-dark.svg'
 html=f'''<!doctype html><html lang="tr"><meta charset="utf-8"><style>{CSS}</style><body><main class="page {bg} s{n}"><img class="logo" src="../assets/{logo}">{markup}<div class="folio">{n:02}　/　05</div></main></body></html>'''
 src=SRC/f'{n:02}.html';src.write_text(html)
 png=OUT/f'{name}.png'
 if png.exists():png.unlink()
 with tempfile.TemporaryDirectory(prefix='ig-discovery-',dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as prof:
  proc=subprocess.Popen([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--force-device-scale-factor=1','--window-size=1080,1350','--virtual-time-budget=1800',f'--user-data-dir={prof}',f'--screenshot={png}',src.as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
  deadline=time.monotonic()+35
  while time.monotonic()<deadline and proc.poll() is None:
   if png.exists() and png.stat().st_size>10000:break
   time.sleep(.25)
  if proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=4)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
 if not png.exists():raise RuntimeError(f'Failed render: {png}')
 exported.append((n,name,lid,png,src))

contact=Image.new('RGB',(5*216,270),'#D8D2C7')
for j,(_,_,_,p,_) in enumerate(exported):
 im=Image.open(p).convert('RGB');im.thumbnail((210,262));contact.paste(im,(j*216,4))
contact.save(OUT/'sequence.jpg',quality=94)
slides=[]
for n,name,lid,p,src in exported:
 slides.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_html':str(src.relative_to(OUT)),'canonical_lockup_id':lid,'canonical_lockup_sha256':records[lid]['sha256'],'canonical_logo_sha256':lm['canonical_seal_sha256'],'canonical_seal_sha256':lm['canonical_seal_sha256']})
manifest={'campaign':'Keşif Defteri — Asya’da Eğitim','concept':'Field-dossier / annotated editorial discovery series; visually distinct from earlier photo-led, headline-block carousels.','status':'EXPLORATORY — HUMAN APPROVAL PENDING','dimensions':[1080,1350],'visual_tokens':{'paper':'#F7F3E9','ink':'#1D2027','red':'#BD2120','type':'Jost','grid':'64px editorial margin; numbered dossier sections; ruled data tables; crop apertures','logo':'Exact P-01 primary lockup at 352px (approved minimum), stable upper-right position.'},'imagery_note':'Illustrative AI-generated campaign photography reused from prior inspected plates; not documentary imagery of named campuses or destinations.','slides':slides}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

files=[p.name for _,_,_,p,_ in exported]
html=f'''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Keşif Defteri · Asya’da Eğitim</title><style>@font-face{{font-family:Jost;src:url(assets/Jost-VF.ttf);font-weight:100 900}}*{{box-sizing:border-box}}body{{margin:0;background:#d8d2c7;color:#1d2027;font:16px/1.55 Jost,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(42px,7vw,74px);line-height:1.02;margin:0}}.lead{{font-size:20px;max-width:800px}}.mock{{display:grid;grid-template-columns:390px 1fr;gap:28px;align-items:start}}.phone{{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 16px 48px #1d202733}}.bar{{padding:13px 16px;border-bottom:1px solid #ddd;display:flex;justify-content:space-between}}.post{{display:block;width:100%;aspect-ratio:4/5;object-fit:cover}}.controls{{display:flex;justify-content:space-between;align-items:center;padding:8px 14px}}button{{font:inherit;font-size:24px;border:0;border-radius:50%;width:44px;height:44px;cursor:pointer}}.thumbs{{display:grid;grid-template-columns:repeat(5,1fr);gap:5px}}.thumbs img{{width:100%;aspect-ratio:4/5;object-fit:cover;cursor:pointer}}.thumbs img.on{{outline:3px solid #bd2120;outline-offset:-3px}}.strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:28px 0}}.strip img{{width:100%;display:block}}.sourcegrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:34px 0}}.sourcegrid img{{width:100%;display:block;aspect-ratio:4/5;object-fit:cover}}.note{{font-size:14px;color:#514b43}}@media(max-width:760px){{header,main{{padding:18px}}.mock{{grid-template-columns:1fr}}.phone{{max-width:390px;margin:auto}}.thumbs{{grid-template-columns:repeat(3,1fr)}}.strip{{grid-template-columns:repeat(2,1fr)}}.sourcegrid{{grid-template-columns:1fr}}}}</style><header><p style="letter-spacing:.15em;color:#bd2120;font-weight:700">ASYA’DA EĞİTİM　/　KEŞİF SERİSİ</p><h1>Keşif Defteri</h1><p class="lead">Önceki görsel kalıptan bilinçli biçimde ayrılan, saha dosyası / editoryal notlar yaklaşımı. Renkli tam zeminli posterler yerine numaralı dosyalar, kenar notları, kayıt çizgileri ve fotoğraf pencereleriyle ilerliyor. Bu bir konsept denemesidir; Instagram’da yayınlanmadı.</p></header><main><div class="mock"><section class="phone"><div class="bar"><span>‹</span><b>Gönderiler</b><span>•••</span></div><div class="bar"><b>asyadaegitim</b><span>•••</span></div><img class="post" id="active" src="{files[0]}"><div class="controls"><button id="prev">‹</button><b id="count">1 / 5</b><button id="next">›</button></div><div style="padding:14px"><b>asyadaegitim</b> Keşif Defteri.<p class="note">Görseller atmosfer amaçlı yapay zekâ üretimidir; belirli kampüs veya ülkelerin belgesel görüntüsü değildir.</p></div></section><section><h2>Profil ızgarası</h2><div class="thumbs" id="thumbs"></div><p class="note">Yaklaşık Instagram gönderi simülasyonu, 1080 × 1350 px (4:5). Carousel okları veya küçük görsellerle gezin.</p><h2>Beş sayfalık akış</h2><div class="strip">{''.join(f'<img src="{f}">' for f in files)}</div><a href="manifest.json">Kanonik logo ve dosya manifestosu</a> · <a href="sequence.jpg">Kontak sayfası</a></section></div><h2>Düzenlenebilir kaynakların önizlemesi</h2><div class="sourcegrid">{''.join(f'<article><img src="{f}"><a href="source/{i:02}.html">{i:02} · HTML/CSS kaynağı</a></article>' for i,f in enumerate(files,1))}</div></main><script>const f={json.dumps(files)};let i=0;function go(n){{i=(n+5)%5;document.getElementById('active').src=f[i];document.getElementById('count').textContent=(i+1)+' / 5';document.querySelectorAll('.thumbs img').forEach((e,j)=>e.classList.toggle('on',j===i))}}document.getElementById('prev').onclick=()=>go(i-1);document.getElementById('next').onclick=()=>go(i+1);document.getElementById('thumbs').innerHTML=f.map((x,j)=>`<img src="${{x}}" onclick="go(${{j}})" alt="Slayt ${{j+1}}">`).join('');go(0)</script></html>'''
(OUT/'index.html').write_text(html)
print('Built discovery-01: 5 slides')

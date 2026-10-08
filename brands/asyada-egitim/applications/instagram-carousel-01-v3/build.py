from pathlib import Path
import json, shutil, hashlib, subprocess, tempfile, os, signal, time
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
APP=Path(__file__).resolve().parent
LOCK=ROOT/'brands/asyada-egitim/assets/lockups'
MANIFEST=json.loads((LOCK/'canonical-lockups.json').read_text())
RECORDS={r['canonical_lockup_id']:r for r in MANIFEST['records']}
subprocess.run(['python3',str(ROOT/'studio/tools/verify_asyada_canonical_lockups.py')],check=True,stdout=subprocess.DEVNULL)
FONT=ROOT/'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf'
PLATES=ROOT/'brands/asyada-egitim/applications/instagram-carousel-01-v2/plates'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PALETTE={'paper':'#F7F3E9','ink':'#1D2027','red':'#BD2120','white':'#FFFFFF'}

SETS={
 'carousel-01-v3':{
  'title':'Başka bir dünya var','concept':'Önceki serinin yeniden tasarımı: daha büyük mesaj, değişen marka zeminleri, editoryal fotoğraf ritmi.',
  'slides':[
    ('01-cover','red','dark','<div class="eyebrow white">YURTDIŞI EĞİTİMDE YENİ ROTALAR</div><h1 class="cover white">Üniversite için<br><em>başka bir dünya</em><br>var.</h1><div class="cover-rule"></div><img class="photo hero-friends" src="../assets/photo-1.png">'),
   ('02-shift','paper','light','<div class="eyebrow red">01 — BAKIŞ AÇISI</div><h1 class="big">Yurtdışı eğitim<br>hep aynı yerler<br><em>mi demek?</em></h1><p class="dek">Alışılmış rotaların ötesine bak.</p><img class="photo door" src="../assets/photo-2.png">'),
   ('03-routes','ink','dark','<div class="eyebrow white">02 — YENİ ROTALAR</div><h1 class="big white">Başka bir dünya.<br><em>Birden fazla rota.</em></h1><div class="country-grid"><b>Çin</b><b>Japonya</b><b>Güney Kore</b><b>Singapur</b><b>Hong Kong</b></div><img class="photo city" src="../assets/photo-3.png">'),
   ('04-pathways','paper','light','<div class="eyebrow red">03 — SANA UYGUN YOL</div><h1 class="big">Kendine uygun<br><em>yolu bul.</em></h1><img class="photo study" src="../assets/study.jpg"><img class="photo campus" src="../assets/campus.jpg"><div class="options"><span>Lisans</span><span>Yüksek lisans</span><span>Dil programları</span><span>Yaz okulları</span></div>'),
   ('05-cta','ink','dark','<div class="eyebrow red">İLK ADIMI AT</div><h1 class="big white">Senin rotan<br><em>nerede başlıyor?</em></h1><div class="country-line white">Çin · Japonya · Güney Kore<br>Singapur · Hong Kong</div><div class="cta-pill">Ücretsiz ön görüşme</div><p class="dek white">Profildeki bağlantıyı ziyaret et.</p>')
  ]},
 'carousel-02':{
  'title':'Sınırların dışında düşün','concept':'Yeni beşli: büyük ölçekli editoryal sorular ve karşıt marka renkleriyle, keşiften danışma çağrısına ilerleyen bir rota.',
  'slides':[
   ('01-cover','ink','dark','<div class="eyebrow red">EĞİTİMDE YENİ BİR YÖN</div><h1 class="cover white">Dünya<br><em>dersliğin</em><br>olabilir.</h1><div class="cover-rule"></div><img class="photo hero-door" src="../assets/photo-2.png">'),
    ('02-question','red','dark','<div class="eyebrow white">BİR SORUYLA BAŞLA</div><h1 class="question white">Nereye<br>gideceğini değil.<br><em>Nedenini.</em></h1><div class="question-bottom white">Ne öğrenmek, nasıl bir gelecek kurmak istiyorsun?</div><img class="photo question-photo" src="../assets/photo-1.png">'),
   ('03-countries','paper','light','<div class="eyebrow red">BEŞ FARKLI EĞİTİM DÜNYASI</div><h1 class="big">Bir ülkeye<br>sığmayan<br><em>seçenekler.</em></h1><div class="country-list"><span>Çin</span><span>Japonya</span><span>Güney Kore</span><span>Singapur</span><span>Hong Kong</span></div><img class="photo city" src="../assets/photo-3.png">'),
   ('04-pathways','red','dark','<div class="eyebrow white">YOLUN SANA AİT</div><h1 class="big white">Her hedefin<br>kendi <em>yolu.</em></h1><img class="photo study" src="../assets/study.jpg"><div class="pathways"><span>01　Lisans</span><span>02　Yüksek lisans</span><span>03　Dil programı</span><span>04　Yaz okulu</span></div>'),
   ('05-cta','paper','light','<div class="eyebrow red">SIRADAKİ ADIM</div><h1 class="closing">Bir sonraki<br>büyük adımın<br><em>burada</em><br>başlayabilir.</h1><img class="photo closing-photo" src="../assets/campus.jpg"><div class="cta-pill">Birlikte keşfedelim</div><p class="dek">İlk adım: tanışma görüşmesi.</p>')
  ]}
}

CSS='''@font-face{font-family:Jost;src:url(../assets/Jost-VF.ttf);font-weight:100 900}*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px;overflow:hidden}body{font-family:Jost,Arial,sans-serif}.slide{position:relative;width:1080px;height:1350px;overflow:hidden;padding:58px 64px}.paper{background:#F7F3E9;color:#1D2027}.ink{background:#1D2027;color:#F7F3E9}.red{background:#BD2120;color:#1D2027}.white{color:#F7F3E9!important}.slide.red em{color:#F7F3E9}.eyebrow{position:relative;z-index:3;font-size:36px;font-weight:650;letter-spacing:.1em}.eyebrow.red{background:none;color:#BD2120}.eyebrow.white{background:none;color:#F7F3E9}.big,.cover,.question,.closing{position:relative;z-index:2;margin:55px 0 0;font-weight:650;letter-spacing:-.055em;line-height:.98;text-wrap:balance}.big{font-size:83px}.cover{font-size:93px;max-width:950px;margin-top:45px}.question{font-size:121px;margin-top:50px;line-height:.88}.closing{font-size:91px;margin-top:47px}em{font-style:normal;color:#BD2120}.white em{color:#F7F3E9}.dek{position:relative;z-index:3;font-size:42px;font-weight:550;line-height:1.15;margin:28px 0}.cover-rule{position:absolute;z-index:2;left:64px;top:573px;width:320px;height:8px;background:#F7F3E9}.photo{position:absolute;object-fit:cover}.hero-friends{left:0;top:590px;width:1080px;height:760px;object-position:center 51%}.hero-door{left:0;top:590px;width:1080px;height:760px;object-position:center 56%}.door{right:0;top:370px;width:480px;height:690px;object-position:center}.country-grid{position:absolute;z-index:2;left:64px;top:405px;width:520px;display:grid;grid-template-columns:1fr 1fr;gap:12px}.country-grid b{font-size:42px;font-weight:600;border-top:2px solid #F7F3E9;padding-top:12px}.city{left:610px;top:430px;width:470px;height:620px;opacity:.86}.country-grid b:last-child{grid-column:1}.study{left:0;top:390px;width:650px;height:330px}.campus{right:0;top:430px;width:375px;height:290px}.options{position:absolute;left:64px;right:64px;top:750px;display:grid;grid-template-columns:1fr 1fr;border-top:4px solid #BD2120}.options span{padding:8px 0;font-size:44px;font-weight:600;border-bottom:1px solid #a9a398}.country-line{position:relative;z-index:3;font-size:38px;line-height:1.45;font-weight:550;margin-top:52px}.cta-pill{position:relative;z-index:3;display:inline-block;background:#BD2120;color:#F7F3E9;font-size:44px;font-weight:650;padding:20px 26px;margin-top:36px}.ink .cta-pill,.paper .cta-pill{background:#BD2120;color:#F7F3E9}.country-list{position:absolute;z-index:2;left:64px;top:475px;width:440px;display:grid}.country-list span{font-size:42px;font-weight:600;padding:11px 0;border-bottom:2px solid #1D2027}.question-bottom{position:absolute;z-index:3;left:64px;top:520px;font-size:54px;font-weight:600;line-height:1.04}.question-photo{right:0;bottom:0;width:520px;height:650px;object-position:center}.pathways{position:absolute;z-index:2;left:64px;top:740px;display:grid;grid-template-columns:1fr 1fr;gap:8px;width:900px}.pathways span{font-size:42px;font-weight:600;padding:9px 0;border-top:2px solid #F7F3E9}.red .pathways{color:#F7F3E9}.red .study{height:330px}.closing-photo{right:0;top:515px;width:470px;height:530px}.closing .dek{font-size:35px}.country-list~.city{left:550px;top:500px;width:530px;height:570px}.dark .eyebrow{color:#BD2120}@media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}'''

for slug,data in SETS.items():
 out=ROOT/'docs/instagram'/slug; assets=out/'assets'; source=out/'source'; assets.mkdir(parents=True,exist_ok=True);source.mkdir(parents=True,exist_ok=True)
 shutil.copy2(FONT,assets/'Jost-VF.ttf')
 for lid,file in [('P-01/light','p01-light.svg'),('P-01/dark','p01-dark.svg')]:shutil.copy2(ROOT/RECORDS[lid]['canonical_file_path'],assets/file)
 for n,p in enumerate(['01-social','02-door','03-city','04-paths'],1):shutil.copy2(next((PLATES/p).glob('*.png')),assets/f'photo-{n}.png')
 # Reuse source imagery as photography only; never use the generated typography/marks from an existing composite.
 from PIL import Image as PILImage
 im=PILImage.open(assets/'photo-4.png').convert('RGB'); im.crop((24,20,1000,735)).save(assets/'study.jpg',quality=95); im.crop((345,740,1000,1510)).save(assets/'campus.jpg',quality=95)
 slides=[]
 for idx,(name,bg,lid,markup) in enumerate(data['slides'],1):
  logo='p01-light.svg' if lid=='light' else 'p01-dark.svg'
  # Consistent 380px P-01 primary lockup on every slide, in a brand-safe contrasting footer field.
  bgclass=bg
  footclass='ink' if bgclass=='red' else bgclass
  footer=f'<div class="logo-foot {footclass}"><img src="../assets/{logo}"></div>'
  slide_markup=markup+footer+f'<div class="folio">{idx:02}/05</div>'
  html=f'<!doctype html><html lang="tr"><meta charset="utf-8"><style>{CSS}.logo-foot{{position:absolute;z-index:4;left:0;bottom:0;width:100%;height:425px;display:flex;align-items:flex-end;padding:0 64px 22px}}.logo-foot img{{width:380px;height:auto;display:block}}.folio{{position:absolute;z-index:5;right:64px;bottom:43px;font-size:34px;font-weight:700;color:{"#F7F3E9" if lid=="dark" else "#BD2120"}}}</style><body><main class="slide {bg}">{slide_markup}</main></body></html>'
  src=source/f'{idx:02}.html';src.write_text(html)
  png=out/f'{name}.png'
  if png.exists():png.unlink()
  with tempfile.TemporaryDirectory(prefix='igcarousel-',dir='/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode') as prof:
   proc=subprocess.Popen([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run','--force-device-scale-factor=1','--window-size=1080,1350','--virtual-time-budget=1800',f'--user-data-dir={prof}',f'--screenshot={png}',src.as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
   deadline=time.monotonic()+25
   while time.monotonic()<deadline and proc.poll() is None:
    if png.exists() and png.stat().st_size>10000:break
    time.sleep(.25)
   if proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=4)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
  if not png.exists():raise RuntimeError(f'No rendered PNG: {png}')
  slides.append((idx,name,lid,png,src))
 strip=Image.new('RGB',(5*216,270),'#D8D2C7')
 for j,(_,_,_,png,_) in enumerate(slides):
  im=Image.open(png).convert('RGB');im.thumbnail((210,262));strip.paste(im,(j*216,4))
 strip.save(out/'sequence.jpg',quality=92)
 records=[]
 for idx,name,lid,png,src in slides:
  canonical='P-01/'+lid;records.append({'file':png.name,'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'source_html':str(src.relative_to(out)),'canonical_lockup_id':canonical,'canonical_lockup_sha256':RECORDS[canonical]['sha256'],'canonical_seal_sha256':MANIFEST['canonical_seal_sha256']})
 manifest={'campaign':data['title'],'concept':data['concept'],'status':'HUMAN APPROVAL PENDING','dimensions':[1080,1350],'brand_tokens':{'paper':PALETTE['paper'],'ink':PALETTE['ink'],'red':PALETTE['red'],'type':'Jost','lockup':'P-01 primary stacked, 380px wide on all five slides'},'imagery':'Previously generated campaign imagery reused as illustrative photography; not documentary evidence of named campuses. AI imagery disclosed on review page.','slides':records}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 # Editable master overview for this five-slide set.
 cards=''.join(f'<article><h2>{i:02}. {name}</h2><img src="{name}.png" alt="{name}"><a href="source/{i:02}.html">Düzenlenebilir HTML/CSS</a> · <a href="{name}.png">PNG 1080 × 1350</a></article>' for i,(name,_,_,_,_) in enumerate(slides,1))
 index=f'''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']} · Instagram</title><style>@font-face{{font-family:Jost;src:url(assets/Jost-VF.ttf);font-weight:100 900}}*{{box-sizing:border-box}}body{{margin:0;background:#D8D2C7;color:#1D2027;font:16px/1.5 Jost,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(42px,7vw,76px);line-height:1.02;margin:0}}.intro{{font-size:20px;max-width:760px}}.mock{{display:grid;grid-template-columns:390px 1fr;gap:28px;align-items:start}}.phone{{background:white;border-radius:22px;overflow:hidden;box-shadow:0 16px 48px #1d202733}}.bar{{padding:14px 17px;border-bottom:1px solid #ddd;display:flex;justify-content:space-between}}.post{{width:100%;aspect-ratio:4/5;object-fit:cover;display:block}}.caption{{padding:14px}}.controls{{display:flex;justify-content:space-between;align-items:center;padding:8px 14px}}button{{font:inherit;font-size:23px;border:0;border-radius:50%;width:44px;height:44px;cursor:pointer}}.thumbs{{display:grid;grid-template-columns:repeat(5,1fr);gap:5px}}.thumbs img{{width:100%;aspect-ratio:4/5;object-fit:cover;cursor:pointer}}.thumbs img.on{{outline:3px solid #BD2120;outline-offset:-3px}}.strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:30px 0}}.strip img{{width:100%;display:block}}.disclosure{{font-size:14px;color:#514b43}}.sources{{display:grid;grid-template-columns:repeat(2,minmax(300px,1fr));gap:20px}}article iframe{{width:100%;aspect-ratio:4/5;border:0;background:white}}.sources img{{width:100%;aspect-ratio:4/5;object-fit:cover}}article h2{{font-size:18px}}@media(max-width:780px){{.mock{{grid-template-columns:1fr}}.phone{{max-width:390px;margin:auto}}.thumbs{{grid-template-columns:repeat(3,1fr)}}.strip{{grid-template-columns:repeat(2,1fr)}}.sources{{grid-template-columns:1fr}}}}</style><header><p style="color:#BD2120;font-weight:700;letter-spacing:.12em">ASYA’DA EĞİTİM · BEŞLİ KAMPANYA</p><h1>{data['title']}</h1><p class="intro">{data['concept']}</p></header><main><div class="mock"><section class="phone"><div class="bar"><span>‹</span><b>Gönderiler</b><span>•••</span></div><div class="bar"><b>asyadaegitim</b><span>•••</span></div><img id="active" class="post" src="{slides[0][1]}.png"><div class="controls"><button id="prev">‹</button><b id="count">1 / 5</b><button id="next">›</button></div><div class="caption"><b>asyadaegitim</b> {data['title']}.<p class="disclosure">İllüstratif kampanya görselleri. Gerçek kampüs fotoğrafı olarak sunulmamaktadır.</p></div></section><section><h2>Profil ızgarası simülasyonu</h2><div id="thumbs" class="thumbs"></div><p class="disclosure">Yaklaşık Instagram gönderi arayüzüdür; platform ekran görüntüsü değildir. 1080 × 1350 gönderi oranı (4:5). Carousel’i gezinmek için okları veya küçük görselleri kullanın.</p><h2>Seri ritmi</h2><div class="strip">{''.join(f'<img src="{s[1]}.png">' for s in slides)}</div><a href="manifest.json">Asset ve kanonik logo manifestosu</a> · <a href="sequence.jpg">Kontak sayfası</a></section></div><h2>Slayt kaynakları</h2><div class="sources">{cards}</div></main><script>const files={json.dumps([s[1]+'.png' for s in slides])};let i=0;function set(n){{i=(n+5)%5;document.getElementById('active').src=files[i];document.getElementById('count').textContent=(i+1)+' / 5';document.querySelectorAll('.thumbs img').forEach((e,j)=>e.classList.toggle('on',j===i))}}document.getElementById('prev').onclick=()=>set(i-1);document.getElementById('next').onclick=()=>set(i+1);document.getElementById('thumbs').innerHTML=files.map((f,j)=>`<img src="${{f}}" onclick="set(${{j}})" alt="Slide ${{j+1}}">`).join('');set(0)</script></html>'''
 (out/'index.html').write_text(index)
 print(f'Built {slug}: {len(slides)} slides')

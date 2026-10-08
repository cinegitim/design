#!/usr/bin/env python3
"""Revision 02: faithfully retain art direction; individually typeset every slide.

Run with PLAYWRIGHT_MODULE pointing to an installed playwright-core module,
or install it normally. CHROME_PATH optionally specifies the browser executable.
The SVGs embed the Jost font and link verbatim canonical SVGs and original imagery.
"""
from pathlib import Path
import base64, hashlib, html, json, shutil, subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPER, INK, RED = '#F7F3E9', '#1D2027', '#BD2120'
CANONICAL = ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json'
ORIGINALS, SOURCE, FINAL, ASSETS = [HERE/n for n in ('originals','source','final','assets')]
LOCKUPS = ASSETS/'lockups'
SEAL_SHA = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'

# Baselines and font sizes are actual Jost dimensions: no stretched textLength,
# no wordmark substitution, no shared placement grid.
SLIDES = [
 {
  'id':'01-cover','lockup':'D-04/dark','logo_xy':[720,62],'logo_width':300,
  'copy':['Üniversite için başka bir dünya var.','Yurtdışı eğitime başka bir yerden bak.'],
  'text':[
   (74,849,48,INK,550,'Üniversite için'),
   (86,942,96,INK,720,'başka bir'),
   (156,1058,96,RED,720,'dünya var.'),
   (210,1128,29,INK,450,'Yurtdışı eğitime'),
   (210,1166,29,INK,450,'başka bir yerden bak.'),
  ],
  'layers':[],
  'note':'Compact signature is inset inside the upper-right ink aperture. Headline steps along the cream sweep, while support retreats from the lower red edge.'
 },
 {
  'id':'02-perspective','lockup':'D-04/dark','logo_xy':[698,1126],'logo_width':318,
  'copy':['Yurtdışı eğitimin tek yönü yok.','Amerika ve Avrupa, seçeneklerin tamamı değil.'],
  'text':[
   (74,147,82,INK,720,'Yurtdışı'),
   (74,239,82,INK,720,'eğitimin'),
   (74,330,80,RED,720,'tek yönü'),
   (72,443,110,INK,740,'yok.'),
   (76,502,29,INK,450,'Amerika ve Avrupa,'),
   (76,541,29,INK,450,'seçeneklerin tamamı'),
   (76,580,29,INK,450,'değil.'),
  ],
  'layers':['<image href="../assets/02-paper-cleanup.png" x="0" y="0" width="1080" height="1350"/>','<image href="../assets/02-logo-contrast.png" x="0" y="0" width="1080" height="1350"/>'],
  'note':'Headline is narrower and clears the threshold. Small Turkish-only signature moves completely off the student into a shaded, empty architectural ground plane at lower-right.'
 },
 {
  'id':'03-five-worlds','lockup':'D-04/light','logo_xy':[53,414],'logo_width':240,
  'copy':['Tek bir Asya yok.','Beş rota. Birbirinden farklı dünyalar.','Çin','Japonya','Güney Kore','Singapur','Hong Kong'],
  'text':[
   (165,562,44,INK,550,'Tek bir'),
   (165,650,80,RED,740,'Asya yok.'),
   (242,694,28,INK,550,'Beş rota.'),
   (242,737,26,INK,450,'Birbirinden farklı dünyalar.'),
   (61,137,30,INK,650,'Çin'),
   (949,332,24,INK,650,'Japonya'),
   (889,828,25,INK,650,'Güney Kore'),
   (59,1223,31,INK,650,'Singapur'),
   (658,1116,35,PAPER,650,'Hong Kong'),
  ],
  'layers':['<path d="M635 1045 L911 1045 L911 1145 L635 1145 Z" fill="url(#caption-fade)"/>'],
  'note':'The central headline uses the original paper aperture, without the generic extra note box. Country labels occupy the original photo annotations; one dark-field label sits on the Hong Kong fragment.'
 },
 {
  'id':'04-experience','lockup':'D-04/dark','logo_xy':[623,54],'logo_width':300,
  'copy':['Sadece bir üniversite seçmiyorsun.','Yeni bir şehir, yeni insanlar, yeni bir dil ve dünyaya başka bir bakış açısı.','Lisans','Yüksek Lisans','Dil Programları','Yaz Okulları'],
  'text':[
   (66,108,43,INK,550,'Sadece bir'),
   (63,170,64,INK,720,'üniversite'),
   (64,230,57,RED,720,'seçmiyorsun.'),
   (105,270,26,INK,450,'Yeni bir şehir, yeni insanlar,'),
   (105,304,25,INK,450,'yeni bir dil ve dünyaya başka'),
   (165,338,26,INK,450,'bir bakış açısı.'),
   (61,563,32,INK,650,'Lisans'),
   (820,897,28,INK,650,'Yüksek'),
   (820,933,28,INK,650,'Lisans'),
   (430,984,29,INK,650,'Dil Programları'),
   (708,1238,31,PAPER,650,'Yaz Okulları'),
  ],
  'layers':['<path d="M650 1174 L999 1174 L999 1271 L650 1271 Z" fill="url(#caption-fade)"/>'],
  'note':'All four pathways follow real annotation apertures instead of floating tags. The large intrusive lower copy card is removed; supporting copy stays with the headline, and the signature clears the edge and the study portrait.'
 },
 {
  'id':'05-invitation','lockup':'H-02/light','logo_xy':[405,580],'logo_width':560,
  'copy':['Senin rotan nerede başlıyor?','Çin · Japonya · Güney Kore · Singapur · Hong Kong','Ücretsiz ön görüşme','Profildeki bağlantıdan bize ulaş.'],
  'text':[
   (473,113,62,PAPER,650,'Senin rotan'),
   (470,189,62,PAPER,650,'nerede başlıyor?'),
   (630,835,26,INK,450,'Çin · Japonya · Güney Kore ·'),
   (630,872,26,INK,450,'Singapur · Hong Kong'),
   (474,1024,43,PAPER,650,'Ücretsiz ön görüşme'),
   (476,1070,28,PAPER,450,'Profildeki bağlantıdan bize ulaş.'),
  ],
  'layers':['<path d="M401 42 L1031 42 L1031 293 L401 293 Z" fill="url(#headline-fade)"/>','<image href="../assets/05-destinations-cleanup.png" x="0" y="0" width="1080" height="1350"/>'],
  'note':'Headline clears the skyline and remains Paper, not low-contrast red-on-night. Bilingual mark now sits wholly on the cream aperture, clear of the student silhouette. Destination line follows it; CTA and contact instruction are grouped on the dark sweep without a redundant button.'
 },
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def svg_for(s, rec):
 font = base64.b64encode((ASSETS/'Jost-VF.ttf').read_bytes()).decode()
 exact = html.escape(json.dumps(s['copy'],ensure_ascii=False),quote=True)
 texts=[]
 for x,y,size,color,weight,value in s['text']:
  tracking='-1.5' if size>=60 else '-0.2'
  texts.append(f'<text x="{x}" y="{y}" font-family="Jost" font-size="{size}" font-weight="{weight}" letter-spacing="{tracking}" fill="{color}" data-copy="{html.escape(value,quote=True)}">{html.escape(value)}</text>')
 logo_file=Path(rec['canonical_file_path']).name
 vb=list(map(float,ET.parse(LOCKUPS/logo_file).getroot().attrib['viewBox'].split()))
 x,y=s['logo_xy']; width=s['logo_width']; height=width*vb[3]/vb[2]
 s['logo_height']=height
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img">
<title>{html.escape(s['copy'][0])}</title>
<defs><style>@font-face{{font-family:Jost;src:url(data:font/truetype;base64,{font}) format('truetype');font-weight:100 900;font-style:normal;}} text{{font-synthesis:none;}}</style>
<linearGradient id="caption-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D2027" stop-opacity="0"/><stop offset=".4" stop-color="#1D2027" stop-opacity=".72"/><stop offset=".8" stop-color="#1D2027" stop-opacity=".72"/><stop offset="1" stop-color="#1D2027" stop-opacity="0"/></linearGradient>
<radialGradient id="headline-fade"><stop offset="0" stop-color="#1D2027" stop-opacity=".65"/><stop offset="1" stop-color="#1D2027" stop-opacity="0"/></radialGradient></defs>
<image href="../originals/{s['id']}.png" x="0" y="0" width="1080" height="1350" preserveAspectRatio="xMidYMid slice"/>
{''.join(s['layers'])}
<g id="editable-campaign-copy" data-typeface="Jost" data-exact-copy-json="{exact}">{''.join(texts)}</g>
<image id="canonical-lockup" href="../assets/lockups/{logo_file}" x="{x}" y="{y}" width="{width}" height="{height:.6f}" preserveAspectRatio="xMidYMid meet"/>
</svg>'''

def main():
 verifier=ROOT/'studio/tools/verify_asyada_canonical_lockups.py'
 if verifier.exists(): subprocess.run(['python3',str(verifier)],check=True)
 if CANONICAL.exists(): shutil.copy2(CANONICAL,ASSETS/'canonical-lockups.json')
 canonical_path=CANONICAL if CANONICAL.exists() else ASSETS/'canonical-lockups.json'
 canonical=json.loads(canonical_path.read_text()); recs={r['canonical_lockup_id']:r for r in canonical['records']}
 # Restore the original paper texture in the small title strip of slide 02.
 # This removes baked decorative strokes that crossed letterforms, not photography.
 # Original raster is preserved byte-for-byte; cleanup is a separately editable layer.
 from PIL import Image,ImageOps,ImageDraw,ImageFilter
 image=ImageOps.fit(Image.open(ORIGINALS/'02-perspective.png').convert('RGB'),(1080,1350))
 tile=image.crop((161,36,305,238))
 texture=Image.new('RGB',(1080,1350))
 for yy in range(0,1350,tile.height):
  for xx in range(0,1080,tile.width): texture.paste(tile,(xx,yy))
 mask=Image.new('L',(1080,1350));draw=ImageDraw.Draw(mask)
 draw.polygon([(42,30),(141,30),(145,462),(51,462)],fill=255)
 draw.polygon([(58,455),(365,451),(389,474),(380,596),(62,605),(45,584)],fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(3));texture.putalpha(mask)
 texture.save(ASSETS/'02-paper-cleanup.png')
 # Atmospheric floor shade protects contrast without a logo box, garment placement,
 # or an additional physical logo. The SVG is composited as a flat campaign signature.
 shade=Image.new('RGBA',(1080,1350),INK);alpha=Image.new('L',(1080,1350))
 d=ImageDraw.Draw(alpha);d.rounded_rectangle((668,1090,1034,1257),radius=30,fill=235)
 alpha=alpha.filter(ImageFilter.GaussianBlur(19));shade.putalpha(alpha)
 shade.save(ASSETS/'02-logo-contrast.png')
 image5=ImageOps.fit(Image.open(ORIGINALS/'05-invitation.png').convert('RGB'),(1080,1350))
 tile5=image5.crop((630,560,790,711));clean=Image.new('RGB',(1080,1350))
 for yy in range(0,1350,tile5.height):
  for xx in range(0,1080,tile5.width):clean.paste(tile5,(xx,yy))
 alpha5=Image.new('L',(1080,1350));d=ImageDraw.Draw(alpha5)
 d.polygon([(608,789),(972,789),(974,891),(610,885)],fill=255)
 alpha5=alpha5.filter(ImageFilter.GaussianBlur(9));clean.putalpha(alpha5)
 clean.save(ASSETS/'05-destinations-cleanup.png')
 for s in SLIDES:
  rec=recs[s['lockup']]; original=ROOT/rec['canonical_file_path']; copied=LOCKUPS/Path(rec['canonical_file_path']).name
  if original.exists(): shutil.copy2(original,copied)
  assert sha(copied)==rec['sha256'], 'Canonical artwork integrity failure: '+s['lockup']
  markup=svg_for(s,rec)
  (SOURCE/f"{s['id']}.svg").write_text(markup)
  (SOURCE/f"{s['id']}.html").write_text(f'<!doctype html><html lang="tr"><meta charset="utf-8"><title>{s["id"]} — placement revision 02</title><style>html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;background:{INK}}}svg{{display:block}}</style>{markup}</html>')
 subprocess.run(['node',str(HERE/'render.mjs')],check=True)
 m={
  'title':'Asya’da Eğitim — Launch Carousel Experiment 02 / Placement revision 02',
  'campaign':'Üniversite için başka bir dünya var.','revision':2,
  'status':'HUMAN EXPERIMENTAL CAMPAIGN REVIEW PENDING','dimensions':[1080,1350],
  'production_method':'Original image-first artwork preserved. Revision 02 individually typesets Jost using Chromium, with no stretching. Exact manifest-listed canonical SVGs are linked as complete artwork.',
  'font':{'family':'Jost','file':'assets/Jost-VF.ttf','sha256':sha(ASSETS/'Jost-VF.ttf')},
  'palette':{'paper':PAPER,'ink':INK,'red':RED},
  'exact_copy':{s['id']:s['copy'] for s in SLIDES},
  'imagery_disclosure':'All people/places are illustrative AI imagery; destination images use city cues, not documentary landmark or named-university claims.',
  'gpt_image_2':{'generation_count':5,'edit_count':1,'revision_02_new_image_calls':0,'backend':'gpt-image-2 via connected ChatGPT subscription'},
  'previous_revision':'history/v1/index.html',
  'alternate_generations':[{'slide':'05-invitation','file':'originals/05-invitation-first.png','sha256':sha(ORIGINALS/'05-invitation-first.png')}],
  'slides':[]
 }
 metrics=json.loads((HERE/'render-validation.json').read_text())
 for s in SLIDES:
  rec=recs[s['lockup']]
  m['slides'].append({
   'id':s['id'],'final_file':f"final/{s['id']}.png",'final_sha256':sha(FINAL/f"{s['id']}.png"),
   'original_file':f"originals/{s['id']}.png",'original_sha256':sha(ORIGINALS/f"{s['id']}.png"),
   'source_file':f"source/{s['id']}.svg",'source_sha256':sha(SOURCE/f"{s['id']}.svg"),
   'editable_html_file':f"source/{s['id']}.html",'dimensions':[1080,1350],'copy':s['copy'],
   'canonical_lockup_id':s['lockup'],'canonical_lockup_sha256':rec['sha256'],
   'canonical_logo_sha256':SEAL_SHA,'canonical_seal_sha256':SEAL_SHA,
   'canonical_lockup_file':f'assets/lockups/{Path(rec["canonical_file_path"]).name}',
   'logo_width_px':s['logo_width'],'logo_height_px':s['logo_height'],'logo_x_y_px':s['logo_xy'],
   'minimum_supported_display_width_px':rec['minimum_supported_display_size']['screen_width_px'],
   'composition_note':s['note'],'render_validation':metrics[s['id']],
  })
 (HERE/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
 print('Built revision 02: 5 Chromium/Jost-rendered slides; exact logo hashes unchanged.')

if __name__=='__main__': main()

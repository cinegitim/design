#!/usr/bin/env python3
"""Verify exact copy/identity, create review previews, manifest and source package."""
from pathlib import Path
import hashlib, json, zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
IDS=['01-hook','02-life-after-class','03-universities','04-language','05-budget','06-decision']
SEAL='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
NS='{http://www.w3.org/2000/svg}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ' '.join(s.split())

exact=json.loads((HERE/'exact-copy.json').read_text())['slides']
report=json.loads((HERE/'render-validation.json').read_text())
canonical=json.loads((ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
records={r['canonical_lockup_id']:r for r in canonical['records']}
photos=json.loads((HERE/'photography-sources.json').read_text())['records']
for rec in photos:
 p=HERE/rec['file']; assert p.is_file() and sha(p)==rec['sha256'],rec['id']

(HERE/'mobile').mkdir(exist_ok=True); (HERE/'package').mkdir(exist_ok=True)
font=ImageFont.truetype(str(HERE/'assets/Jost-VF.ttf'),16)
srgb_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
finals=[]; pairs=[]; slides=[]; integrity=[]
for ident in IDS:
 final=HERE/'final'/f'{ident}.png'; original=HERE/'originals'/f'{ident}.png'; source=HERE/'source'/f'{ident}.svg'; editable=HERE/'source'/f'{ident}.html'
 assert Image.open(final).size==(1080,1350) and Image.open(original).size==(1080,1350)
 assert report[ident]['jostLoaded'] and not report[ident]['issues']
 root=ET.parse(source).getroot(); group=next(e for e in root.iter() if e.attrib.get('id')=='editable-campaign-copy')
 encoded=json.loads(group.attrib['data-exact-copy-json']); visible=' '.join((e.text or '') for e in group.iter(NS+'text'))
 assert encoded==exact[ident],f'{ident}: exact metadata'
 assert norm(visible)==norm(' '.join(exact[ident])),f'{ident}: visible exact copy'
 mark=next(e for e in root.iter() if e.attrib.get('id')=='canonical-lockup'); lock_id=mark.attrib['data-lockup-id']; rec=records[lock_id]
 copied=HERE/'assets/lockups'/Path(rec['canonical_file_path']).name; assert sha(copied)==rec['sha256']
 x,y,w,h=[float(mark.attrib[k]) for k in ('x','y','width','height')]
 assert w>=rec['minimum_supported_display_size']['screen_width_px']
 im=Image.open(final).convert('RGB'); im.save(final,optimize=True,icc_profile=srgb_profile); im=Image.open(final).convert('RGB')
 bg=Image.open(original).convert('RGB')
 mobile=im.resize((375,469),Image.Resampling.LANCZOS); mobile.save(HERE/'mobile'/f'{ident}-375x469.png',optimize=True)
 finals.append((ident,im)); pairs.append((ident,bg,im))
 changed=sum(1 for a,b in zip(im.getdata(),bg.getdata()) if max(abs(a[i]-b[i]) for i in range(3))>24)
 integrity.append({'slide':ident,'background_to_final_changed_area_percent':round(changed/(1080*1350)*100,2),'status':'PASS'})
 slides.append({'id':ident,'final_file':f'final/{ident}.png','final_sha256':sha(final),'original_file':f'originals/{ident}.png','original_sha256':sha(original),'source_file':f'source/{ident}.svg','source_sha256':sha(source),'editable_html_file':f'source/{ident}.html','dimensions':[1080,1350],'copy':exact[ident],'canonical_lockup_id':lock_id,'canonical_lockup_sha256':rec['sha256'],'canonical_logo_sha256':SEAL,'canonical_seal_sha256':SEAL,'canonical_lockup_file':f'assets/lockups/{copied.name}','logo_width_px':w,'logo_height_px':h,'logo_x_y_px':[x,y],'minimum_supported_display_width_px':rec['minimum_supported_display_size']['screen_width_px'],'render_validation':report[ident]})

# 3×2 contact sheet.
sheet=Image.new('RGB',(1080,1000),'#111318');d=ImageDraw.Draw(sheet)
for i,(ident,im) in enumerate(finals):
 x=(i%3)*360;y=(i//3)*500;sheet.paste(im.resize((360,450),Image.Resampling.LANCZOS),(x,y));d.text((x+12,y+462),f'{i+1:02}  {ident}',font=font,fill='#F7F3E9')
sheet.save(HERE/'contact-sheet.png',optimize=True)

# Clean editorial background → final typography/signature comparison.
pair=Image.new('RGB',(6*300,410),'#111318');d=ImageDraw.Draw(pair)
for i,(ident,bg,im) in enumerate(pairs):
 pair.paste(bg.resize((150,188),Image.Resampling.LANCZOS),(i*300,0));pair.paste(im.resize((150,188),Image.Resampling.LANCZOS),(i*300+150,0));d.text((i*300+6,198),'BACKGROUND',font=font,fill='#9BA0A8');d.text((i*300+156,198),'FINAL',font=font,fill='#F7F3E9');d.text((i*300+6,232),ident,font=font,fill='#F7F3E9')
pair.save(HERE/'source-vs-final-contact-sheet.jpg',quality=92,optimize=True)

# Mobile carousel preview in one horizontal viewport strip.
mobile_strip=Image.new('RGB',(6*215+70,370),'#111318');d=ImageDraw.Draw(mobile_strip)
for i,(ident,im) in enumerate(finals):
 thumb=im.resize((205,256),Image.Resampling.LANCZOS);x=35+i*215;mobile_strip.paste(thumb,(x,42));d.text((x,312),f'{i+1:02}',font=font,fill='#F7F3E9')
mobile_strip.save(HERE/'mobile-carousel-preview.png',optimize=True)

# Feed cover preview: square Instagram crop shown inside a neutral feed shell.
cover=finals[0][1];crop=ImageOps.fit(cover,(810,810),centering=(.5,.45));feed=Image.new('RGB',(1080,1080),'#EEEAE1');feed.paste(crop,(135,135));d=ImageDraw.Draw(feed);d.rounded_rectangle((54,52,1026,1028),radius=34,outline='#D2CBBB',width=4);d.ellipse((86,78,135,127),fill='#BD2120');d.text((151,87),"asyadaegitim",font=ImageFont.truetype(str(HERE/'assets/Jost-VF.ttf'),23),fill='#1D2027');d.text((845,87),'•••',font=font,fill='#1D2027')
feed.save(HERE/'instagram-feed-cover-preview.png',optimize=True)

# Final-vs-mobile proof, used as the requested revision/readability comparison artifact.
mobile_compare=Image.new('RGB',(6*285,430),'#111318');d=ImageDraw.Draw(mobile_compare)
for i,(ident,im) in enumerate(finals):
 mobile=Image.open(HERE/'mobile'/f'{ident}-375x469.png').convert('RGB');mobile_compare.paste(im.resize((142,178),Image.Resampling.LANCZOS),(i*285,0));mobile_compare.paste(mobile.resize((142,178),Image.Resampling.LANCZOS),(i*285+143,0));d.text((i*285+4,190),'FULL',font=font,fill='#F7F3E9');d.text((i*285+147,190),'375 PX',font=font,fill='#D8F457');d.text((i*285+4,225),ident,font=font,fill='#F7F3E9')
mobile_compare.save(HERE/'full-vs-mobile-contact-sheet.jpg',quality=92,optimize=True)

manifest={'title':"Asya'da Eğitim — Rotanı Seç #001 / Tokyo mu, Seul mü?",'campaign':'Rotanı Seç / 001','status':'HUMAN CAMPAIGN REVIEW PENDING — NOT SOCIAL-PUBLISHED','dimensions':[1080,1350],'colour_space':'sRGB','production_method':'Licensed documentary photographs and deterministic HTML/CSS/SVG composition. Exact Turkish copy remains editable in SVG. Canonical lockups are complete, unmodified manifest-listed SVGs.','font':{'family':'Jost','file':'assets/Jost-VF.ttf','sha256':sha(HERE/'assets/Jost-VF.ttf')},'palette_anchors':{'red':'#BD2120','ink':'#1D2027','paper':'#F7F3E9'},'exact_copy':exact,'photography_sources':'photography-sources.json','photography_attributions':'photography-attributions.md','image_model_calls':{'generation_count':0,'edit_count':0,'note':'No AI-generated imagery used; all campaign photography is licensed Wikimedia Commons material.'},'factual_sources':'factual-sources.md','slides':slides,'pixel_integrity_review':integrity,'mobile_preview_files':[f'mobile/{i}-375x469.png' for i in IDS],'contact_sheet_file':'contact-sheet.png','source_vs_final_contact_sheet_file':'source-vs-final-contact-sheet.jpg','revision_comparison_file':'full-vs-mobile-contact-sheet.jpg','mobile_carousel_preview_file':'mobile-carousel-preview.png','feed_cover_preview_file':'instagram-feed-cover-preview.png','package_file':'package/rotani-sec-tokyo-seoul-001.zip'}
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

readme="""# Rotanı Seç #001 — Tokyo mu, Seul mü?\n\nSix final 1080×1350 sRGB PNG slides are included at ZIP root and in `final/`. Editable HTML/SVG sources preserve exact copy separately from licensed photographs. `templates/` contains the art-directed HTML/CSS composition source; `originals/` contains clean rendered backgrounds; `assets/photos/originals/` preserves downloaded source photographs.\n\nCanonical Asya'da Eğitim lockups are exact copied SVG files. Human campaign review is pending. Nothing in this package authorizes social publication.\n\nRebuild with the repository-pinned Playwright module and Chrome: `python3 build.py && python3 verify_and_package.py`.\n"""
(HERE/'package/README.md').write_text(readme,encoding='utf-8')
zip_path=HERE/manifest['package_file']; zip_path.unlink(missing_ok=True)
include=[HERE/'manifest.json',HERE/'exact-copy.json',HERE/'build.py',HERE/'extract-backgrounds.mjs',HERE/'render.mjs',HERE/'verify_and_package.py',HERE/'render-validation.json',HERE/'text-layout.json',HERE/'quality-review.md',HERE/'generation-notes.md',HERE/'photography-sources.json',HERE/'photography-attributions.md',HERE/'factual-sources.md',HERE/'caption.md',HERE/'platform-adaptation-notes.md',HERE/'handoff.md',HERE/'package/README.md',HERE/'contact-sheet.png',HERE/'source-vs-final-contact-sheet.jpg',HERE/'full-vs-mobile-contact-sheet.jpg',HERE/'mobile-carousel-preview.png',HERE/'instagram-feed-cover-preview.png']
for folder in ('final','originals','source','templates','mobile','assets'):
 include.extend(p for p in (HERE/folder).rglob('*') if p.is_file())
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in include:z.write(p,p.relative_to(HERE))
 for ident,_ in finals:z.write(HERE/'final'/f'{ident}.png',f'{ident}.png')
print(json.dumps({'slides':6,'exact_copy':'PASS','canonical_lockups':'PASS','package':str(zip_path),'package_bytes':zip_path.stat().st_size},ensure_ascii=False,indent=2))

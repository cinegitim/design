#!/usr/bin/env python3
"""Validate exports, create mobile/contact previews, and assemble publishable ZIP."""
from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
M = json.loads((HERE / "manifest.json").read_text())
JOST = HERE / "assets/Jost-VF.ttf"
OUT = HERE / "mobile"
OUT.mkdir(exist_ok=True)

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

small = ImageFont.truetype(str(JOST), 14)
finals=[]
pair_images=[]
integrity=[]
for slide in M["slides"]:
    final=HERE / slide["final_file"]
    original=HERE / slide["original_file"]
    source=HERE / slide["source_file"]
    assert final.exists() and original.exists() and source.exists()
    assert Image.open(final).size == (1080,1350), (slide["id"],Image.open(final).size)
    assert sha(final)==slide["final_sha256"], slide["id"]+" final hash"
    assert sha(original)==slide["original_sha256"], slide["id"]+" original hash"
    assert sha(source)==slide["source_sha256"], slide["id"]+" source hash"
    assert slide["logo_width_px"] >= slide["minimum_supported_display_width_px"], slide["id"]+" below canonical minimum"
    for line in slide["copy"]:
        assert line in M["exact_copy"][slide["id"]]
    source_root=ET.parse(source).getroot()
    editable=next(el for el in source_root.iter() if el.attrib.get('id')=='editable-campaign-copy')
    encoded_copy=json.loads(editable.attrib.get('data-exact-copy-json','[]'))
    assert encoded_copy==slide['copy'], slide['id']+" editable SVG copy mismatch"
    im=Image.open(final).convert('RGB')
    im.resize((324,405),Image.Resampling.LANCZOS).save(OUT/f"{slide['id']}-324x405.png",optimize=True)
    finals.append((slide,im))
    # Compare against crop/scale of exact source art; guard against flattening the original design.
    source_img=ImageOps.fit(Image.open(original).convert('RGB'),(1080,1350),method=Image.Resampling.LANCZOS)
    diff=ImageChops.difference(im,source_img).convert('L')
    changed=sum(1 for px in diff.getdata() if px>24)
    changed_pct=round(changed/(1080*1350)*100,2)
    assert changed_pct < 55, f"{slide['id']} reconstruction altered too much of source ({changed_pct}%)"
    # Confirm actual logo-region pixel changes, not only a manifest declaration.
    x,y=slide['logo_x_y_px']; w=slide['logo_width_px']; ar={"P-01":1.017,"C-03":2.312,"D-04":2.612,"H-02":2.666}[slide['canonical_lockup_id'].split('/')[0]]; h=round(w/ar)
    logo_diff=diff.crop((x,y,min(1080,x+w),min(1350,y+h)))
    logo_pixels=sum(1 for px in logo_diff.getdata() if px>45)
    assert logo_pixels>1200, f"{slide['id']} logo zone not genuinely composited"
    integrity.append({"slide":slide['id'],"source_to_final_changed_area_percent":changed_pct,"logo_region_changed_pixels":logo_pixels,"status":"PASS"})
    pair_images.append((source_img.resize((180,225),Image.Resampling.LANCZOS),im.resize((180,225),Image.Resampling.LANCZOS),slide['id']))

# Full five-slide final contact sheet.
sheet=Image.new('RGB',(5*216,320),'#17181b'); d=ImageDraw.Draw(sheet)
for i,(slide,im) in enumerate(finals):
    sheet.paste(im.resize((216,270),Image.Resampling.LANCZOS),(i*216,0))
    d.text((i*216+8,282),f"0{i+1}  {slide['id'].split('-',1)[1]}",font=small,fill='#f7f3e9')
sheet.save(HERE/'contact-sheet.png',optimize=True)

# Side-by-side original → final contact strip.
pair=Image.new('RGB',(10*180,255),'#17181b'); d=ImageDraw.Draw(pair)
for i,(o,f,label) in enumerate(pair_images):
    pair.paste(o,(i*360,0));pair.paste(f,(i*360+180,0))
    d.text((i*360+3,232),f"0{i+1} ORIGINAL",font=small,fill='#f7f3e9')
    d.text((i*360+184,232),"FINAL",font=small,fill='#f7f3e9')
pair.save(HERE/'original-to-final-contact-sheet.jpg',quality=91,optimize=True)

# Verify every copied lockup against canonical manifest.
canonical=json.loads((ROOT/'brands/asyada-egitim/assets/lockups/canonical-lockups.json').read_text())
records={r['canonical_lockup_id']:r for r in canonical['records']}
for slide in M['slides']:
    rec=records[slide['canonical_lockup_id']]
    asset=ROOT/rec['canonical_file_path']
    assert sha(asset)==rec['sha256']==slide['canonical_lockup_sha256']
    copied=HERE/'assets/lockups'/asset.name
    assert sha(copied)==rec['sha256']

M['pixel_integrity_review']=integrity
M['package_file']='package/launch-carousel-5slides.zip'
M['mobile_preview_files']=[f"mobile/{s['id']}-324x405.png" for s in M['slides']]
M['contact_sheet_file']='contact-sheet.png'
M['source_vs_final_contact_sheet_file']='original-to-final-contact-sheet.jpg'
(HERE/'manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2))

readme='''# Asya’da Eğitim — Launch Carousel Experiment 02\n\nFive publishable 1080×1350 PNGs are at the ZIP root, named 01-cover.png through 05-invitation.png.\n\n- `originals/`: unmodified generated artwork used as the visual source of truth (plus initial slide-05 version).\n- `source/`: editable SVG reconstructions with linked originals and canonical SVG lockups.\n- `assets/`: Jost variable font and verbatim manifest-listed canonical lockup SVGs.\n- `build.py`: deterministic SVG/PNG build.\n- `manifest.json`: exact copy, hashes, provenance, pixel-difference/fidelity metrics, and canonical lockup IDs/hashes.\n\nAI people/places are illustrative; no exact institution or landmark is claimed. Review pending; not published to Instagram.\n'''
(HERE/'package/README.md').write_text(readme,encoding='utf-8')
zip_path=HERE/'package/launch-carousel-5slides.zip'
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for slide in M['slides']:
        p=HERE/slide['final_file']; z.write(p,Path(slide['final_file']).name)
    paths=[HERE/'manifest.json',HERE/'build.py',HERE/'verify_and_package.py',HERE/'generation-notes.md',HERE/'quality-review.md',HERE/'package/README.md',JOST,HERE/'contact-sheet.png',HERE/'original-to-final-contact-sheet.jpg']
    paths += sorted((HERE/'originals').glob('*.png'))
    paths += sorted((HERE/'source').glob('*.svg'))
    paths += sorted((HERE/'assets/lockups').glob('*.svg'))
    for p in paths:
        z.write(p,p.relative_to(HERE))
print(json.dumps({"slides":len(finals),"integrity":integrity,"zip":str(zip_path),"zip_bytes":zip_path.stat().st_size},ensure_ascii=False,indent=2))

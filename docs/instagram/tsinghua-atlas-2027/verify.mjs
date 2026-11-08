import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const root=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(root,'../../../');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const locks=JSON.parse(await fs.readFile(path.join(repo,'brands/asyada-egitim/assets/lockups/canonical-lockups.json'),'utf8'));
const expectedSeal='8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a';
if(locks.canonical_seal_sha256!==expectedSeal) throw Error('Canonical seal manifest SHA mismatch');
const variants={
  'P-01/light':{asset:'assets/p-01-light.svg',canonical:'brands/asyada-egitim/assets/lockups/p-01-primary-stacked-light.svg',min:352},
  'D-04/light':{asset:'assets/d-04-light.svg',canonical:'brands/asyada-egitim/assets/lockups/d-04-small-use-digital-light.svg',min:200},
  'D-04/dark':{asset:'assets/d-04-dark.svg',canonical:'brands/asyada-egitim/assets/lockups/d-04-small-use-digital-dark.svg',min:200},
};
const logoRecords={};
for(const [id,v] of Object.entries(variants)){
  const local=await fs.readFile(path.join(root,v.asset));
  const canonical=await fs.readFile(path.join(repo,v.canonical));
  if(!local.equals(canonical)) throw Error(`${id}: local SVG differs from canonical original`);
  const record=locks.records.find(r=>r.canonical_lockup_id===id);
  if(!record||sha(local)!==record.sha256) throw Error(`${id}: SHA-256 does not match canonical manifest`);
  logoRecords[id]={file:v.asset,canonical_file:v.canonical,sha256:sha(local),minimum_display_width_px:v.min};
}
const rendered=[];
for(let i=1;i<=7;i++){
  const n=String(i).padStart(2,'0');
  const image=await fs.readFile(path.join(root,'png',`${n}.png`));
  if(!image.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) throw Error(`png/${n}.png is not a PNG`);
  const width=image.readUInt32BE(16),height=image.readUInt32BE(20);
  if(width!==1080||height!==1350) throw Error(`png/${n}.png dimensions ${width}x${height}`);
  const html=await fs.readFile(path.join(root,'source',`${n}.html`),'utf8');
  for(const asset of ['Jost-VF.ttf','d-04-light.svg','d-04-dark.svg','p-01-light.svg','tsinghua-main-building.jpg','tsinghua-old-library.jpg']){
    if(html.includes(asset)) await fs.access(path.join(root,'assets',asset));
  }
  const ids={1:'P-01/light',2:'D-04/light',3:'D-04/light',4:'D-04/light',5:'D-04/light',6:'D-04/light',7:'D-04/dark'};
  rendered.push({slide_id:`${n}`,file:`png/${n}.png`,editable:`source/${n}.html`,dimensions:[width,height],sha256:sha(image),canonical_lockup_id:ids[i],canonical_lockup_sha256:logoRecords[ids[i]].sha256,canonical_seal_sha256:expectedSeal});
}
const assetFiles=['assets/Jost-VF.ttf','assets/Jost-OFL.txt','assets/carousel.css','assets/tsinghua-main-building.jpg','assets/tsinghua-old-library.jpg','contact-sheet.svg','contact-sheet.png','mobile-feed-preview.html','sources-and-verification.md','production-notes.md','generation-notes.md','quality-review.md','caption-and-credits.md'];
const assets={};
for(const file of assetFiles){const bytes=await fs.readFile(path.join(root,file));assets[file]={sha256:sha(bytes),bytes:bytes.length};}
const manifest={
  title:'Tsinghua Üniversitesi — 2027 lisans başvuru carousel',
  status:'HUMAN REVIEW PENDING — DESIGN-SITE REVIEW; NOT POSTED TO INSTAGRAM',
  checked_on:'2026-10-10',dimensions:[1080,1350],color_space:'sRGB (Chrome PNG render)',
  brand:'asyada-egitim',brand_system_note:'Approved identity metadata and lockups used; no full brand-system approval inferred.',
  canonical_seal_sha256:expectedSeal,canonical_lockups:logoRecords,slides:rendered,assets,
  files:{contact_sheet:'contact-sheet.png',contact_sheet_editable:'contact-sheet.svg',mobile_preview:'mobile-feed-preview.html',gallery:'index.html',sources:'sources-and-verification.md',quality_review:'quality-review.md',caption:'caption-and-credits.md',font_license:'assets/Jost-OFL.txt'},
  production:{image_generation:'none',render:'Chrome + Playwright; editable HTML per slide',design_site_review_page:true,instagram_published:false}
};
await fs.writeFile(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'PASS',slides:rendered.length,dimensions:'1080x1350',canonical_lockups:Object.keys(logoRecords)},null,2));

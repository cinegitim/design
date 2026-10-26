import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {test} from 'node:test';

const root=path.resolve(import.meta.dirname,'../../..');
const source=fs.readFileSync(path.join(root,'docs/visual-editor/browser/catalog.js'),'utf8');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'docs/visual-editor/browser/product-groups.json'),'utf8'));
const inventory=JSON.parse(fs.readFileSync(path.join(root,'docs/inventory/snapshot.json'),'utf8'));
const archive=JSON.parse(fs.readFileSync(path.join(root,'docs/archive/retired-collections.json'),'utf8'));
const scope={URL,console};vm.runInNewContext(source,scope);
const Catalog=scope.BrandstudioCatalog;
const raw=Catalog.fromPaths(inventory.files.map(x=>x[0]));
const families=Catalog.groupRecords(raw,manifest);

test('27 independently discovered versions reduce to 14 usable families',()=>{
 assert.equal(raw.length,27);
 assert.equal(families.length,14);
 assert.equal(new Set(families.map(x=>x.id)).size,14);
 assert.ok(families.every(x=>x.pages.length>0&&Array.isArray(x.versions)&&x.versions.length));
});
test('all 27 old product ids either still belong to a family or are explicitly retired',()=>{
 const retired=new Set(manifest.retired.map(x=>x.id));
 assert.deepEqual(new Set(raw.filter(x=>!Catalog.byId(families,x.id)).map(x=>x.id)),retired);
 assert.ok(!families.some(x=>retired.has(x.id)));
});
test('main family opens default version and old source URLs retain their product id',()=>{
 for(const group of manifest.groups){
  const match=families.find(x=>x.id===group.defaultId);
  assert.ok(match,'missing default '+group.defaultId);
  assert.equal(match.groupId,group.defaultId);
  assert.equal(match.currentId,group.currentId);
  assert.equal(match.defaultId,group.defaultId);
  assert.deepEqual(Array.from(match.categoryPath),group.categoryPath);
  for(const version of group.versions){
   const actual=Catalog.byId(families,version.id);
   assert.ok(actual,version.id);
   assert.equal(actual.id,version.id);
   assert.equal(actual.groupId,group.defaultId);
   assert.ok(actual.pages.every(p=>p.includes('/')));
  }
 }
});
test('Phase 2C variants include retained Phase 2B cover and all updated slides',()=>{
 for(const [suffix,number] of [['a-snu',7],['b-waseda',6],['c-tokyo',7],['d-six-steps',8]]){
  const p=Catalog.byId(families,'instagram-phase-2c-'+suffix);
  assert.equal(p.pages.length,number);
  assert.match(p.pages[0],new RegExp('phase-2b/'+suffix+'/editable/01.html$'));
  assert.match(p.pages[1],new RegExp('phase-2c/'+suffix+'/editable/02.html$'));
 }
});
test('source assets and canonical identity paths are preserved in original repository',()=>{
 assert.equal(archive.filesTotal,1372);
 assert.equal(archive.transferState,'archive-branch-verified-source-paths-preserved');
 const src=new Map(inventory.files.map(x=>[x[0],x]));
 const uniq=new Set();
 for(const group of archive.collections)for(const f of group.files){
  assert.ok(!uniq.has(f.path),'double archived '+f.path);uniq.add(f.path);
  assert.equal(f.gitBlob,src.get(f.path)?.[1]);assert.equal(f.bytes,src.get(f.path)?.[2]);
  assert.ok(!/^brands\/(?:asyada-egitim|cin-egitim)\/assets\//.test(f.path),'canonical brand asset archived '+f.path);
  assert.ok(!/^brands\/(?:asyada-egitim|cin-egitim)\/decisions\//.test(f.path),'canonical decision archived '+f.path);
  assert.ok(!f.path.startsWith('brands/cin-egitim/reference/'));
 }
 assert.equal(uniq.size,1372);
});
test('Instagram publication requires real post evidence and does not invent a matched revision',()=>{
 const published=families.filter(x=>x.lifecycle==='published');
 assert.equal(manifest.socialPublication.totalInstagramPostsSeen,7);
 assert.equal(published.length,5);
 assert.deepEqual(new Set(published.map(x=>x.id)),new Set([
  'instagram-carousel-01-v2','instagram-tsinghua-atlas-2027-v2','instagram-rotani-sec-tokyo-seoul-001-v3',
  'instagram-basvuru-rehberi-china-001','instagram-burs-dosyasi-gks-2027-001'
 ]));
 assert.ok(families.every(x=>(x.publications||[]).every(p=>p.verified&&p.url.startsWith('https://www.instagram.com/'))));
 const publishedV2=Catalog.byId(families,'instagram-carousel-01-v2');
 assert.equal(publishedV2.lifecycle,'published');
 assert.equal(publishedV2.publications[0].productId,'instagram-carousel-01-v2');
 const newerDraft=Catalog.byId(families,'carousel-01-v3');
 assert.equal(newerDraft.lifecycle,'in-review');
 assert.ok(newerDraft.familyPublications.length);
 const withInvalid=JSON.parse(JSON.stringify(manifest));
 withInvalid.socialPublication.posts=[{groupId:'instagram-carousel-01',verified:true,url:'https://not-instagram.com/p/XYZ',publishedAt:'2026-10-01'}];
 assert.equal(Catalog.groupRecords(raw,withInvalid).find(x=>x.id==='instagram-carousel-01-v2').lifecycle,'in-review');
 const withEvidence=JSON.parse(JSON.stringify(manifest));
 withEvidence.socialPublication.posts=[{groupId:'instagram-carousel-01',verified:true,url:'https://www.instagram.com/p/AbCdEf01234/',publishedAt:'2026-10-20'}];
 assert.equal(Catalog.groupRecords(raw,withEvidence).find(x=>x.id==='instagram-carousel-01-v2').lifecycle,'published');
});
test('future products not manually mapped remain visible',()=>{
 const rawPlus=[...raw,{id:'instagram-new-product-001',title:'Yeni Tasarım',family:'instagram',kind:'html',pages:['instagram/new-product-001/source/01.html']}];
 const newest=Catalog.groupRecords(rawPlus,manifest);
 assert.equal(newest.length,15);
 assert.ok(newest.find(x=>x.id==='instagram-new-product-001'));
});
test('editor offers actual product version selector; catalog does not show historical experiments',()=>{
 const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
 assert.match(html,/id="catalog-version"/);
 assert.match(html,/renderProductVersions/);
 assert.match(html,/İncelemede/);
 assert.match(html,/Yayımlandı/);
 assert.doesNotMatch(html,/Üretim Envanteri<\/a>/);
});

test('Phase 2C saved edits and linked groups migrate to retained-cover numbering exactly once',()=>{
 const old={colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:{'0:5':{styles:{left:'123px'}},'2:7':{styles:{top:'10px'}}},groups:{'0':[[1,2]],'2':[[3,4]]}};
 const moved=Catalog.migrateLegacyPhase2CState(old);
 assert.deepEqual(Object.keys(moved.edits).sort(),['1:5','3:7']);
 assert.deepEqual(Object.keys(moved.groups).sort(),['1','3']);
 assert.equal(moved.edits['1:5'].styles.left,'123px');
 assert.equal(old.edits['0:5'].styles.left,'123px');
 assert.equal(moved.colors.paper,old.colors.paper);
 const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
 assert.match(html,/sourcePageSchema===2/);
 assert.match(html,/pre-cover-20261026/);
 assert.match(html,/raw\.sourcePageSchema!==2/);
 assert.match(html,/if\(sourceCoverAdded\(\)\)updated\.sourcePageSchema=2/);
});

test('published revision v2 is the default, while latest v3 remains directly selectable',()=>{
 const g=families.find(x=>x.familyId==='instagram-carousel-01');
 assert.equal(g.id,'instagram-carousel-01-v2');
 assert.equal(g.currentId,'carousel-01-v3');
 assert.equal(g.publishedVersionId,'instagram-carousel-01-v2');
 assert.equal(g.publications[0].productId,'instagram-carousel-01-v2');
 assert.equal(g.versions.length,3);
 assert.deepEqual(Array.from(g.versions,x=>x.label),['v1','v2','v3']);
 assert.equal(Catalog.byId(families,'carousel-01-v3').id,'carousel-01-v3');
});
test('design taxonomy has subcategories nested within carousels',()=>{
 const carousel=manifest.groups.filter(g=>g.categoryPath?.[1]==='Karuseller');
 assert.equal(carousel.length,11);
 assert.ok(new Set(carousel.map(g=>g.categoryPath[2])).size>=4);
 assert.ok(carousel.every(g=>g.categoryPath[0]==='Sosyal Medya'));
 assert.equal(manifest.groups.filter(g=>g.categoryPath?.[2]==='Logolar ve Kapaklar').length,2);
 const workspace=fs.readFileSync(path.join(root,'docs/workspaces/asyada-egitim/index.html'),'utf8');
 assert.match(workspace,/work-subgroup/);
 assert.match(workspace,/work-class/);
 assert.match(workspace,/Logolar ve Kapaklar/);
 assert.match(workspace,/tile\.href='logos-and-covers\/'/);
 assert.match(workspace,/g\.defaultId\|\|g\.currentId/);
});
test('one actual gallery shows logos, profile images, and platform covers',()=>{
 const folder=path.join(root,'docs/workspaces/asyada-egitim/logos-and-covers');
 const html=fs.readFileSync(path.join(folder,'index.html'),'utf8');
 assert.match(html,/Onaylı logo ailesi/);
 assert.match(html,/Sosyal medya profil görselleri/);
 assert.match(html,/Sosyal medya kapakları/);
 assert.doesNotMatch(html,/location\.replace\(/);
 const src=[...html.matchAll(/<img[^>]*src="([^"]+)"/g)].map(x=>x[1]);
 assert.ok(src.length>=10);
 const publishedFiles=new Set(inventory.files.map(f=>f[0]));
 for(const rel of src){
  const repoPath=path.relative(root,path.resolve(folder,rel)).split(path.sep).join('/');
  assert.ok(publishedFiles.has(repoPath),'Gallery references untracked image: '+repoPath);
 }
});

test('review tiles expose compact, separately accessible icons within each card',()=>{
 const ws=fs.readFileSync(path.join(root,'docs/workspaces/asyada-egitim/index.html'),'utf8');
 assert.match(ws,/function quickIcon\(kind\)/);
 assert.match(ws,/className='quick-action ig'|el\('a','quick-action ig'\)/);
 assert.match(ws,/el\('a','quick-action edit'\)/);
 assert.match(ws,/el\('nav','quick-actions'\)/);
 assert.match(ws,/actions\.append\(editor\)/);
 assert.match(ws,/wrap\.append\(actions\)/);
 assert.match(ws,/proof\.setAttribute\('aria-label'/);
 assert.match(ws,/editor\.setAttribute\('aria-label'/);
 assert.doesNotMatch(ws,/visual-editor-action/);
 assert.doesNotMatch(ws,/instagram-proof-link/);
 assert.match(ws,/const pub=posts\.filter\(p=>pubUrl\(p\)/);
 assert.match(ws,/tile\.href=url/);
 assert.match(ws,/tile\.href='logos-and-covers\/'/);
});

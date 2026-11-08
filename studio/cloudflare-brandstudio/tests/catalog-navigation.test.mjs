import assert from "node:assert/strict";
import {test} from "node:test";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const root=path.resolve(import.meta.dirname,"../../..");
const browser=path.join(root,"docs/visual-editor/browser");
const read=(file)=>fs.readFileSync(path.join(browser,file),"utf8");
const manifest=JSON.parse(read("product-groups.json"));
const navigation=JSON.parse(read("navigation-classification.json"));
const registry=JSON.parse(read("style-registry.json"));
const script=read("catalog-navigation.js"),ui=read("catalog-navigator-ui.js");
const scope={};vm.runInNewContext(script,scope);
const N=scope.BrandstudioCatalogNavigation;
const records=manifest.groups.map(g=>({
  id:g.defaultId||g.currentId,familyId:g.id,title:g.title,brand:g.brand,categoryPath:g.categoryPath,
  versions:g.versions,currentId:g.currentId,defaultId:g.defaultId,
  publishedVersionId:g.publishedVersionId||null
}));
const index=()=>N.build(records,navigation,registry);
const asJson=x=>JSON.parse(JSON.stringify(x));

test("19 products, all 32 source versions, independent brands and two retired assets remain intact",()=>{
  const x=index();
  assert.equal(x.products.length,19);
  assert.equal(x.products.reduce((count,p)=>count+p.versions.length,0),32);
  assert.deepEqual(new Set(x.products.map(p=>p.groupId)),new Set(manifest.groups.map(g=>g.id)));
  assert.equal(navigation.items.length,19);
  assert.equal(navigation.confirmedVersions.length,0);
  assert.equal(new Set(navigation.items.map(x=>x.groupId)).size,19);
  assert.equal(manifest.retired.length,2);
  assert.equal(x.products.find(x=>x.groupId==="cin-egitim-rollup").brand,"cin-egitim");
  assert.ok(x.products.every(x=>x.defaultId&&x.versions.some(v=>v.id===x.defaultId)));
});

test("content browser has 5-level paths with real content subjects, and proposals stay proposed",()=>{
 const x=index(),categories=N.facets(x,"asyada-egitim","");
 assert.deepEqual(asJson(categories.mains),["Karuseller","Profil ve Kapaklar","Tekil Paylaşımlar"]);
 const carousels=N.filter(x,{brand:"asyada-egitim",main:"Karuseller",sort:"category"});
 assert.equal(carousels.length,14);
 assert.equal(carousels.filter(x=>x.sub==="Üniversite Tanıtımları").length,3);
 assert.equal(carousels.filter(x=>x.sub==="Başvuru ve Burs Rehberleri").length,3);
 assert.equal(carousels.filter(x=>x.sub==="Şehir ve Öğrenci Yaşamı").length,2);
 assert.equal(carousels.filter(x=>x.sub==="Lansman ve Kampanyalar").length,4);
 assert.equal(carousels.filter(x=>x.sub==="Üniversite Fırsatları").length,1);
 const bavul=x.products.find(x=>x.groupId==="instagram-creative-breakout-bavul-001");
 assert.equal(bavul.sub,"Yaratıcı Kampanyalar");
 assert.equal(bavul.links.length,0,"Creative Breakout was a legacy subject label, not approved style usage");
 assert.ok(x.products.filter(p=>p.links.some(link=>link.status==="proposed")).length===13);
 assert.ok(x.products.every(p=>p.links.every(link=>link.status!=="verified")));
});

test("one canonical style can span distinct subject categories and sort by family/preset",()=>{
 const x=index();
 const data=N.filter(x,{brand:"asyada-egitim",main:"Karuseller",style:"data-atlas",scope:"proposed"});
 assert.deepEqual(new Set(data.map(p=>p.groupId)),new Set([
  "instagram-burs-dosyasi-gks-2027-001","instagram-rotani-sec-tokyo-seoul-001",
  "instagram-tsinghua-atlas-2027","instagram-six-steps"
 ]));
 assert.deepEqual(new Set(data.map(p=>p.sub)),
  new Set(["Başvuru ve Burs Rehberleri","Şehir ve Öğrenci Yaşamı","Üniversite Tanıtımları"]));
 assert.equal(N.useStats(x,"data-atlas","asyada-egitim").subcategories,3);
 assert.equal(N.useStats(x,"data-atlas","asyada-egitim").verified,0);
 assert.equal(N.useStats(x,"data-atlas","asyada-egitim").proposed,4);
 assert.equal(N.filter(x,{style:"data-atlas",preset:"metrics-overview",scope:"proposed"}).length,2);
 const sorted=N.filter(x,{brand:"asyada-egitim",main:"Karuseller",sort:"style"});
 const keys=sorted.map(p=>p.match?.styleId||"zzzz");
 assert.deepEqual(keys,keys.slice().sort((a,b)=>a.localeCompare(b,"tr")));
 assert.equal(N.filter(x,{brand:"asyada-egitim",style:"data-atlas",scope:"verified"}).length,0);
 assert.equal(N.filter(x,{brand:"asyada-egitim",style:"unassigned"}).length,5);
});

test("style-first navigation can alias the same single product under two independently proven source styles",()=>{
 const nav=structuredClone(navigation);
 nav.confirmedVersions=[
  {groupId:"instagram-tsinghua-atlas-2027",versionId:"instagram-tsinghua-atlas-2027",
   styleId:"editorial-campaign",presetId:"photo-editorial",
   status:"verified",evidence:"https://github.com/cinegitim/design/pull/227"},
  {groupId:"instagram-tsinghua-atlas-2027",versionId:"instagram-tsinghua-atlas-2027-v2",
   styleId:"data-atlas",presetId:"metrics-overview",
   status:"verified",evidence:"https://github.com/cinegitim/design/pull/226"}
 ];
 const x=N.build(records,nav,registry);
 const styleFirst=N.filter(x,{mode:"style",brand:"asyada-egitim",scope:"verified"});
 const rows=styleFirst.filter(p=>p.groupId==="instagram-tsinghua-atlas-2027");
 assert.equal(rows.length,2);
 assert.deepEqual(new Set(rows.map(p=>p.match.styleId)),new Set(["editorial-campaign","data-atlas"]));
 assert.deepEqual(new Set(rows.map(p=>p.match.versionId)),
  new Set(["instagram-tsinghua-atlas-2027","instagram-tsinghua-atlas-2027-v2"]));
 const same=N.filter(x,{mode:"content",brand:"asyada-egitim",scope:"verified"})
  .filter(p=>p.groupId==="instagram-tsinghua-atlas-2027");
 assert.equal(same.length,1,"content navigation never clones the underlying product");
 assert.equal(x.products.length,19);
});

test("current cloud editing selection is a draft only and never a fabricated confirmed GitHub version",()=>{
 const first=index(),base=first.products.find(p=>p.groupId==="instagram-kaist-tech-track-2027-001");
 assert.ok(base.links.every(x=>x.status==="proposed"));
 const active=N.build(records,navigation,registry,{groupId:base.groupId,
  versionId:"instagram-kaist-tech-track-2027-001-v2",
  selection:{style_id:"data-atlas",preset_id:"comparison-led"}});
 const updated=active.products.find(p=>p.groupId===base.groupId);
 assert.equal(updated.links[0].status,"draft");
 assert.equal(updated.links[0].styleId,"data-atlas");
 assert.equal(updated.links[0].versionId,"instagram-kaist-tech-track-2027-001-v2");
 assert.equal(N.filter(active,{style:"data-atlas",scope:"verified"}).length,0);
 assert.equal(N.filter(active,{style:"data-atlas",scope:"draft"}).length,1);
});

test("cross-brand, cross-format, unknown product, forged approval, and bogus version fail closed",()=>{
 const wrong=structuredClone(navigation);
 wrong.items.find(x=>x.groupId==="cin-egitim-rollup").suggestion={
  styleId:"editorial-campaign",presetId:"institutional-paper",status:"proposed",scope:"future-design"};
 assert.throws(()=>N.build(records,wrong,registry));
 const unknown=structuredClone(navigation);
 unknown.items[0].groupId="nonexistent";
 assert.throws(()=>N.build(records,unknown,registry));
 const fake=structuredClone(navigation);
 fake.items[0].suggestion.status="approved";
 assert.throws(()=>N.build(records,fake,registry));
 const falseVersion=structuredClone(navigation);
 falseVersion.confirmedVersions=[{groupId:"instagram-tsinghua-atlas-2027",versionId:"unknown-v999",
  styleId:"data-atlas",presetId:"metrics-overview",status:"verified",evidence:"https://github.com/cinegitim/design/pull/1"}];
 assert.throws(()=>N.build(records,falseVersion,registry));
 const forged=structuredClone(navigation);
 forged.confirmedVersions=[{groupId:"instagram-tsinghua-atlas-2027",versionId:"instagram-tsinghua-atlas-2027-v2",
  styleId:"data-atlas",presetId:"metrics-overview",status:"verified",evidence:"http://evil.example/approve"}];
 assert.throws(()=>N.build(records,forged,registry));
});

test("UI is an accessible opt-in overlay; no auto save, no duplicate products, no new API",()=>{
 const html=read("index.html");
 for(const id of ["catalog-explore-toggle","catalog-navigator","nav-mode-content","nav-mode-style",
  "nav-brand","nav-main","nav-sub","nav-style","nav-preset","nav-scope","nav-sort",
  "nav-search","nav-results","nav-summary","nav-close"]){
  assert.ok(html.includes('id="'+id+'"'),"Missing "+id)
 }
 for(const file of ["catalog-navigation.js","catalog-navigator-ui.js"])
  assert.match(html,new RegExp('src="'+file.replace(".","\\.")+'"'));
 assert.match(html,/navigation-classification\.json/);
 assert.match(html,/canLeaveEditing\(\)/);
 assert.match(html,/refreshLibraryNavigation\(\)/);
 assert.match(html,/updateLibraryBreadcrumb\(\)/);
 assert.match(html,/styleUI\?\.sync\(\)/);
 assert.match(ui,/aria-pressed/);
 assert.match(ui,/statusText/);
 assert.match(ui,/\.dataset\.mode=mode/);
 assert.match(ui,/status==="proposed"/);
 assert.doesNotMatch(script+ui,/fetch\(|XMLHttpRequest|localStorage|api\.github\.com|fetch\s*\(/);
});

import assert from "node:assert/strict";
import {test} from "node:test";
import fs from "node:fs";
import vm from "node:vm";
import crypto from "node:crypto";
import path from "node:path";

const root=path.resolve(import.meta.dirname,"../../..");
const browser=path.join(root,"docs/visual-editor/browser");
const script=fs.readFileSync(path.join(browser,"style-selection.js"),"utf8");
const registry=JSON.parse(fs.readFileSync(path.join(browser,"style-registry.json"),"utf8"));
const ctx={};vm.runInNewContext(script,ctx);
const S=ctx.BrandstudioStyleSelection;
const style=registry.styles.find(x=>x.style_id==="editorial-campaign");
const baseline=()=>({brand:"asyada-egitim",category:"instagram-carousel",style_id:"editorial-campaign",
  preset_id:"institutional-paper",lockup_id:"H-02/dark",overrides:{}});

test("static registry is derived exactly from canonical Git sources",()=>{
 assert.equal(registry.schema,1);
 assert.ok(registry.categories.some(x=>x.id==="instagram-carousel"));
 assert.equal(style.version,"0.1.1");
 assert.equal(style.status,"review-only");
 const raw=fs.readFileSync(path.join(root,style.source_path));
 const gitBlob=crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob "+raw.length+"\0"),raw])).digest("hex");
 assert.equal(style.source_blob_sha,gitBlob);
 const src=JSON.parse(raw);
 assert.deepEqual(JSON.parse(JSON.stringify(style.presets)),src.presets);
 assert.deepEqual(JSON.parse(JSON.stringify(style.variation_axes)),src.variation_axes);
 assert.deepEqual(JSON.parse(JSON.stringify(style.palette)),src.hard_locks.palette_tokens);
 assert.deepEqual(style.lockups.map(x=>x.id),src.hard_locks.lockup_options);
 for(const lockup of style.lockups)
  assert.equal(crypto.createHash("sha256").update(fs.readFileSync(path.join(root,lockup.path))).digest("hex"),lockup.sha256);
});

test("all executor types resolve the same immutable selected style",()=>{
 const x=S.resolve(registry,baseline());
 assert.equal(x.schema,1);assert.equal(x.style_version,"0.1.1");
 assert.equal(x.style_source_blob_sha,style.source_blob_sha);
 assert.equal(x.lockup_sha256,style.lockups.find(x=>x.id==="H-02/dark").sha256);
 assert.equal(x.approval_status,"review-only");
 assert.equal(x.variation.color_mode,"paper-dominant");
 assert.equal(x.font_family,"Jost");
 assert.equal(x.palette.red,"#BD2120");
 assert.equal(S.validate(registry,x),true);
 assert.equal(JSON.stringify(x),JSON.stringify(S.resolve(registry,{...baseline(),executor:"chatgpt-work"})));
});

test("presets and controlled axes differ while canonical identity stays exact",()=>{
 const a=S.resolve(registry,baseline());
 const b=S.resolve(registry,{...baseline(),preset_id:"photo-editorial",overrides:{photo_density:"low"}});
 assert.equal(a.lockup_sha256,b.lockup_sha256);
 assert.notEqual(a.variation.layout_rhythm,b.variation.layout_rhythm);
 assert.equal(b.variation.photo_density,"low");
 assert.equal(b.palette.ink,a.palette.ink);
});

test("bad style category, retired logo, or impossible variation fail closed",()=>{
 for(const input of [
  {...baseline(),category:"social-post"},
  {...baseline(),lockup_id:"D-04/dark"},
  {...baseline(),preset_id:"missing-preset"},
  {...baseline(),overrides:{photo_density:"neon"}},
  {...baseline(),overrides:{logo_geometry:"retype"}},
 ])assert.throws(()=>S.resolve(registry,input));
 const x=S.resolve(registry,baseline());
 for(const changed of [
  {...x,style_version:"100.0.0"}, {...x,lockup_sha256:"0".repeat(64)},
  {...x,palette:{...x.palette,ink:"#ff00ff"}}, {...x,approval_status:"approved"},
 ])assert.throws(()=>S.validate(registry,changed));
});

test("legacy editor state stays valid; selection round trips through cloud and archives",()=>{
 const codecSrc=fs.readFileSync(path.join(browser,"portable.js"),"utf8"),scope={};
 vm.runInNewContext(codecSrc,scope);
 const codec=scope.BrandstudioPortable;
 const old={colors:{paper:"#f7f3e9",red:"#bd2120",ink:"#1d2027"},edits:{},groups:{}};
 assert.equal(codec.validateState(old,5).designStyle,undefined);
 const selection=S.resolve(registry,baseline());
 const updated={...old,designStyle:selection};
 const checked=codec.validateState(updated,5);
 assert.equal(checked.designStyle.lockup_sha256,selection.lockup_sha256);
 const doc=codec.makeArchive("carousel-01-v3",[{version:2,note:"style",state:updated}],updated);
 const re=codec.parseArchive(doc,"carousel-01-v3",5);
 assert.equal(re.current.designStyle.preset_id,selection.preset_id);
 assert.equal(re.versions[0].state.designStyle.style_source_blob_sha,selection.style_source_blob_sha);
 for(const extra of ["<svg onload=alert(1)>",42,{foo:"bar"}])
  assert.throws(()=>codec.validateState({...old,designStyle:extra},5));
});

test("production brief is a GitHub-PR input, not a fake publication",()=>{
 const choice=S.resolve(registry,baseline());
 const out=S.productionBrief({selection:choice,product:"instagram-kaist-tech-track-2027-001-v2",version:3});
 assert.equal(out.selection.style_id,"editorial-campaign");
 assert.equal(out.origin,"brandstudio-visual-editor");
 assert.equal(out.github.status,"not-submitted");
 assert.equal(out.approval.creative,"pending");
 assert.equal(out.approval.social_published,false);
 assert.equal(out.product,"instagram-kaist-tech-track-2027-001-v2");
 assert.throws(()=>S.productionBrief({selection:choice,product:"../bad",version:3}));
});

test("editor has opt-in picker and does not automatically restyle existing slides",()=>{
 const html=fs.readFileSync(path.join(browser,"index.html"),"utf8");
 for(const id of ["design-language-panel","style-category","style-family","style-preset","style-axes","style-logo","style-save","style-export","style-status"])
  assert.ok(html.includes('id="'+id+'"'),"Missing "+id);
 assert.ok(html.includes('src="style-selection.js"'));
 assert.ok(html.includes("fetch('style-registry.json'"));
 assert.match(html,/state\.designStyle\s*=\s*selection/);
 assert.ok(html.includes("dirtyStatus()"));
 assert.ok(html.includes("styleModule.productionBrief"));
 assert.doesNotMatch(script,/fetch\(|api\.github\.com|cloudflare\.com/);
});

test("Cloudflare gateway permits valid style revision and rejects forged style fields",async()=>{
 const {onRequestPost}=await import("../asya-gateway/worker.mjs");
 const selection=S.resolve(registry,baseline());
 let forwarded=false;
 const env={BRANDSTUDIO_OBJECTS:{idFromName:x=>x,get:()=>({fetch:async req=>{forwarded=true;return new Response(await req.text(),{status:200})}})}};
 const state={colors:{paper:"#f7f3e9",ink:"#1d2027",red:"#bd2120"},edits:{},groups:{},designStyle:selection};
 const post=async data=>{
  forwarded=false;
  const req=new Request("https://studio.asyadaegitim.com/visual-editor/api/revisions?product=carousel-01-v3",{
   method:"POST",headers:{"origin":"https://studio.asyadaegitim.com","X-Brandstudio-Editor":"1","Content-Type":"application/json"},
   body:JSON.stringify({product:"carousel-01-v3",version:2,state:data,expectedSha:null})
  });
  const response=await onRequestPost({authenticated:true,request:req,env});
  return {status:response.status,forwarded};
 };
 const yes=await post(state);
 assert.equal(yes.status,200);assert.equal(yes.forwarded,true);
 for(const bad of [
  {...state,designStyle:{...selection,lockup_id:"D-04/dark"}},
  {...state,designStyle:{...selection,style_version:"<script>"}},
  {...state,designStyle:{...selection,variation:{bad:"javascript:alert(1)"}}},
  {...state,designStyle:{...selection,unknown:"extra"}}
 ]){const no=await post(bad);assert.equal(no.status,400);assert.equal(no.forwarded,false)}
});

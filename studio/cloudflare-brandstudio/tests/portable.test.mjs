import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {test} from "node:test";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "../../..");
const portableSource = fs.readFileSync(path.join(root,"docs/visual-editor/browser/portable.js"),"utf8");
const editor = fs.readFileSync(path.join(root,"docs/visual-editor/browser/index.html"),"utf8");
const scope = {};
vm.runInNewContext(portableSource,scope);
const codec=scope.BrandstudioPortable;
const fresh=()=>({colors:{paper:"#F7F3E9",ink:"#1D2027",red:"#BD2120"},edits:{"0:2":{styles:{left:"100px",top:"300px",width:"500px",margin:"0",position:"absolute"},mode:"direct",color:"#AABBCC"}}});

test("valid source-based state and archive round-trip",()=>{
  const validated=codec.validateState(fresh(),5);
  assert.equal(validated.colors.paper,"#f7f3e9");
  const a=codec.makeArchive("carousel-01-v3",[{version:2,note:"A",state:fresh(),time:"2026"}],fresh());
  const imported=codec.parseArchive(a,"carousel-01-v3",5);
  assert.equal(imported.versions.length,1);
  assert.equal(imported.current.edits["0:2"].color,"#aabbcc");
});
test("reject other product, brand, or revision format",()=>{
  const backup=codec.makeArchive("carousel-01-v3",[],fresh());
  assert.throws(()=>codec.parseArchive(backup,"different-product",5));
  const other={...backup,brand:"other"};
  assert.throws(()=>codec.parseArchive(other,"carousel-01-v3",5));
  assert.throws(()=>codec.parseArchive({...backup,schema:1},"carousel-01-v3",5));
});
test("reject malicious CSS and impossible page keys",()=>{
  let s=fresh();s.edits["0:2"].styles.background="url(https://example.com)";
  assert.throws(()=>codec.validateState(s,5),/CSS/);
  s=fresh();s.edits["10:2"]={styles:{},mode:"inherit"};
  assert.throws(()=>codec.validateState(s,5),/slayt/);
  s=fresh();s.colors.red="var(--red);background:url(https://example.com)";
  assert.throws(()=>codec.validateState(s,5),/renk/);
});
test("reject malformed version chains and oversized states",()=>{
  const a=codec.makeArchive("carousel-01-v3",[],fresh());
  a.versions=[{version:2,note:"a",state:fresh()},{version:2,note:"b",state:fresh()}];
  assert.throws(()=>codec.parseArchive(a,"carousel-01-v3",5),/sürüm/);
  const s=fresh();for(let i=0;i<480;i++)s.edits["0:"+i]={styles:{left:"123px",top:"456px",width:"789px"},mode:"inherit"};
  assert.throws(()=>codec.validateState(s,5),/32 KB/);
});
test("editor provides explicit portable controls and no cloud write endpoint",()=>{
  assert.match(editor,/id="importFile"/);
  assert.match(editor,/id="export"/);
  assert.match(editor,/portable\.js/);
  assert.match(editor,/getDirectoryHandle\('versions'/);
  assert.match(editor,/getDirectoryHandle\(dirname,\{create:false\}\)/);
  assert.match(editor,/sourceAt\(i\)/);
  assert.doesNotMatch(editor,/method\s*:\s*['"]POST/);
  assert.doesNotMatch(portableSource,/fetch\(/);
});
test("valid JavaScript syntax in source and embedded editor",()=>{
  assert.ok(new vm.Script(portableSource));
  const embedded=editor.match(/<script>\s*([\s\S]*?)\s*<\/script>/);
  assert.ok(embedded);
  assert.ok(new vm.Script(embedded[1]));
});

test("text editing is constrained to text nodes and rejects identity overrides",()=>{
 const draft=fresh();draft.edits["0:2"].segments=["Yeni başlık", "metin"];
 const a=codec.parseArchive(codec.makeArchive("carousel-01-v3",[],draft),"carousel-01-v3",5);
 assert.equal(a.current.edits["0:2"].segments[0],"Yeni başlık");
 const el={ownerDocument:{createTreeWalker(){const ns=[{nodeValue:"eski"},{nodeValue:"parça"}];let i=0;return{nextNode(){return ns[i++]||null}}}}};
 codec.applyText(el,a.current.edits["0:2"].segments);
 assert.throws(()=>codec.applyText(el,["single"]),/yapısı/);
 const s=fresh();s.edits["0:2"].segments=["".padEnd(1601,"a")];
 assert.throws(()=>codec.validateState(s,5),/metin|Metin/);
 assert.match(portableSource,/function locked\(el\)/);
 assert.match(portableSource,/identityGuard\(el,edit\)/);
});

test("linked groups round trip in schema 2 and remain optional in older archives",()=>{
 const a=fresh();a.groups={"0":[[0,2],[3,4]]};
 const packed=codec.makeArchive("carousel-01-v3",[{version:2,note:"group",state:a}],a);
 assert.deepEqual(JSON.parse(JSON.stringify(codec.parseArchive(packed,"carousel-01-v3",5).current.groups)),{"0":[[0,2],[3,4]]});
 const old=fresh();delete old.groups;
 assert.deepEqual(JSON.parse(JSON.stringify(codec.validateState(old,5).groups)),{});
 assert.equal(packed.schema,2);
});
test("reject malformed, duplicated, overlapping and oversized group references",()=>{
 const bad=[
  {"0":[[1,2],[2,3]]},
  {"0":[[1,1]]},
  {"0":[[1]]},
  {"9":[[1,2]]},
  {"0":[[1,-2]]},
  {"0":[[1,501]]},
  {"0":[Array.from({length:25},(_,i)=>i)]},
  Object.fromEntries([["__proto__",[[1,2]]]])
 ];
 for(const groups of bad){const s=fresh();s.groups=groups;assert.throws(()=>codec.validateState(s,5))}
});

test("embedded WebP photo data round-trips through existing schema 2 with content",()=>{
 const data="data:image/webp;base64,"+"U".repeat(64);
 const a=fresh();a.edits["0:3"]={mode:"inherit",styles:{"object-fit":"cover","object-position":"50% 45%"},image:data};
 const saved=codec.validateState(a,5);
 assert.equal(saved.edits["0:3"].image,data);
 const archive=codec.makeArchive("carousel-01-v3",[{version:2,note:"local image",time:"2026",state:a}],a);
 assert.equal(archive.schema,2);
 const restored=codec.parseArchive(archive,"carousel-01-v3",5);
 assert.equal(restored.current.edits["0:3"].image,data);
 assert.equal(restored.versions[0].state.edits["0:3"].image,data);
 const old=codec.validateState(fresh(),5);
 assert.ok(!old.edits["0:2"].image);
});

test("photo replacements reject remote URLs, SVG and unsafe or oversized payloads",()=>{
 const good="data:image/webp;base64,"+"U".repeat(64);
 const bad=[
  "https://example.com/image.jpg","data:image/svg+xml;base64,"+"U".repeat(64),
  "data:text/html;base64,"+"U".repeat(64),"data:image/webp;base64,###",
  "data:image/jpeg;base64,"+"U".repeat(260001),"data:image/webp;base64,abc"
 ];
 for(const uri of bad){
  const s=fresh();s.edits["0:3"]={mode:"inherit",styles:{},image:uri};
  assert.throws(()=>codec.validateState(s,5));
 }
 const s=fresh();
 for(let i=0;i<9;i++)s.edits["1:"+i]={mode:"inherit",styles:{},image:good};
 assert.throws(()=>codec.validateState(s,5),/en fazla 8/);
});

test("photo patch is only permitted on normal img nodes, not locked identity",()=>{
 const uri="data:image/webp;base64,"+"U".repeat(64);
 const attrs={},img={tagName:"IMG",classList:{contains:()=>false},closest:()=>null,
  setAttribute(k,v){attrs[k]=v},style:{setProperty(){}}};
 const el={tagName:"DIV",classList:{contains:()=>false},closest:()=>null,style:{setProperty(){}}};
 assert.match(portableSource,/if\(el\.tagName!=='IMG'\)err/);
 assert.match(portableSource,/identityGuard\(el,edit\)/);
 assert.doesNotMatch(portableSource,/eval\(/);
 assert.ok(uri.startsWith("data:image/webp;base64,"));
});

test("photo editor provides browser-only image selection and reversible source changes",()=>{
 for(const id of ["photoFile","replace-photo","reset-photo","photo-status"])assert.match(editor,new RegExp('id="'+id+'"'));
 for(const token of ["createImageBitmap(file)","canvas.toDataURL('image/webp'","imageFromLocalFile(file)","delete state.edits[key].image","src:n.getAttribute('src')","n.setAttribute('src',original.src)","codec.validateState(candidate,pages.length)"]){
  assert.ok(editor.includes(token),"Missing local photo behavior "+token);
 }
 assert.doesNotMatch(editor,/method\s*:\s*['"]POST/);
 assert.doesNotMatch(editor,/R2\.put/);
});

test("backing band colour is archive-safe; unsafe CSS is rejected",()=>{
 let t=fresh();t.edits["0:4"]={mode:"inherit",styles:{"background-color":"#ff5599",position:"absolute",width:"800px",height:"200px"}};
 const archive=codec.makeArchive("carousel-01-v3",[{version:2,note:"band",state:t}],t);
 assert.equal(codec.parseArchive(archive,"carousel-01-v3",5).current.edits["0:4"].styles["background-color"],"#ff5599");
 t.edits["0:4"].styles["background-color"]="url(javascript:malicious)";
 assert.throws(()=>codec.validateState(t,5));
});
test("canonical artwork can be repositioned and proportionally resized, not replaced or distorted",()=>{
 const doc=(name,cls,ancestor)=>({tagName:name,classList:{contains:k=>cls===k},
  closest:q=>q==='.logo-foot'&&ancestor?{}:null});
 assert.match(portableSource,/function identityGuard\(el,e\)/);
 assert.match(portableSource,/if\(e\.image!==undefined\|\|e\.segments!==undefined/);
 assert.match(portableSource,/if\(!allowed\[k\]\)err/);
 assert.doesNotMatch(portableSource,/minimum 352 px/);
 assert.match(portableSource,/function locked\(el\)\{return false\}/);
 assert.match(portableSource,/identityGuard\(el,e\)/);
 assert.ok(doc('IMG','anything',true).closest('.logo-foot'));
});

test("max-width escape hatch permits only safe none value on author-requested resize",()=>{
 const s=fresh();s.edits["0:2"].styles["max-width"]="none";
 assert.equal(codec.validateState(s,5).edits["0:2"].styles["max-width"],"none");
 s.edits["0:2"].styles["max-width"]="url(javascript:unsafe)";
 assert.throws(()=>codec.validateState(s,5),/max-width/);
});

test("font-family export safely round-trips only approved families",()=>{
 const d=fresh();d.edits["0:2"].styles["font-family"]="Georgia";
 const archive=codec.makeArchive("carousel-01-v3",[],d);
 assert.equal(codec.parseArchive(archive,"carousel-01-v3",5).current.edits["0:2"].styles["font-family"],"Georgia");
 d.edits["0:2"].styles["font-family"]="serif;url(evil)";
 assert.throws(()=>codec.validateState(d,5),/font/);
});

test("logo artboard coordinate basis is portable and rejects unknown basis",()=>{
 const s=fresh();
 s.edits["0:5"]={styles:{position:"absolute",left:"64px",top:"960px",width:"300px",right:"auto",bottom:"auto",margin:"0"},mode:"inherit",basis:"artboard"};
 const archive=codec.makeArchive("carousel-01-v3",[{version:2,note:"Independent logo",state:s}],s);
 const restored=codec.parseArchive(archive,"carousel-01-v3",5);
 assert.equal(restored.current.edits["0:5"].basis,"artboard");
 assert.equal(restored.versions[0].state.edits["0:5"].styles.left,"64px");
 s.edits["0:5"].basis="parent";
 assert.throws(()=>codec.validateState(s,5),/koordinat temeli/);
});
test("existing carousel fonts are backed by actual repository assets and safe values",()=>{
 for(const font of ["Jost","SongCJK","Manrope","SourceSerif","Hiragino Sans","Yu Gothic","Apple SD Gothic Neo","Noto Sans KR"]){
  assert.ok(codec.fonts.includes(font),"Missing existing brand font: "+font);
  const s=fresh();s.edits["0:2"].styles["font-family"]=font;
  assert.equal(codec.validateState(s,5).edits["0:2"].styles["font-family"],font);
 }
 for(const pathPart of ["instagram/carousel-01-v3/assets/Jost-VF.ttf",
 "instagram/basvuru-rehberi-001-cince-bilmeden/assets/SongtiSC-CJK-subset.ttf",
 "cin-egitim/social-avatars-02/assets/manrope-normal-latin.woff2",
 "cin-egitim/social-avatars-02/assets/source-serif-4-normal-latin.woff2"]){
  assert.ok(portableSource.includes(pathPart),"Registered asset URL absent: "+pathPart);
 }
 const bad=fresh();bad.edits["0:2"].styles["font-family"]="Manrope;url(//evil.invalid/font)";
 assert.throws(()=>codec.validateState(bad,5));
});
test("portable export detaches canonical logo before applying revisions",()=>{
 assert.match(portableSource,/function detachLogo\(doc\)/);
 assert.match(portableSource,/band\.after\(img\)/);
 assert.match(portableSource,/img\.setAttribute\(LOGO_MARKER,'true'\)/);
 assert.match(portableSource,/detachLogo\(doc\);installFonts\(doc,sourceUrl\)/);
 assert.match(portableSource,/function adaptLogoEdit\(doc,el,edit,selectedState,index\)/);
 assert.match(portableSource,/identityGuard\(el,edit\)/);
 assert.match(portableSource,/el\.hasAttribute\(LOGO_MARKER\)/);
});

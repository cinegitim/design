import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {test} from "node:test";
import path from "node:path";
const root=path.resolve(import.meta.dirname,"../../..");
const uxSource=fs.readFileSync(path.join(root,"docs/visual-editor/browser/ux.js"),"utf8");
const html=fs.readFileSync(path.join(root,"docs/visual-editor/browser/index.html"),"utf8");
const scope={};vm.runInNewContext(uxSource,scope);const UX=scope.BrandstudioUX;
const entry=(id,props={})=>({id,isText:true,isPhoto:false,isLogo:false,isFooter:false,rect:{x:20,y:20,w:250,h:50},...props});

test("photo and overlaid type are in the same accordion",()=>{
 const list=[entry(0),entry(1,{isText:false,isPhoto:true,rect:{x:400,y:450,w:300,h:330}}),entry(2,{rect:{x:430,y:500,w:190,h:90}}),entry(3,{isLogo:true,rect:{x:10,y:1190,w:300,h:100}}),entry(4,{isFooter:true})];
 const groups=UX.groupLayers(list);const photo=groups.find(x=>x.id==="photo-0");
 assert.ok(photo);
 assert.deepEqual(Array.from(photo.items,x=>x.id),[1,2]);
 assert.deepEqual(Array.from(groups.find(x=>x.id==="identity").items,x=>x.id),[3,4]);
 assert.ok(groups.find(x=>x.id==="copy").items.some(x=>x.id===0));
});
test("two photos form independent named accordions",()=>{
 const list=[entry(0,{isText:false,isPhoto:true,rect:{x:50,y:450,w:240,h:280}}),entry(1,{isText:false,isPhoto:true,rect:{x:640,y:450,w:240,h:280}}),entry(2,{rect:{x:90,y:470,w:170,h:60}}),entry(3,{rect:{x:690,y:470,w:170,h:60}})];
 const groups=UX.groupLayers(list);
 assert.equal(groups.filter(x=>x.id.startsWith("photo-")).length,2);
 assert.deepEqual(Array.from(groups.find(x=>x.id==="photo-0").items,x=>x.id),[0,2]);
 assert.deepEqual(Array.from(groups.find(x=>x.id==="photo-1").items,x=>x.id),[1,3]);
});
test("undo/redo history is bounded and branching resets redo",()=>{
 const h=UX.createHistory(2);
 let state={x:0};
 h.checkpoint(state);state.x=10;
 h.checkpoint(state);state.x=20;
 h.checkpoint(state);state.x=30;
 assert.equal(h.status().undo,2);
 state=h.undo(state);assert.equal(state.x,20);
 state=h.undo(state);assert.equal(state.x,10);
 assert.equal(h.undo(state),null);
 state=h.redo(state);assert.equal(state.x,20);
 h.checkpoint(state);state.x=99;
 assert.equal(h.redo(state),null);
 h.clear();assert.equal(h.status().undo,0);
});
test("state snapshots do not mutate saved versions",()=>{
 const h=UX.createHistory();
 const initial={colors:{ink:"#111111"},edits:{"0:1":{styles:{left:"10px"}}}};
 h.checkpoint(initial);
 initial.edits["0:1"].styles.left="120px";
 const reverted=h.undo(initial);
 assert.equal(reverted.edits["0:1"].styles.left,"10px");
 assert.equal(initial.edits["0:1"].styles.left,"120px");
});
test("UI includes real accordion, slide strip, keyboard handling and identity lock",()=>{
 assert.match(html,/id="groups-open"/);
 assert.match(html,/className='layer-group'/);
 assert.match(html,/document\.createElement\('details'\)/);
 assert.match(html,/id="slide-tabs"/);
 assert.match(html,/id="undo"/);assert.match(html,/id="redo"/);
 assert.match(html,/history\.checkpoint\(state\)/);
 assert.match(html,/ev\.key==='ArrowRight'/);
 assert.match(html,/function identityImage\(n\)/);
 assert.match(html,/src="ux\.js"/);
 assert.doesNotMatch(html,/fetch\([^)]*,\s*\{\s*method:\s*['"]POST/);
 const embedded=html.match(/<script>\s*([\s\S]*?)\s*<\/script>/);
 assert.ok(embedded);assert.ok(new vm.Script(embedded[1]));
 assert.ok(new vm.Script(uxSource));
});

test("shift selection toggles whole linked groups and keeps unrelated members",()=>{
 const eq=(a,b)=>assert.deepEqual(Array.from(a),b);
 eq(UX.selectionTargets([],2,[[2,4]],false),[2,4]);
 eq(UX.selectionTargets([1],2,[[2,4]],true),[1,2,4]);
 eq(UX.selectionTargets([1,2,4],4,[[2,4]],true),[1]);
 eq(UX.selectionTargets([1,2],3,[],true),[1,2,3]);
 eq(UX.selectionTargets([1,2],2,[],true),[1]);
});
test("linked group sections are distinct from photo accordion heuristics",()=>{
 const entries=[entry(0),entry(1),entry(2,{isLogo:true}),entry(3,{isPhoto:true,isText:false})];
 const sections=UX.groupLayers(entries,[[0,1]]);
 const linked=sections.find(x=>x.id==="linked-0");
 assert.ok(linked);
 assert.equal(linked.label,"Bağlı grup 1");
 assert.deepEqual(Array.from(linked.items,x=>x.id),[0,1]);
 assert.ok(sections.find(x=>x.id==="identity").items.some(x=>x.id===2));
 assert.ok(!UX.groupLayers(entries,[[0,2]]).some(x=>x.id==="linked-0"));
});
test("union bounds include each selected object's dimensions",()=>{
 const b=UX.bounds([{x:64,y:90,w:100,h:40},{x:220,y:150,w:70,h:130}]);
 assert.deepEqual({...b},{x:64,y:90,w:226,h:190});
});
test("group controls and transforms are wired and exclude locked identity",()=>{
 for(const id of ["selection-tools","selection-summary","link-group","unlink-group","multi-align"])assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(html,/choose\(item\.id,ev\.shiftKey\)/);
 assert.match(html,/ux\.selectionTargets\(selectedIds,i,linkedGroups\(\),!!extend\)/);
 assert.match(html,/function linkedGroups\(/);
 assert.match(html,/state\.groups\[String\(page\)\]=next/);
 assert.match(html,/state\.groups\[String\(page\)\]=rest/);
 assert.match(html,/selectedIds\.map\(function\(i\)\{return nodes\(\)\[i\]\}\)/);
 assert.match(html,/snapshots=ids\.filter\(function\(i\)\{return editable\(ns\[i\]\)\}\)\.map\(function\(i\)\{return\{id:i,node:ns\[i\],p:pos\(ns\[i\]\)\}\}\)/);
 assert.match(html,/snapshots\.forEach\(function\(item\)\{/);
 assert.match(html,/if\(evt\.shiftKey\)\{choose\(index,true\)/);
});

test("pointer drag re-anchors a multi-selection to the grabbed member",()=>{
 assert.match(html,/if\(!wasSelected\)choose\(index,false\);else\{sel=index;showSelection\(\)\}/);
 assert.match(html,/var start=pos\(n\),sx=evt\.clientX,sy=evt\.clientY/);
 assert.match(html,/setXY\(start\.x\+e\.clientX-sx,start\.y\+e\.clientY-sy\)/);
});

test("context menu operates on current selection and snapping keeps undo semantics",()=>{
 assert.match(html,/b\.oncontextmenu=function\(ev\)/);
 assert.match(html,/document\.addEventListener\('pointerdown',function\(e\)/);
 assert.match(html,/closeContextMenu\(\)/);
 assert.match(html,/if\(action==='front'\|\|action==='back'\)/);
 assert.match(html,/if\(action==='reset'\)/);
 assert.match(html,/refreshPreview\(\);dirtyStatus\(\)/);
 assert.match(html,/var snapshots=ids\.filter/);
});

test("resize math handles proportional corners, sides and relative child scaling",()=>{
 const box={x:40,y:60,w:200,h:100};
 const e=UX.resizeRect(box,"e",35,0,false);
 assert.deepEqual({...e},{x:40,y:60,w:235,h:100});
 const shift=UX.resizeRect(box,"e",35,0,true);
 assert.equal(shift.w,235);assert.equal(shift.h,117.5);
 assert.equal(shift.y,51.25);
 const nw=UX.resizeRect(box,"nw",20,10,true);
 assert.equal(Math.round(nw.w/nw.h*100),200);
 assert.equal(nw.x+nw.w,240);
 assert.equal(nw.y+nw.h,160);
 const child=UX.scaleRect({x:60,y:80,w:60,h:20},box,{x:40,y:60,w:400,h:200});
 assert.deepEqual({...child},{x:80,y:100,w:120,h:40});
 const floor=UX.resizeRect({x:0,y:0,w:200,h:100},"w",195,0,true);
 assert.ok(floor.w>=20&&floor.h>=20);
});
test("rulers are outside frame and keyboard handles iframe and redo",()=>{
 const expected='<div class="ruler-stage" id="ruler-stage">';
 assert.ok(html.includes(expected));
 const frame=html.slice(html.indexOf('<div class="canvas"'),html.indexOf('</main>'));
 assert.ok(frame.indexOf('id="ruler-x"')<frame.indexOf('class="frame" id="frame"'));
 assert.ok(frame.indexOf('id="ruler-y"')<frame.indexOf('class="frame" id="frame"'));
 assert.doesNotMatch(frame.slice(frame.indexOf('id="frame"')),/<canvas id="ruler-x"/);
 assert.match(html,/doc\.addEventListener\('keydown',editorKeydown\)/);
 assert.match(html,/doc\.addEventListener\('keyup',editorKeyup\)/);
 assert.match(html,/function editorKeydown\(ev\)/);
 assert.match(html,/ev\.shiftKey\?\$\('redo'\):\$\('undo'\)/);
 assert.match(html,/var p=pos\(n\),step=ev\.shiftKey\?10:1/);
 assert.match(html,/if\(!dragging&&!keyboardNudging\)checkpoint\(\)/);
});
test("selection frame scales selected objects and descendants with Shift",()=>{
 assert.match(html,/var targets=new Set\(selected\)/);
 assert.match(html,/node\.querySelectorAll\('\[data-edit-index\]'\)/);
 assert.match(html,/ux\.resizeRect\(initial,direction,dx,dy,alwaysProportional\|\|ev\.shiftKey\)/);
 assert.match(html,/ux\.scaleRect\(item\.rect,initial,to\)/);
 assert.match(html,/var size=Math\.max\(8,Math\.min\(260,/);
 assert.match(html,/handle\.hidden=!list\.length/);
});

test("artboard has a real pasteboard and selection can leave its edges",()=>{
 assert.match(html,/PASTEBOARD=320/);
 assert.match(html,/function installPasteboard\(/);
 assert.match(html,/\.slide\{margin:'\+PASTEBOARD\+'px!important;overflow:visible!important/);
 assert.match(html,/\(DESIGN_W\+PASTEBOARD\*2\)/);
 assert.match(html,/gridTemplateColumns='25px '/);
});
test("compact independent side panels with searchable layer list",()=>{
 for(const id of ["toggle-left","toggle-right","layer-search","layer-path","font","fs","x","y"])
  assert.match(html,new RegExp('id="'+id+'"'));
 assert.doesNotMatch(html,/Fotoğraf ve yazılar ilişkili başlıklarda gösterilir/);
 assert.doesNotMatch(html,/Kaydettiğin sürümler/);
 assert.match(html,/function setupSidebars\(/);
 assert.match(html,/function syncInspectorSections\(/);
 assert.match(html,/\$\('layer-search'\)\.oninput=function\(\)\{layers\(\)\}/);
 const start=html.indexOf('<div class="panel primary-properties">'),end=html.indexOf('</div></div>',start);
 const first=html.slice(start,end);
 assert.ok(first.indexOf('id="font"')<first.indexOf('id="fs"'));
 assert.ok(first.indexOf('id="fs"')<first.indexOf('id="x"'));
 assert.ok(first.indexOf('id="x"')<first.indexOf('id="y"'));
});
test("layer drag reorder persists z-index, supports undo and shows read-only path",()=>{
 for(const token of ["function moveLayer(source,target,before)","b.draggable=true","dragstart","dragover","drop","moveLayer(source,item.id)","entry.styles['z-index']=String(index+1)","checkpoint();","function layerPath(i)"])
  assert.ok(html.includes(token),"Missing stacking control "+token);
});
test("inline click-to-type caret saves only valid segments, with undo",()=>{
 for(const token of ["function beginInlineText(n,x,y)","function endInlineText()","doc.caretRangeFromPoint","n.setAttribute('contenteditable','true')","n.addEventListener('beforeinput'","n.addEventListener('input'","codec.validateState(draft,pages.length)","beginInlineText(n,e.clientX,e.clientY)"])
  assert.ok(html.includes(token),"Missing inline text behavior "+token);
 assert.match(html,/ev\.target\?\.isContentEditable/);
});
test("Shift type scaling and stationary logo during band movement",()=>{
 assert.match(html,/\(ev\.shiftKey\|\|members\.length>1\)/);
 assert.match(html,/var stationary=snapshots\.filter/);
 assert.match(html,/stationary\.forEach\(function\(item\)\{setRectangle\(item\.node,item\.p,false\)\}/);
});

test("canvas clicks alternate layer selection, inline caret and layer selection again",()=>{
 assert.match(html,/if\(inlineEditing===n&&!evt\.shiftKey\)\{[\s\S]*?endInlineText\(\);evt\.preventDefault\(\);return/);
 assert.match(html,/var index=Number\(n\.dataset\.editIndex\),wasSelected=selectedIds\.includes\(index\)/);
 assert.match(html,/if\(!wasSelected\)choose\(index,false\)/);
 assert.match(html,/if\(!moved&&wasSelected&&selectedIds\.length===1&&textEligible\(n\)\)beginInlineText/);
 assert.match(html,/n\.setAttribute\('contenteditable','true'\)/);
 assert.match(html,/n\.removeAttribute\('contenteditable'\)/);
});
test("Backspace/Delete remove selected layers but preserve native text editing",()=>{
 assert.match(html,/function deleteSelection\(\)/);
 assert.match(html,/if\(ev\.target\?\.isContentEditable\)return;/);
 assert.match(html,/ev\.key==='Backspace'\|\|ev\.key==='Delete'/);
 assert.match(html,/if\(inlineEditing\|\|sel<0\|\|!selectedIds\.length\)return/);
 assert.match(html,/e\.styles\.display='none';patch\(ns\[i\],e\)/);
 assert.match(html,/selectedIds=\[\];sel=-1;/);
 assert.match(html,/filter\(function\(item\)\{return !isDeleted\(item\.id\)\}\)/);
 assert.match(html,/data-action="delete"/);
 assert.match(html,/if\(action==='delete'\)\{deleteSelection\(\);return\}/);
});

const catalogSource=fs.readFileSync(path.join(root,"docs/visual-editor/browser/catalog.js"),"utf8");
const adapterSource=fs.readFileSync(path.join(root,"docs/visual-editor/browser/adapter.js"),"utf8");
const catCtx={},adaptCtx={};vm.runInNewContext(catalogSource,catCtx);vm.runInNewContext(adapterSource,adaptCtx);
const Catalog=catCtx.BrandstudioCatalog,Adapter=adaptCtx.BrandstudioAdapter;
test("public catalog discovers new future HTML/SVG/raster outputs without registration",()=>{
 const entries=Catalog.fromPaths([
  "docs/instagram/future-campus/source/01-cover.html",
  "docs/instagram/future-campus/source/02-life.html",
  "docs/cin-egitim/rollup/new-banner.html",
  "docs/social-covers/2027/new-01.png",
  "docs/social-covers/2027/new-02.svg",
  "docs/../private.png"
 ]);
 const products=Array.from(entries,r=>({id:r.id,kind:r.kind,pages:Array.from(r.pages)}));
 assert.ok(products.some(r=>r.id==="instagram-future-campus"&&r.pages.length===2));
 assert.ok(products.some(r=>r.id==="cin-egitim-rollup-new-banner"&&r.kind==="html"));
 assert.ok(products.some(r=>r.kind==="image"&&r.pages.length===2));
 assert.ok(products.every(r=>r.pages.every(p=>!p.includes(".."))));
});
test("snapshot lists previously produced designs and remains independent of local accounts",()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,"docs/visual-editor/browser/catalog.json"),"utf8"));
 assert.ok(data.length>=20&&data.length<100,"Show real editable deliverables, not an uncurated folder dump");
 assert.ok(data.some(x=>x.id==="carousel-01-v3"&&x.pages.length===5));
 assert.ok(data.some(x=>x.id==="instagram-tsinghua-atlas-2027"&&x.pages.length===7));
 assert.ok(data.some(x=>x.id==="cin-egitim-rollup-rollup-design-a"&&x.pages.length===1));
 assert.ok(data.some(x=>x.kind==="image"&&x.pages.length>1));
 assert.ok(!data.some(x=>/typography-round|direction-[a-z]/i.test(x.id)),"Review direction pages must not become projects");
 assert.ok(data.every(x=>x.pages.every(p=>!/(?:photos-original|source-originals|\/assets\/Jost|\/qa\/)/.test(p))),"Intermediate assets must not be listed as finished work");
 assert.equal(new Set(data.map(x=>x.id)).size,data.length);
});
test("browser adapter preserves each layout's own page size and wraps standalone image",()=>{
 const banner='html, body {\n width: 850px;\n height: 2000px;\n overflow:hidden;}';
 assert.equal(Adapter.dimensions(banner,"html").width,850);
 assert.equal(Adapter.dimensions(banner,"html").height,2000);
 const img=Adapter.normalize("","https://cinegitim.github.io/design/social-covers/cover-01.png","image");
 assert.match(img.html,/<div class="slide"><img class="photo"/);
 assert.equal(img.mode,"whole-image");
 assert.ok(!img.html.includes("<script"));
});
test("browser product picker, dynamic dimensions and isolated version state are wired",()=>{
 for(const fragment of ["id=\"catalog-search\"","id=\"catalog-select\"","src=\"catalog.js\"","src=\"adapter.js\"","function openProduct(productId)","async function sourceAt(i)","DESIGN_W","DESIGN_H","window.history.replaceState","brandstudio:browser:","await discovery.load"])
  assert.ok(html.includes(fragment),"Missing "+fragment);
 assert.match(html,/sourceCache\[i\]=normalized/);
 assert.match(html,/codec\.parseArchive\(raw,slug,pages\.length,brand\)/);
 assert.match(html,/codec\.makeArchive\(slug,allV\(\),state,brand\)/);
});

test("catalog shows actual authored work, not the typography comparison board in screenshot",()=>{
 const examples=[
  "docs/cin-egitim/typography-round-01/direction-a.html",
  "docs/cin-egitim/typography-round-01/direction-l.html",
  "docs/cin-egitim/typography-finalists/index.html",
  "docs/instagram/tsinghua-atlas-2027/source/01.html",
  "docs/instagram/tsinghua-atlas-2027/source/02.html",
  "docs/instagram/tsinghua-atlas-2027/assets/campus.jpg",
  "docs/instagram/tsinghua-atlas-2027/01-render.png",
  "docs/cin-egitim/rollup/rollup-design-a.html",
  "docs/instagram/creative-breakout/composited/A-cover.png",
  "docs/instagram/creative-breakout/source-originals/A-cover.png"
 ];
 const picked=Catalog.fromPaths(examples);
 const ids=picked.map(x=>x.id);
 assert.ok(ids.includes("instagram-tsinghua-atlas-2027"));
 assert.ok(ids.includes("cin-egitim-rollup-rollup-design-a"));
 assert.ok(ids.includes("asset-instagram-creative-breakout"));
 assert.ok(!ids.some(id=>/typography-round|typography-finalists/.test(id)));
 const atlas=picked.find(x=>x.id==="instagram-tsinghua-atlas-2027");
 assert.equal(atlas.kind,"html");
 assert.equal(atlas.pages.length,2);
 assert.ok(!picked.some(x=>x.pages.some(p=>/campus\.jpg|source-originals/.test(p))));
});

test("audited SVG legacy machine-local font URL is repaired only in browser",()=>{
 const legacy="url(/Users/artist/work/brands/example/assets/Jost-VF.ttf)";
 assert.equal(Adapter.repairLegacyFonts(legacy),"url(../assets/Jost-VF.ttf)");
 assert.equal(Adapter.repairLegacyFonts("url(../assets/Jost-VF.ttf)"),"url(../assets/Jost-VF.ttf)");
 assert.equal(Adapter.repairLegacyFonts("url(/Users/artist/private/photo.jpg)"),"url(/Users/artist/private/photo.jpg)");
});

test("nested footer transforms use containing block padding origin",()=>{
 const artboard={getBoundingClientRect:()=>({left:320,top:320}),contains:x=>x===footer};
 const footer={getBoundingClientRect:()=>({left:394,top:1380}),clientLeft:2,clientTop:3};
 const img={offsetParent:footer};
 assert.deepEqual({...UX.containingBlockOrigin(img,artboard)},{x:76,y:1063});
 assert.deepEqual({...UX.containingBlockOrigin({offsetParent:artboard},artboard)},{x:0,y:0});
 assert.deepEqual({...UX.containingBlockOrigin({offsetParent:null},artboard)},{x:0,y:0});
});
test("editor retains logo images and veil as selectable independent layers",()=>{
 const portable=fs.readFileSync(path.join(root,"docs/visual-editor/browser/portable.js"),"utf8");
 // Stage CI uses a sparse checkout; test editor code and independent identity guards.
 assert.match(html,/ux\.containingBlockOrigin\(n,doc\.querySelector\('\.slide'\)\)/);
 assert.match(html,/Fotoğraf filtresi · koyu gradyan/);
 assert.match(html,/\['static','absolute','relative'\]\.includes\(original\.position\)/);
 assert.match(html,/styles\.transform='translate\('/);
 assert.match(html,/var actual=pos\(n\),dx=/);
 assert.match(portable,/Logo yalnızca orantılı/);

 assert.match(html,/x\.classList\.contains\('veil'\).*pointerEvents/);
 assert.match(html,/\(\?:\^\|\-\)logo/);
 assert.match(portable,/function identityArtwork\(el\)/);
 assert.match(portable,/namedImage/);
});

test("full-height gradient stays directly clickable and will not collapse during move",()=>{
 assert.match(html,/if\(x\.classList\.contains\('veil'\)\)x\.style\.pointerEvents='auto'/);
 assert.match(html,/if\(!styles\.width\)styles\.width=Math\.round\(rect\.w\)\+'px'/);
 assert.match(html,/if\(n\.tagName!=='IMG'&&!styles\.height\)styles\.height=Math\.round\(rect\.h\)\+'px'/);
 assert.match(html,/hit\.classList\.contains\('veil'\)/);
 assert.match(html,/if\(n===cover&&wasSelected\)choose\(Number\(photo\.dataset\.editIndex\),false\)/);
 assert.match(html,/else if\(n===photo\)choose\(Number\(cover\.dataset\.editIndex\),false\)/);
});
test("layer reorder cannot send elements behind the canvas",()=>{
 assert.match(html,/function peerLayers\(i\)/);
 assert.match(html,/from\.parentElement!==to\.parentElement/);
 assert.match(html,/stackTier\(from\)!==stackTier\(to\)/);
 assert.match(html,/entry\.styles\['z-index'\]=String\(index\+1\)/);
 assert.match(html,/if\(computed\.position==='static'&&!/);
 assert.match(html,/entry\.styles\.position='relative'/);
 assert.doesNotMatch(html,/entry\.styles\['z-index'\]=String\(index-30\)/);
 assert.doesNotMatch(html,/e\.styles\['z-index'\]=action==='front'\?'20':'-20'/);
});

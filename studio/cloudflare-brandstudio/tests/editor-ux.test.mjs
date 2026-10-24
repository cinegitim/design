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
 assert.match(html,/logo\(n\)\|\|n\.classList\.contains\('folio'\)/);
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
 assert.match(html,/if\(!editable\(node\)\)return/);
 assert.match(html,/if\(evt\.shiftKey\)\{choose\(index,true\)/);
});

test("pointer drag re-anchors a multi-selection to the grabbed member",()=>{
 assert.match(html,/if\(!wasSelected\)choose\(index,false\);else\{sel=index;showSelection\(\)\}/);
 assert.match(html,/var start=pos\(n\),sx=evt\.clientX,sy=evt\.clientY/);
 assert.match(html,/setXY\(start\.x\+e\.clientX-sx,start\.y\+e\.clientY-sy\)/);
});

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import {test} from "node:test";
import path from "node:path";

const root=path.resolve(import.meta.dirname,"../../..");
const html=fs.readFileSync(path.join(root,"docs/visual-editor/browser/index.html"),"utf8");
const js=fs.readFileSync(path.join(root,"docs/visual-editor/browser/portable.js"),"utf8");
const env={};vm.runInNewContext(js,env);
const codec=env.BrandstudioPortable;
const sample=()=>({colors:{paper:"#f7f3e9",ink:"#1d2027",red:"#bd2120"},edits:{"1:3":{mode:"paper",styles:{
  position:"absolute",left:"72px",top:"320px",width:"550px",height:"380px",
  "font-size":"60px","font-weight":"550","letter-spacing":"-1.5px",
  "line-height":"1.22","text-align":"center",opacity:"0.75",
  "object-fit":"cover","object-position":"85% 12%","border-radius":"24px","z-index":"2"
}}}});

test("expanded safe geometry and typography survive archive roundtrip",()=>{
 const a=codec.makeArchive("carousel-01-v3",[{version:2,note:"Advanced",time:"2026",state:sample()}],sample());
 const b=codec.parseArchive(a,"carousel-01-v3",5);
 assert.equal(b.current.edits["1:3"].styles["object-position"],"85% 12%");
 assert.equal(b.versions[0].state.edits["1:3"].styles["font-weight"],"550");
 assert.equal(b.current.edits["1:3"].styles["border-radius"],"24px");
});

test("strict CSS policy blocks URLs, oversized opacity, unsafe photo offsets",()=>{
 for(const [k,v] of [["object-position","300% 50%"],["opacity","1.10"],["line-height","url(javascript:evil)"],["font-weight","1000"],["z-index","999"],["text-align","url(evil)"],["border-radius","url(http://bad)"],["object-fit","url(bad)"]]){
  const a=sample();a.edits["1:3"].styles[k]=v;
  assert.throws(()=>codec.validateState(a,5),undefined,k+" should be rejected");
 }
});

test("inspector and resize actions have real handlers, not decorative buttons",()=>{
 for(const id of ["zoom","zoom-in","zoom-out","frame","canvas","pan-shield","hand","focus","snap","weight","letter","leading","textalign","height","opacity","radius","zindex","photo-tools","fit","cropx","cropy"]){
  assert.ok(html.includes('id="'+id+'"'),"Missing UI "+id);
 }
 for(const token of ["setZoom(","setupOverlay()","selectionHandle.addEventListener('pointerdown'","fillAdvanced(n)","updateCrop()","data-align","checkpoint();","aria-pressed","new ResizeObserver"]){
  assert.ok(html.includes(token),"Missing handler "+token);
 }
 assert.match(html,/photo-tools" hidden/);
 assert.match(html,/Math\.round\(x\/8\)\*8/);
 assert.match(html,/logo\(target\)/);
});

test("published copy and canonical identity remain locked and unchanged",()=>{
 assert.match(html,/function logo\(n\)/);
 assert.match(html,/locked=logo\(n\)\|\|n\.classList\.contains\('folio'\)/);
 assert.doesNotMatch(html,/contentEditable\s*=\s*true/);
 assert.doesNotMatch(html,/method\s*:\s*['"]POST/);
 assert.doesNotMatch(js,/fetch\(/);
});

test("embedded code remains parseable; limited-size portable codec is present",()=>{
 const m=html.match(/<script>\s*([\s\S]*?)\s*<\/script>/);
 assert.ok(m);
 assert.ok(new vm.Script(m[1]));
 assert.ok(new vm.Script(js));
 assert.match(js,/32 KB sınırını aşıyor/);
});

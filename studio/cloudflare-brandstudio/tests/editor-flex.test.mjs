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

test("anchored image resize persists origin offsets without unsafe CSS",()=>{
 const x=sample();Object.assign(x.edits["1:3"].styles,{left:"44px",top:"71px",right:"auto",bottom:"auto"});
 const safe=codec.validateState(x,5);
 assert.equal(safe.edits["1:3"].styles.right,"auto");
 assert.equal(safe.edits["1:3"].styles.top,"71px");
 x.edits["1:3"].styles.right="url(https://bad)";
 assert.throws(()=>codec.validateState(x,5),/ankrajı/);
 assert.match(html,/left:Math\.round\(rect\.x-pr\.x\)\+'px'/);
 assert.match(html,/top:Math\.round\(rect\.y-pr\.y\)\+'px'/);
 assert.match(html,/right:'auto',bottom:'auto'/);
});
test("inspector and resize actions have real handlers, not decorative buttons",()=>{
 for(const id of ["zoom","zoom-in","zoom-out","frame","canvas","pan-shield","hand","focus","snap","weight","letter","leading","textalign","height","opacity","radius","zindex","photo-tools","fit","cropx","cropy"]){
  assert.ok(html.includes('id="'+id+'"'),"Missing UI "+id);
 }
 for(const token of ["setZoom(","setupOverlay()","handle.addEventListener('pointerdown'","fillAdvanced(n)","updateCrop()","data-align","checkpoint();","aria-pressed","new ResizeObserver"]){
  assert.ok(html.includes(token),"Missing handler "+token);
 }
 assert.match(html,/photo-tools" hidden/);
 assert.match(html,/Math\.round\(x\/8\)\*8/);
 assert.match(html,/function identityImage\(n\)/);
});

test("published copy and canonical identity remain locked and unchanged",()=>{
 assert.match(html,/function logo\(n\)/);
 assert.match(html,/var locked=logo\(n\),parts=codec\.textNodes\(n\)/);
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

test("formatted text segments are bounded and survive JSON state round-trip",()=>{
 const s=sample();
 s.edits["1:3"].segments=["Üniversite için","başka bir dünya","var."];
 const checked=codec.validateState(s,5);
 assert.equal(checked.edits["1:3"].segments[1],"başka bir dünya");
 const result=codec.parseArchive(codec.makeArchive("carousel-01-v3",[],s),"carousel-01-v3",5);
 assert.equal(result.current.edits["1:3"].segments[2],"var.");
 for(const bad of [["x".repeat(401)],[],Array(21).fill("x"),["ok",0]]){
  const changed=sample();changed.edits["1:3"].segments=bad;
  assert.throws(()=>codec.validateState(changed,5));
 }
});

test("history applies to live preview instead of reloading an iframe",()=>{
 assert.match(html,/function refreshPreview\(/);
 assert.match(html,/restoreState\(value\).*refreshPreview\(\);dirtyStatus\(\)/);
 assert.doesNotMatch(html,/function restoreState\(value\)[^\n]*show\(page\)/);
 assert.match(html,/sourceNodes=nodes\(\)\.map\(/);
 assert.match(html,/sourceNodes\[i\]/);
 assert.match(html,/function renderTextFields\(/);
 assert.match(html,/id="copy-tools" hidden/);
 assert.match(html,/field\.addEventListener\('change'/);
 assert.match(html,/candidate=copy\(state\)/);
 assert.match(html,/codec\.validateState\(candidate,pages\.length\)/);
 assert.match(html,/codec\.applyText\(n,v\.segments\)/);
 assert.doesNotMatch(html,/contentEditable\s*=\s*true/);
});

test("group state has undo snapshots, and group operations do not expose paid APIs",()=>{
 assert.match(html,/var state=\{colors:Object\.assign\(\{\},defaults\),edits:\{\},groups:\{\}\}/);
 assert.match(html,/checkpoint\(\);if\(!state\.groups\)state\.groups=\{\}/);
 assert.match(html,/function setXY\(x,y\)/);
 assert.match(html,/var ids=selectedIds\.length\?selectedIds:\[sel\]/);
 assert.match(html,/setRectangle\(node,\{x:p\.x\+dx,y:p\.y\+dy,w:p\.w,h:p\.h\},false\)/);
 assert.match(html,/handle\.hidden=!list\.length/);
 assert.doesNotMatch(html,/method\s*:\s*['"]POST/);
});

test("eight directional resize handles, rulers, context actions and primary geometry tools are genuine",()=>{
 for(const id of ["ruler-x","ruler-y","context-menu","band-color","band-tools","w","height","fs","x","y"])
  assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(html,/function drawRulers\(/);
 assert.match(html,/var positions=\{nw:/);
 assert.match(html,/selectionOverlay\._handles=handles/);
 assert.match(html,/handle\.addEventListener\('pointerdown'/);
 assert.match(html,/setRectangle\(item\.node,rect,true\)/);
 assert.match(html,/function openContextMenu\(/);
 assert.match(html,/doc\.addEventListener\('contextmenu'/);
 for(const action of ["front","back","align-left","align-center","align-right","group","ungroup","reset","undo"])
  assert.match(html,new RegExp('data-action="'+action+'"'));
 const props=html.indexOf('<div id="props" hidden>'),width=html.indexOf('id="w"'),type=html.indexOf('id="fs"'),appearance=html.indexOf('<h2>Görünüm</h2>');
 assert.ok(props>=0&&width>props&&width<appearance&&type<appearance);
});
test("logo backing band is editable independently while approved SVG remains immutable",()=>{
 assert.match(html,/function identityImage\(n\)/);
 assert.match(html,/function editable\(n\)\{return !!n\}/);
 assert.match(html,/Math\.max\(20,Number\.parseFloat\(value\)\)/);
 assert.match(html,/function setRectangle\(n,rect,resize\)/);
 assert.match(html,/if\(!identityImage\(n\)\)\{styles\.height=/);
 assert.match(html,/styles\['background-color'\]/);
 assert.match(html,/if\(identityImage\(n\)\)delete styles\.height/);
 assert.match(js,/function identityArtwork\(el\)/);
 assert.doesNotMatch(js,/minimum 352 px/);
 assert.doesNotMatch(html,/contentEditable\s*=\s*true/);
});

test("horizontal resize overrides source max-width only when actually resized",()=>{
 assert.match(html,/styles\['max-width'\]='none'/);
 assert.match(html,/if\(field==='width'&&!identityImage\(n\)\)e\.styles\['max-width'\]='none'/);
 assert.match(html,/var props=\[[^\]]*'max-width'/);
 assert.match(js,/else if\(k==='max-width'\)/);
 const s=sample();s.edits["1:3"].styles["max-width"]="none";
 assert.equal(codec.validateState(s,5).edits["1:3"].styles["max-width"],"none");
 s.edits["1:3"].styles["max-width"]="700px";
 assert.throws(()=>codec.validateState(s,5),/max-width/);
});

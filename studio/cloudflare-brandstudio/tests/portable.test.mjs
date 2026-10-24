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
 assert.match(portableSource,/if\(locked\(el\)\)err/);
});

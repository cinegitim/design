import assert from "node:assert/strict";
import {test} from "node:test";
import fs from "node:fs";
import path from "node:path";

const root=path.resolve(import.meta.dirname,"../../..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const data=JSON.parse(read("docs/system/catalog.json"));
const page=read("docs/system/index.html");
const app=read("docs/system/app.js");

test("system hub has category-specific independent style families",()=>{
 assert.equal(data.schema,1);
 assert.equal(data.categories.length,6);
 assert.equal(data.styles.length,3);
 assert.equal(data.categories.find(x=>x.id==="instagram-carousel").style_count,3);
 assert.deepEqual(data.styles.map(x=>x.id),["editorial-campaign","data-atlas","conceptual-breakout"]);
 assert.ok(data.styles.every(x=>x.status==="review-only"&&x.production_approved===false));
 assert.equal(data.styles[0].status,"review-only");
 assert.equal(data.styles[0].production_approved,false);
 assert.ok(data.categories.some(x=>x.id==="social-post"&&x.style_count===0));
});
test("agent and LLM selectors do not infer model tools or approval",()=>{
 assert.equal(data.executors.length,8);
 assert.ok(data.model_families.length>=5);
 assert.ok(data.model_families.every(x=>x.status==="advisory"&&x.capabilities_verified===false));
 assert.equal(data.workflow.automatic_agent_execution,false);
 assert.equal(data.workflow.github_version,"pr-required");
 assert.equal(data.workflow.social_proof,"platform-evidence-required");
});
test("working navigation links library, production center, editor and archive",()=>{
 for(const id of ["library","production","pipeline","category-picker","style-picker","preset-picker","executor-picker","model-picker","copy-brief"])
  assert.ok(page.includes('id="'+id+'"'),"Missing "+id);
 for(const source of ["docs/index.html","docs/workspaces/asyada-egitim/index.html"])
  assert.match(read(source),/system\//);
 assert.match(page,/\.\.\/visual-editor\/browser\//);
 assert.match(page,/\.\.\/workspaces\/asyada-egitim\//);
});
test("client copies only an honest PR-ready brief",()=>{
 assert.match(app,/fetch\("catalog.json"/);
 assert.match(app,/github\.status/);
 assert.match(app,/not-submitted/);
 assert.match(app,/model_capabilities_verified:false/);
 assert.doesNotMatch(app,/api\.github\.com|fetch\("\/admin\/|postMessage.*password|auto_publish/);
});


test("style family cards switch product style selection without creating templates or writes",()=>{
 const css=read("docs/system/style.css");
 assert.match(app,/style-family-grid/);
 assert.match(app,/style-family-card/);
 assert.match(app,/aria-pressed/);
 assert.match(app,/activeStyle=s.id/);
 assert.match(app,/updatePresets\(\);drawStyle\(\)/);
 assert.match(app,/found.length\+" bağımsız tasarım dili/);
 for(const id of ["editorial-campaign","data-atlas","conceptual-breakout"])
  assert.ok(css.includes('data-style="'+id+'"]'));
 assert.doesNotMatch(app,/fetch\([^)]*,\s*\{\s*method:\s*["']POST/);
});

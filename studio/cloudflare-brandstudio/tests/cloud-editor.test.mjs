import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const source=fs.readFileSync(path.join(root,'docs/visual-editor/browser/github-sync.js'),'utf8');
const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
const backend=fs.readFileSync(path.join(root,'functions/visual-editor/api/revisions.js'),'utf8');
function fixture(){
 const data=new Map(),calls=[];
 async function fetch(url,opts={}){
  calls.push({url,method:opts.method,headers:opts.headers});
  const product=new URL(url,'https://studio.asyadaegitim.com').searchParams.get('product');
  const old=data.get(product);
  if(opts.method==='GET')return new Response(JSON.stringify(old||{sha:null,document:{schema:1,product,versions:{},history:[]}}),{headers:{'content-type':'application/json'}});
  if(opts.method!=='POST')throw Error('Unexpected method');
  const body=JSON.parse(opts.body);
  if((old?.sha??null)!==body.expectedSha)return new Response(JSON.stringify({error:'Kaydedilemedi'}),{status:409,headers:{'content-type':'application/json'}});
  const doc=old?structuredClone(old.document):{schema:1,product,versions:{},history:[]};
  doc.versions['v'+body.version]={state:body.state,note:body.note};
  doc.history.push({id:'entry-'+(doc.history.length+1),state:body.state,version:body.version,kind:body.kind});
  const sha='test-revision-'+(doc.history.length);
  const next={sha,document:doc};
  data.set(product,next);
  return new Response(JSON.stringify(next),{headers:{'content-type':'application/json'}})
 }
 const sandbox={fetch,URL,Response,TextEncoder,TextDecoder,structuredClone,btoa,atob,console};
 sandbox.globalThis=sandbox;
 vm.runInNewContext(source,sandbox);
 return {cloud:sandbox.BrandstudioCloud,calls,data}
}
const state=n=>({colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:n?{'0:2':{styles:{left:n+'px'},mode:'inherit'}}:{},groups:{}});
test('single Cloudflare API, no browser GitHub PAT or direct GitHub write',async()=>{
 const {cloud,calls}=fixture();
 assert.equal(cloud.authenticated(),true);
 const init=await cloud.load('sample');
 assert.equal(init.sha,null);
 await cloud.commit({product:'sample',version:1,state:state(1),expectedSha:null});
 assert.ok(calls.every(c=>c.url.startsWith('/visual-editor/api/revisions?product=')));
 assert.ok(calls.every(c=>!JSON.stringify(c.headers).includes('Bearer')));
 assert.doesNotMatch(source,/api\.github\.com|accessToken|localStorage|sessionStorage|document\.cookie/);
});
test('same version save and intentional next version preserve earlier history',async()=>{
 const {cloud}=fixture();
 let a=await cloud.commit({product:'sample',version:2,state:state(1),expectedSha:null,kind:'autosave'});
 let b=await cloud.commit({product:'sample',version:2,state:state(2),expectedSha:a.sha,kind:'autosave'});
 assert.equal(b.document.versions.v2.state.edits['0:2'].styles.left,'2px');
 assert.equal(b.document.history.length,2);
 let c=await cloud.commit({product:'sample',version:3,state:state(2),expectedSha:b.sha,kind:'new'});
 assert.equal(Object.keys(c.document.versions).join(','),'v2,v3');
});
test('stale writers receive a clear conflict instead of silent overwrite',async()=>{
 const {cloud}=fixture();
 const a=await cloud.commit({product:'sample',version:2,state:state(1),expectedSha:null});
 await assert.rejects(cloud.commit({product:'sample',version:2,state:state(3),expectedSha:'stale'}),/başka bir yerde değişmiş/i);
 const now=await cloud.load('sample');
 assert.equal(now.sha,a.sha);
 assert.equal(now.document.versions.v2.state.edits['0:2'].styles.left,'1px');
});
test('server rejects unauthenticated requests and verifies signed Access JWT',()=>{
 assert.match(backend,/Cf-Access-Jwt-Assertion/);
 assert.match(backend,/crypto\.subtle\.verify/);
 assert.match(backend,/OWNER=/);
 assert.match(backend,/ACCESS_AUD=/);
 assert.match(backend,/if\(!await authorized/);
 assert.match(backend,/X-Brandstudio-Editor/);
 assert.match(backend,/req\.headers\.get\('Origin'\)!==url\.origin/);
 assert.match(backend,/STORE='BRANDSTUDIO_OBJECTS'/);
 assert.ok(backend.includes('idFromName(product)'));
 assert.ok(backend.includes('objectFor(context,product).fetch'));
 assert.doesNotMatch(backend,/editor_documents|BRANDSTUDIO_EDITOR/);
 const store=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/editor-store/worker.mjs'),'utf8');
 assert.match(store,/class BrandstudioRevisionObject/);
 assert.ok(store.includes('this.ctx.storage.transaction'));
 assert.match(store,/RECOVERED_BAVUL/);
 assert.doesNotMatch(store,/sha:"legacy-v2"/);
});
test('one visible editor, simple autosave and direct PNG/JPEG downloads',()=>{
 assert.match(html,/location\.hostname==='cinegitim\.github\.io'/);
 assert.ok(html.includes('studio.asyadaegitim.com'));
 assert.match(html,/function wakeAutoSave/);
 assert.match(html,/function updateRecoveryButtons/);
 for(const id of ['download-png','download-jpeg','side-download-png','side-download-jpeg'])assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(html,/html2canvas\(slide/);
 assert.match(html,/canvas\.toBlob/);
 assert.match(html,/id="cloud-token"[^>]*type="password"/);
 assert.doesNotMatch(html,/GitHub erişim anahtarı \(yalnızca bellekte/);
 assert.doesNotMatch(source,/localStorage|sessionStorage|document\.cookie/);
});

test('autosave captures a stable input snapshot and normalizes live state only after server acknowledgment',()=>{
 assert.match(html,/submitted=copy\(state\)/);
 assert.match(html,/codec\.validateState\(submitted,pages\.length\)/);
 assert.match(html,/if\(JSON\.stringify\(state\)===serialized\)state=copy\(checked\)/);
 assert.match(html,/dirty=JSON\.stringify\(state\)!==JSON\.stringify\(savedState\)/);
 const store=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/editor-store/worker.mjs'),'utf8');
 assert.match(store,/unchanged:true/);
 assert.doesNotMatch(store,/fetch\(url,/);
 assert.match(store,/RECOVERED_BAVUL/);
});

test('recovered pending state compares normalized values and does not show false unsaved work',()=>{
 assert.match(html,/codec\.validateState\(pending\.state,pages\.length\)/);
 assert.match(html,/codec\.validateState\(cloudData\.versions\['v'\+pending\.version\]\.state,pages\.length\)/);
 const store=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/editor-store/worker.mjs'),'utf8');
 assert.match(store,/function compactRetryHistory/);
 assert.match(store,/repeatedAutosaves/);
 assert.match(store,/if\(stored\.document\.history\.length>=100\)/);
});

test('Brandstudio Cloudflare gateway stages password/session auth and routes revisions to private DO',()=>{
 const edge=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
 assert.ok(edge.includes('ADMIN_PBKDF2_HASH'));
 assert.ok(edge.includes('BRANDSTUDIO_AUTH'));
 assert.ok(edge.includes('session(request,env)'));
 const cfg=JSON.parse(fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/wrangler.json'),'utf8'));
 assert.equal(cfg.durable_objects.bindings[0].class_name,'BrandstudioRevisionObject');
 assert.ok(edge.includes('X-Brandstudio-Editor'));
 assert.ok(edge.includes('__Host-brandstudio_session'));
 assert.ok(edge.includes('__Host-branddesign_session'));
 assert.ok(!edge.includes('Cf-Access-Jwt-Assertion'));
 assert.ok(edge.includes('https://brandstudio-pages-git.pages.dev'));
 assert.ok(edge.includes('https://brandstudio.internal/revisions'));
 assert.ok(edge.includes("if(request.method==='GET')return attachSession(await onRequestGet(context),user)"));
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'studio/brandstudio/manifest.json'),'utf8'));
 assert.equal(manifest.destination.account,'asyadaegitim');
 assert.equal(manifest.editor.origin,'https://studio.asyadaegitim.com');
 assert.equal(manifest.source.status,'retired-after-verified-migration-2026-10-30');
});

test('Durable Object revisions always get mirrored to D1 without risking authoritative saves',()=>{
 const store=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/editor-store/worker.mjs'),'utf8');
 const cfg=JSON.parse(fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/editor-store/wrangler.json'),'utf8'));
 assert.ok(cfg.d1_databases.some(x=>x.binding==='BACKUP_DB'&&x.database_name==='brandstudio-editor'));
 assert.match(store,/async archiveRevision\(record,product\)/);
 assert.match(store,/INSERT OR IGNORE INTO editor_revision_backups/);
 assert.match(store,/await this.archiveRevision\(result,product\)/);
 assert.match(store,/await this.archiveRevision\(existing,product\)/);
 assert.match(store,/await this.archiveRevision\(current,product\)/);
 assert.match(store,/Brandstudio secondary backup pending/);
 assert.match(store,/lastArchivedRevision/);
 const schema=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/migrations/0002_editor_backup.sql'),'utf8');
 assert.match(schema,/PRIMARY KEY\(product,revision\)/);
 assert.match(schema,/CHECK\(json_valid\(body\)\)/);
});

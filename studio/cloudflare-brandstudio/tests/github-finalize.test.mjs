import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {submitProductFinalization,finalizationStatus} from '../asya-gateway/github-finalize.mjs';

const PRODUCT='instagram-kaist-tech-track-2027-001-v2';
const SHA='0882e066-d82d-4d31-9d9f-5aac06b3b2ca';
const TOKEN='github_pat_mock_token_not_real_0123456789';
const STATE={colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:{},groups:{}};
const versions={v1:{state:STATE,updatedAt:'2026-11-04T08:00:00Z',note:'A'},v2:{state:STATE,updatedAt:'2026-11-04T09:00:00Z',note:'B'}};
const history=[{id:'h1',at:'2026-11-04T08:00:00Z',version:1,kind:'save',state:STATE},
 {id:'h2',at:'2026-11-04T09:00:00Z',version:2,kind:'new',state:STATE}];
const source=['instagram/kaist-tech-track-2027-001/v2/source/01.html','instagram/kaist-tech-track-2027-001/v2/source/02.html'];
const files=[];
for(const n of [1,2])for(const i of [1,2]){
 const p='versions/v0'+n+'/slides/0'+i;
 files.push({path:p+'.html',content:'<!doctype html><html><body><div class="slide">slide '+i+'</div></body></html>'});
 files.push({path:p+'.css',content:'.slide{color:red}'});
}
const payload=(extra={})=>({product:PRODUCT,selectedVersion:2,expectedSha:SHA,sourcePages:source,files,
 acknowledgePublicRepository:true,...extra});
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json'}});
const request=(data,headers={})=>new Request('https://studio.asyadaegitim.com/visual-editor/api/finalize',{
 method:'POST',headers:{Origin:'https://studio.asyadaegitim.com','Content-Type':'application/json',
 'X-Brandstudio-Editor':'1',...headers},body:JSON.stringify(data)
});
const ctx=(data=payload(),extra={},headers={})=>({authenticated:true,request:request(data,headers),env:{
 GITHUB_PR_TOKEN:TOKEN,BRANDSTUDIO_OBJECTS:{idFromName:x=>x,get:()=>({
  fetch:async()=>response({sha:SHA,document:{versions,history}})})},...extra
}});
function fixture(existing=false){
 const calls=[];let tree=null;
 const fetch=async(url,opts={})=>{
  const u=new URL(url),method=opts.method||'GET',body=opts.body?JSON.parse(opts.body):null;
  calls.push({path:u.pathname+u.search,method,body,headers:opts.headers});
  if(u.hostname==='brandstudio-pages-git.pages.dev')return response([
   {id:PRODUCT,title:'KAIST',family:'instagram',kind:'html',pages:source}]);
  if(u.pathname.endsWith('/pulls')&&method==='GET')return response(existing?
   [{html_url:'https://github.com/cinegitim/design/pull/888',number:888,state:'open',merged_at:null}]:[]);
  if(u.pathname.includes('/git/ref/heads/studio/'))return response({message:'not found'},404);
  if(u.pathname.endsWith('/git/ref/heads/main'))return response({object:{sha:'1'.repeat(40)}});
  if(u.pathname.endsWith('/git/commits/'+'1'.repeat(40)))return response({tree:{sha:'2'.repeat(40)}});
  if(u.pathname.endsWith('/git/trees')&&method==='POST'){tree=body;return response({sha:'3'.repeat(40)},201)}
  if(u.pathname.endsWith('/git/commits')&&method==='POST')return response({sha:'4'.repeat(40)},201);
  if(u.pathname.endsWith('/git/refs')&&method==='POST')return response({ref:'ok'},201);
  if(u.pathname.endsWith('/pulls')&&method==='POST')return response({
   html_url:'https://github.com/cinegitim/design/pull/888',number:888},201);
  throw Error('Unexpected path: '+method+' '+u.pathname)
 };
 return {calls,fetch,get tree(){return tree}}
}
async function withFetch(f,cb){const old=globalThis.fetch;globalThis.fetch=f;try{return await cb()}finally{globalThis.fetch=old}}

test('manual product-finalization status is private, honest, and token-free',async()=>{
 let a=ctx();a.authenticated=false;assert.equal(finalizationStatus(a).status,401);
 const s=await finalizationStatus(ctx()).json();
 assert.equal(s.mode,'product-bulk-draft-review');assert.equal(s.enabled,true);
 assert.ok(!JSON.stringify(s).includes(TOKEN));
 assert.equal((await finalizationStatus(ctx(payload(),{GITHUB_PR_TOKEN:undefined})).json()).enabled,false);
});

test('reject missing consent, cross-origin and malformed product',async()=>{
 assert.equal((await submitProductFinalization(ctx(payload({acknowledgePublicRepository:false})))).status,400);
 assert.equal((await submitProductFinalization(ctx(payload(),{}, {'Origin':'https://evil.example'}))).status,403);
 assert.equal((await submitProductFinalization(ctx(payload({product:'../bad'})))).status,400);
 let c=ctx();c.authenticated=false;assert.equal((await submitProductFinalization(c)).status,401);
 assert.equal((await submitProductFinalization(ctx(payload(),{GITHUB_PR_TOKEN:undefined}))).status,503);
});

test('reject wrong cloud SHA, missing saved version and mismatched source inventory',async()=>{
 assert.equal((await submitProductFinalization(ctx(payload({expectedSha:'11111111-1111-1111-1111-111111111111'})))).status,409);
 const f=fixture();
 await withFetch(f.fetch,async()=>{
  assert.equal((await submitProductFinalization(ctx(payload({selectedVersion:3})))).status,409);
  assert.equal((await submitProductFinalization(ctx(payload({sourcePages:['wrong.html']})))).status,409);
  assert.equal((await submitProductFinalization(ctx(payload({files:files.slice(0,-1)})))).status,413);
  assert.equal((await submitProductFinalization(ctx(payload({files:[...files.slice(0,-1),files[0]]})))).status,400);
 });
 assert.equal(f.calls.filter(c=>c.path.includes('/git/trees')).length,0);
});

test('one explicit submit creates one GitHub commit and one DRAFT PR with every saved version',async()=>{
 const f=fixture();
 await withFetch(f.fetch,async()=>{
  const r=await submitProductFinalization(ctx());assert.equal(r.status,201);
  const data=await r.json();
  assert.equal(data.number,888);assert.equal(data.versions,2);assert.equal(data.renderedSlides,8);
  assert.match(data.branch,/^studio\/finalize-instagram-kaist/);
  assert.ok(!JSON.stringify(data).includes(TOKEN));
 });
 const treeRequests=f.calls.filter(c=>c.path.endsWith('/git/trees')&&c.method==='POST');
 const commitRequests=f.calls.filter(c=>c.path.endsWith('/git/commits')&&c.method==='POST');
 const refs=f.calls.filter(c=>c.path.endsWith('/git/refs')&&c.method==='POST');
 const prs=f.calls.filter(c=>c.path.endsWith('/pulls')&&c.method==='POST');
 assert.equal(treeRequests.length,1);assert.equal(commitRequests.length,1);
 assert.equal(refs.length,1);assert.equal(prs.length,1);
 assert.equal(prs[0].body.draft,true);
 assert.equal(prs[0].body.maintainer_can_modify,false);
 assert.deepEqual(commitRequests[0].body.parents,['1'.repeat(40)]);
 const entries=treeRequests[0].body.tree;
 assert.equal(entries.length,12); // 8 HTML/CSS + 2 state JSON + history + manifest
 const names=entries.map(x=>x.path);
 assert.ok(names.some(n=>n.endsWith('/manifest.json')));
 assert.ok(names.some(n=>n.endsWith('/history.json')));
 for(const n of [1,2])assert.ok(names.some(p=>p.endsWith('/versions/v0'+n+'/editor-state.json')));
 const manifest=JSON.parse(entries.find(x=>x.path.endsWith('/manifest.json')).content);
 assert.equal(manifest.source.baseCommit,'1'.repeat(40));
 assert.equal(manifest.review.socialPublished,false);
 assert.equal(manifest.versions.length,2);
 const saved=JSON.parse(entries.find(x=>x.path.endsWith('/versions/v02/editor-state.json')).content);
 assert.deepEqual(saved.state,STATE);
 assert.ok(f.calls.every(c=>!c.path.includes('/contents/docs/')));
 assert.ok(f.calls.filter(c=>c.path.includes('api.github.com')).every(c=>c.headers?.Authorization==='Bearer '+TOKEN));
});

test('repeat click reuses the existing PR and does not create any commit or branch',async()=>{
 const f=fixture(true);
 await withFetch(f.fetch,async()=>{
  const r=await submitProductFinalization(ctx());assert.equal(r.status,200);
  const data=await r.json();assert.equal(data.existing,true);assert.equal(data.number,888);
 });
 assert.equal(f.calls.filter(c=>c.path.includes('/git/trees')||c.path.includes('/git/refs')).length,0);
});

test('editor finalization is manual, item-wide and separate from cloud save',()=>{
 const root=path.resolve(import.meta.dirname,'../../..');
 const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
 const client=fs.readFileSync(path.join(root,'docs/visual-editor/browser/github-sync.js'),'utf8');
 const worker=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
 assert.match(html,/id="finalize-product"/);
 assert.match(html,/function cloudVersionNumbers\(/);
 assert.match(html,/if\(!confirm\(record.title/);
 assert.match(html,/codec\.html\(originals\[i\],pages\[i\],clean,i\)/);
 assert.match(html,/codec\.css\(originals\[i\],clean,i,pages\[i\]\)/);
 assert.match(html,/if\(slug!==product\|\|cloudSha!==sha\|\|dirty\)/);
 assert.doesNotMatch(html,/id="style-pr"/);
 assert.match(client,/async function finalizeProduct\(/);
 assert.doesNotMatch(client,/api\.github\.com|GITHUB_PR_TOKEN/);
 assert.match(worker,/submitProductFinalization\(\{request,env,authenticated:true\}\)/);
 assert.match(worker,/'\/visual-editor\/api\/finalize'/);
});

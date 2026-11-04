import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import {promotionStatus,submitSourcePromotion} from '../asya-gateway/github-promote.mjs';
const PRODUCT='instagram-kaist-tech-track-2027-001-v2';
const ROOT='instagram/kaist-tech-track-2027-001/v2/source/';
const REV='0882e066-d82d-4d31-9d9f-5aac06b3b2ca';
const TOKEN='github_pat_mock_no_real_token_0123456789';
const STATE={colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:{},groups:{}};
const source=[ROOT+'01.html',ROOT+'02.html'];
const oldBranch='studio/finalize-'+PRODUCT.slice(0,62)+'-'+REV.replace(/-/g,'').slice(0,12);
const promoBranch='studio/promote-'+PRODUCT.slice(0,58)+'-'+REV.replace(/-/g,'').slice(0,12);
const archive='studio/production/finalized/'+PRODUCT+'/'+REV.replace(/-/g,'').slice(0,12)+'/';
const groups={schema:1,groups:[{id:'instagram-kaist-tech-track-2027-001',
 title:'KAIST',brand:'asyada-egitim',currentId:PRODUCT,defaultId:'instagram-kaist-tech-track-2027-001',
 publishedVersionId:'instagram-kaist-tech-track-2027-001',
 versions:[{id:'instagram-kaist-tech-track-2027-001',label:'v1'},{id:PRODUCT,label:'v2'}]}]};
const catalog=[{id:PRODUCT,title:'KAIST v2',family:'instagram',kind:'html',pages:source}];
const manifest={kind:'brandstudio-product-finalization',revision:REV,product:PRODUCT,selectedVersion:1,
 source:{repository:'cinegitim/design',baseCommit:'1'.repeat(40),paths:source.map(s=>'docs/'+s)}};
const html=(n)=>'<!doctype html><html lang="tr"><head><base href="https://studio.asyadaegitim.com/'+source[n-1]+'"><link rel="stylesheet" href="../assets/style.css"></head><body><main class="slide"><img src="../../assets/h02-primary-horizontal-dark.svg"></main></body></html>';
const contents=new Map([
 ['docs/visual-editor/browser/catalog.json',JSON.stringify(catalog)],
 ['docs/visual-editor/browser/product-groups.json',JSON.stringify(groups)],
 [archive+'manifest.json',JSON.stringify(manifest)],
 [archive+'versions/v01/editor-state.json',JSON.stringify({product:PRODUCT,version:1,state:STATE})],
 ...[1,2].flatMap(n=>[
  [archive+'versions/v01/slides/0'+n+'.html',html(n)],
  [archive+'versions/v01/slides/0'+n+'.css','.slide{letter-spacing:1px}']
 ])
]);
const reply=(x,status=200)=>new Response(JSON.stringify(x),{status,headers:{'content-type':'application/json'}});
const request=(v={},headers={})=>new Request('https://studio.asyadaegitim.com/visual-editor/api/promote',
 {method:'POST',headers:{Origin:'https://studio.asyadaegitim.com',
  'Content-Type':'application/json','X-Brandstudio-Editor':'1',...headers},
 body:JSON.stringify({product:PRODUCT,expectedSha:REV,selectedVersion:1,acknowledgeNewGitHubVersion:true,...v})});
const ctx=(v={},options={},headers={})=>({authenticated:true,request:request(v,headers),
 env:{GITHUB_PR_TOKEN:TOKEN,BRANDSTUDIO_OBJECTS:{
  idFromName:x=>x,get:()=>({fetch:async()=>reply({sha:options.stale?'11111111-1111-1111-1111-111111111111':REV,
    document:{versions:{v1:{state:STATE}}}})})}
 }});
function mockApi({merged=true,existing=false,files=contents}={}){
 let calls=[];
 async function fetch(url,opts={}){
  const u=new URL(url),method=opts.method||'GET';
  const data=opts.body?JSON.parse(opts.body):null;
  calls.push({url:u.pathname+u.search,method,body:data});
  if(u.pathname.endsWith('/pulls')&&method==='GET'){
   if(u.searchParams.get('head')==='cinegitim:'+oldBranch)
    return reply([{head:{ref:oldBranch},state:merged?'closed':'open',merged_at:merged?'2026-11-04T10:00:00Z':null,number:7}]);
   if(u.searchParams.get('head')==='cinegitim:'+promoBranch)
    return reply(existing?[{html_url:'https://github.com/cinegitim/design/pull/333',number:333,state:'open',merged_at:null}]:[]);
  }
  if(u.pathname.includes('/git/ref/heads/studio/promote-'))return reply({message:'not found'},404);
  if(u.pathname.endsWith('/git/ref/heads/main'))return reply({object:{sha:'1'.repeat(40)}});
  if(u.pathname.endsWith('/git/commits/'+'1'.repeat(40)))return reply({tree:{sha:'2'.repeat(40)}});
  if(u.pathname.includes('/contents/')&&method==='GET'){
   const p=decodeURIComponent(u.pathname.split('/contents/')[1]);
   return files.has(p)?reply({type:'file',encoding:'base64',content:Buffer.from(files.get(p),'utf8').toString('base64')}):reply({message:'Not Found'},404);
  }
  if(u.pathname.endsWith('/git/trees')&&method==='POST')return reply({sha:'3'.repeat(40)},201);
  if(u.pathname.endsWith('/git/commits')&&method==='POST')return reply({sha:'4'.repeat(40)},201);
  if(u.pathname.endsWith('/git/refs')&&method==='POST')return reply({ref:'created'},201);
  if(u.pathname.endsWith('/pulls')&&method==='POST')return reply({html_url:'https://github.com/cinegitim/design/pull/333',number:333},201);
  throw Error('unexpected URL '+method+' '+u.pathname+u.search);
 }
 return {fetch,calls};
}
async function runWith(m,callback){
 const prev=globalThis.fetch;globalThis.fetch=m.fetch;
 try{return await callback()}finally{globalThis.fetch=prev}
}
test('requires admin session, origin, consent and configured GitHub token',async()=>{
 const a=ctx();a.authenticated=false;
 assert.equal((await submitSourcePromotion(a)).status,401);
 assert.equal((await submitSourcePromotion(ctx({}, {},{Origin:'https://evil.example'}))).status,403);
 assert.equal((await submitSourcePromotion(ctx({acknowledgeNewGitHubVersion:false}))).status,400);
 const c=ctx();c.env.GITHUB_PR_TOKEN=undefined;
 assert.equal((await submitSourcePromotion(c)).status,503);
 const enabled=await promotionStatus(ctx()).json();
 assert.equal(enabled.enabled,true);
 assert.equal(enabled.mode,'immutable-new-source-version');
 assert.ok(!JSON.stringify(enabled).includes(TOKEN));
});
test('does not promote stale state or unmerged delivery',async()=>{
 assert.equal((await submitSourcePromotion(ctx({}, {stale:true}))).status,409);
 const m=mockApi({merged:false});
 await runWith(m,async()=>{
  const r=await submitSourcePromotion(ctx());
  assert.equal(r.status,409);
  assert.match((await r.json()).error,/toplu teslim/i);
 });
 assert.equal(m.calls.filter(x=>x.method==='POST').length,0);
});
test('creates one draft PR with brand-new v3 while preserving v2 and publication metadata',async()=>{
 const m=mockApi();
 const response=await runWith(m,()=>submitSourcePromotion(ctx()));
 assert.equal(response.status,201);
 const out=await response.json();
 assert.equal(out.newProduct,'instagram-kaist-tech-track-2027-001-v3');
 assert.equal(out.newVersion,3);assert.equal(out.sourceFiles,2);
 const tree=m.calls.find(c=>c.method==='POST'&&c.url.endsWith('/git/trees')).body.tree;
 assert.ok(tree.some(x=>x.path==='docs/instagram/kaist-tech-track-2027-001/v3/source/01.html'));
 assert.ok(tree.some(x=>x.path==='docs/instagram/kaist-tech-track-2027-001/v3/source/02.html'));
 assert.ok(tree.every(x=>!x.path.includes('/v2/source/')));
 const first=tree.find(x=>x.path.endsWith('/v3/source/01.html')).content;
 assert.match(first,/<base href="\.\.\/\.\.\/v2\/source\/01\.html"/);
 assert.match(first,/data-brandstudio-promoted/);
 assert.match(first,/h02-primary-horizontal-dark\.svg/);
 const registered=JSON.parse(tree.find(x=>x.path==='docs/visual-editor/browser/product-groups.json').content).groups[0];
 assert.equal(registered.currentId,'instagram-kaist-tech-track-2027-001-v3');
 assert.equal(registered.defaultId,'instagram-kaist-tech-track-2027-001');
 assert.equal(registered.publishedVersionId,'instagram-kaist-tech-track-2027-001');
 assert.equal(registered.versions.length,3);
 const cat=JSON.parse(tree.find(x=>x.path==='docs/visual-editor/browser/catalog.json').content);
 assert.ok(cat.some(x=>x.id==='instagram-kaist-tech-track-2027-001-v3'));
 assert.equal(m.calls.filter(c=>c.method==='POST'&&c.url.endsWith('/pulls')).length,1);
 assert.equal(m.calls.find(c=>c.method==='POST'&&c.url.endsWith('/pulls')).body.draft,true);
 assert.equal(m.calls.filter(c=>c.method==='POST'&&c.url.endsWith('/git/commits')).length,1);
});
test('repeat click reuses promotion PR with zero new writes',async()=>{
 const m=mockApi({existing:true});
 const r=await runWith(m,()=>submitSourcePromotion(ctx()));
 assert.equal(r.status,200);assert.equal((await r.json()).existing,true);
 assert.equal(m.calls.filter(c=>c.method==='POST').length,0);
});
test('rejects changed catalogue or archive state rather than inventing files',async()=>{
 const altered=new Map(contents);
 altered.set('docs/visual-editor/browser/catalog.json',JSON.stringify([{id:PRODUCT,kind:'html',pages:['wrong/source/01.html']}]));
 const m=mockApi({files:altered});
 const r=await runWith(m,()=>submitSourcePromotion(ctx()));
 assert.equal(r.status,409);
 assert.equal(m.calls.filter(c=>c.method==='POST').length,0);
});
test('editor exposes explicit promotion, with no automatic PR on cloud revision save',()=>{
 const root=path.resolve(import.meta.dirname,'../../..');
 const page=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
 const client=fs.readFileSync(path.join(root,'docs/visual-editor/browser/github-sync.js'),'utf8');
 const worker=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
 const codec=fs.readFileSync(path.join(root,'docs/visual-editor/browser/portable.js'),'utf8');
 assert.match(page,/id="promote-version"/);
 assert.match(page,/\$\('promote-version'\)\.onclick/);
 assert.match(page,/cloud\.promoteVersion\(\{/);
 assert.match(client,/async function promoteVersion/);
 assert.doesNotMatch(client,/api\.github\.com|GITHUB_PR_TOKEN/);
 assert.match(worker,/submitSourcePromotion\(\{request,env,authenticated:true\}\)/);
 assert.match(codec,/if\(!doc\.head\.querySelector\('base'\)\)/);
});

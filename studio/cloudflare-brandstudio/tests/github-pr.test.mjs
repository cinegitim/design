import assert from 'node:assert/strict';
import {test} from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import {submitEditorReview} from '../asya-gateway/github-pr.mjs';

const PRODUCT='instagram-kaist-tech-track-2027-001-v2';
const REV='0882e066-d82d-4d31-9d9f-5aac06b3b2ca';
const STATE={colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:{'0:2':{styles:{left:'15px'}}},groups:{}};
const TOK='github_pat_mock_token_is_not_real_0123456789';
const request=(data,headers={})=>new Request('https://studio.asyadaegitim.com/visual-editor/api/github-pr',{
 method:'POST',headers:{'Origin':'https://studio.asyadaegitim.com','Content-Type':'application/json',
  'X-Brandstudio-Editor':'1',...headers},body:JSON.stringify(data)});
const payload=(other={})=>({product:PRODUCT,version:2,expectedSha:REV,acknowledgePublicRepository:true,...other});
const context=(body=payload(),envExtra={},headers={})=>({authenticated:true,request:request(body,headers),
 env:{GITHUB_PR_TOKEN:TOK,BRANDSTUDIO_OBJECTS:{idFromName:x=>x,get:()=>({fetch:async()=>new Response(JSON.stringify({
  sha:REV,document:{versions:{v2:{state:STATE}}}
 }),{headers:{'content-type':'application/json'}})})},...envExtra}});
const result=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json'}});

test('auth, same origin, exact consent and secret are mandatory',async()=>{
 const anon=context();anon.authenticated=false;
 assert.equal((await submitEditorReview(anon)).status,401);
 assert.equal((await submitEditorReview(context(payload(),{}, {'Origin':'https://evil.example'}))).status,403);
 assert.equal((await submitEditorReview(context(payload({acknowledgePublicRepository:false})))).status,400);
 assert.equal((await submitEditorReview(context(payload({product:'../bad'})))).status,400);
 assert.equal((await submitEditorReview(context(payload({version:27})))).status,400);
 assert.equal((await submitEditorReview(context(payload(),{GITHUB_PR_TOKEN:undefined}))).status,503);
});

test('stale or unsaved cloud revision cannot open PR',async()=>{
 const stale=await submitEditorReview(context(payload({expectedSha:'11111111-1111-1111-1111-111111111111'})));
 assert.equal(stale.status,409);
 const missing=await submitEditorReview(context(payload(),{BRANDSTUDIO_OBJECTS:{
  idFromName:x=>x,get:()=>({fetch:async()=>result({sha:REV,document:{versions:{}}})})
 }}));
 assert.equal(missing.status,409);
});

test('explicit submit creates a draft PR from the authoritative server snapshot, never client state',async()=>{
 const old=globalThis.fetch,calls=[];
 globalThis.fetch=async(url,options)=>{
  const u=new URL(url);calls.push({path:u.pathname+u.search,method:options.method,body:options.body});
  if(u.pathname.endsWith('/pulls')&&options.method==='GET')return result([]);
  if(u.pathname.includes('/git/ref/heads/studio'))return result({message:'Not Found'},404);
  if(u.pathname.endsWith('/git/ref/heads/main'))return result({object:{sha:'1'.repeat(40)}});
  if(u.pathname.endsWith('/git/refs')&&options.method==='POST')return result({ref:'created'},201);
  if(u.pathname.includes('/contents/')&&options.method==='PUT')return result({content:{sha:'2'.repeat(40)}},201);
  if(u.pathname.endsWith('/pulls')&&options.method==='POST')return result({
   html_url:'https://github.com/cinegitim/design/pull/999',number:999
  },201);
  throw Error('unexpected GitHub API path: '+u.pathname);
 };
 try{
  const response=await submitEditorReview(context());const body=await response.json();
  assert.equal(response.status,201);
  assert.equal(body.status,'pr-open');assert.equal(body.number,999);
  assert.match(body.branch,/^studio\/editor-instagram-kaist/);
  const put=calls.find(x=>x.method==='PUT');assert.ok(put);
  const file=JSON.parse(Buffer.from(JSON.parse(put.body).content,'base64').toString('utf8'));
  assert.deepEqual(file.savedState,STATE);
  assert.equal(file.revision,REV);
  assert.deepEqual(file.approval,{creative:'pending',socialPublished:false});
  const pr=JSON.parse(calls.find(x=>x.method==='POST'&&x.path.endsWith('/pulls')).body);
  assert.equal(pr.draft,true);assert.equal(pr.base,'main');
  assert.equal(calls.filter(x=>x.method==='POST').length,2);
  assert.ok(!calls.some(x=>x.path.includes('/contents/docs/')));
  assert.ok(!JSON.stringify(body).includes(TOK));
 }finally{globalThis.fetch=old}
});

test('repeated click returns existing PR without another branch or write',async()=>{
 const old=globalThis.fetch,calls=[];
 globalThis.fetch=async(url,opts)=>{
  calls.push({url,method:opts.method});
  return result([{html_url:'https://github.com/cinegitim/design/pull/55',number:55,state:'open',merged_at:null}])
 };
 try{
  const r=await submitEditorReview(context());const data=await r.json();
  assert.equal(r.status,200);assert.equal(data.existing,true);
  assert.equal(data.url,'https://github.com/cinegitim/design/pull/55');
  assert.deepEqual(calls.map(c=>c.method),['GET']);
 }finally{globalThis.fetch=old}
});

test('PR credentials remain server side; editor has explicit, unsaved-state guarded UI',()=>{
 const root=path.resolve(import.meta.dirname,'../../..');
 const client=fs.readFileSync(path.join(root,'docs/visual-editor/browser/github-sync.js'),'utf8');
 const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
 const gateway=fs.readFileSync(path.join(root,'studio/cloudflare-brandstudio/asya-gateway/worker.mjs'),'utf8');
 assert.ok(client.includes('openReviewPr'));
 assert.doesNotMatch(client,/api\.github\.com|GITHUB_PR_TOKEN/);
 assert.ok(html.includes('id="style-pr"'));
 assert.ok(html.includes('id="style-pr-status"'));
 assert.match(html,/if\(dirty\|\|autoBusy\|\|JSON\.stringify\(state\)!==JSON\.stringify\(stored\)\)/);
 assert.ok(html.includes("confirm('v'+version"));
 assert.match(gateway,/submitEditorReview\(\{request,env,authenticated:true\}\)/);
});

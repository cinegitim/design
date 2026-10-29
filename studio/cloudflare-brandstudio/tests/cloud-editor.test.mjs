import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const source=fs.readFileSync(path.join(root,'docs/visual-editor/browser/github-sync.js'),'utf8');
const html=fs.readFileSync(path.join(root,'docs/visual-editor/browser/index.html'),'utf8');
function fixture(){
 const data=new Map(),calls=[],auth=[];
 let branch=false,head='basecommit';
 async function fetch(url,opts={}){
  const u=new URL(url),pathname=u.pathname.replace('/repos/cinegitim/design','');
  calls.push([opts.method||'GET',pathname]);
  auth.push(opts.headers?.Authorization||'');
  let code=200,body={};
  if(pathname==='/git/ref/heads/brandstudio-editor-history'){
    if(!branch)code=404;else body={object:{sha:head}}
  } else if(pathname==='/git/ref/heads/main')body={object:{sha:'mainsha'}};
  else if(pathname==='/git/refs'&&opts.method==='POST'){
    assert.equal(JSON.parse(opts.body).ref,'refs/heads/brandstudio-editor-history');branch=true;
    body={ref:'refs/heads/brandstudio-editor-history'}
  } else if(pathname.startsWith('/contents/')){
    let file=decodeURIComponent(pathname.slice('/contents/'.length));
    if(opts.method==='PUT'){
      assert.equal(branch,true);
      const payload=JSON.parse(opts.body);
      if(data.has(file)&&payload.sha!==data.get(file).sha){code=409;body={message:'Conflict'}}
      else if(!data.has(file)&&payload.sha){code=409;body={message:'Conflict'}}
      else {const sha='sha'+(data.size+calls.length);const text=Buffer.from(payload.content,'base64').toString('utf8');data.set(file,{sha,text});head='commit'+calls.length;body={content:{sha},commit:{sha:head}}}
    } else if(data.has(file))body={type:'file',sha:data.get(file).sha,content:Buffer.from(data.get(file).text,'utf8').toString('base64')};
    else code=404;
  } else throw Error('Unexpected endpoint '+pathname);
  return new Response(JSON.stringify(body),{status:code,headers:{'content-type':'application/json'}});
 }
 const sandbox={fetch,URL,Response,TextEncoder,TextDecoder,structuredClone,btoa,atob,console,Math,Date};
 sandbox.globalThis=sandbox;
 vm.runInNewContext(source,sandbox);
 return{cloud:sandbox.BrandstudioCloud,calls,auth,data};
}
const state=(n)=>({colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:n?{'0:2':{styles:{left:n+'px'},mode:'inherit'}}:{},groups:{}});
test('GitHub editor cloud rejects writes unless user supplies repo-scoped token',async()=>{
 const {cloud,calls}=fixture();
 await assert.rejects(cloud.commit({product:'carousel-demo',version:1,state:state(0)}),/access|anahtar/i);
 assert.equal(calls.length,0);
});
test('source v1 is overwritable and history retains every earlier state',async()=>{
 const {cloud,auth,calls}=fixture();
 cloud.setToken('test-only-token');
 let x=await cloud.commit({product:'carousel-demo',version:1,state:state(18),note:'ilk düzenleme'});
 assert.equal(x.document.history.length,2);
 assert.equal(x.document.history[0].kind,'original');
 assert.equal(x.document.history[1].state.edits['0:2'].styles.left,'18px');
 x=await cloud.commit({product:'carousel-demo',version:1,state:state(42),note:'aynı v1 güncellemesi'});
 assert.equal(x.document.history.length,3);
 assert.equal(x.document.versions.v1.state.edits['0:2'].styles.left,'42px');
 assert.equal(x.document.history[1].state.edits['0:2'].styles.left,'18px');
 assert.equal(x.document.history[0].state.edits['0:2'],undefined);
 assert.ok(auth.filter(Boolean).every(x=>x==='Bearer test-only-token'));
 assert.ok(calls.some(x=>x[0]==='POST'&&x[1]==='/git/refs'));
});
test('existing v2 is updated in place; v3 must be created explicitly',async()=>{
 const {cloud}=fixture();cloud.setToken('test-only-token');
 let a=await cloud.commit({product:'carousel-demo',version:2,state:state(20)});
 let b=await cloud.commit({product:'carousel-demo',version:2,state:state(50)});
 assert.deepEqual(Object.keys(b.document.versions),['v2']);
 assert.equal(b.document.history.length,2);
 let c=await cloud.commit({product:'carousel-demo',version:3,state:state(50),kind:'new'});
 assert.deepEqual(Object.keys(c.document.versions),['v2','v3']);
 const restored=await cloud.commit({product:'carousel-demo',version:2,state:b.document.history[0].state,kind:'restore'});
 assert.equal(restored.document.versions.v2.state.edits['0:2'].styles.left,'20px');
 assert.equal(restored.document.history.at(-1).kind,'restore');
 assert.equal(restored.document.history[0].state.edits['0:2'].styles.left,'20px');
});
test('browser editor labels cloud versions distinctly and preserves local saves',()=>{
 assert.match(html,/cloudSelected\?'cloud:'\+current/);
 assert.match(html,/option\.value='cloud:'\+k\.slice\(1\)/);
 assert.match(html,/cloud\.commit\(\{product:slug,version:n,state:checked/);
 assert.match(html,/if\(target\.indexOf\('cloud:'\)===0\)/);
 assert.match(html,/renderCloudHistory\(\)/);
 assert.match(html,/function applyCloudSnapshot/);
 assert.match(html,/\$\('cloud-original'\)\.onclick/);
 assert.match(html,/function loadSavedVersion/);
 assert.match(html,/function dump\(\)/);
 assert.doesNotMatch(source,/localStorage|sessionStorage|document\.cookie/);
});
test('PNG and JPEG export actual canvases, not renamed HTML',()=>{
 assert.match(html,/id="raster-format"/);
 assert.match(html,/value="png"/);
 assert.match(html,/value="jpeg"/);
 assert.match(html,/html2canvas\.min\.js/);
 assert.match(html,/html2canvas\(slide/);
 assert.match(html,/canvas\.toBlob/);
 assert.match(html,/blob\.size<1000/);
 const vendor=fs.readFileSync(path.join(root,'docs/visual-editor/browser/html2canvas.min.js'),'utf8');
 assert.ok(vendor.length>190000);
 assert.match(vendor,/html2canvas/i);
});
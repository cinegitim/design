// Explicit, fail-closed GitHub review PR export of a *saved* Brandstudio revision.
// Called only by the authenticated Brandstudio gateway; no GitHub token is sent to browsers.
// Review snapshots never alter main/source HTML and never constitute creative or social approval.
const REPO='cinegitim/design';
const API='https://api.github.com/repos/'+REPO;
const PRODUCT=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const REVISION=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const out=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{
 'content-type':'application/json; charset=utf-8','cache-control':'no-store',
 'x-content-type-options':'nosniff','referrer-policy':'no-referrer'
}});
class GithubFailure extends Error {
 constructor(status){super('GitHub request failed');this.status=status}
}
function validInput(x){
 return x&&typeof x==='object'&&!Array.isArray(x)&&
  Object.keys(x).length===4&&x.acknowledgePublicRepository===true&&
  typeof x.product==='string'&&x.product.length<=130&&PRODUCT.test(x.product)&&
  Number.isInteger(x.version)&&x.version>=1&&x.version<=26&&
  typeof x.expectedSha==='string'&&REVISION.test(x.expectedSha);
}
function encodeUtf8(raw){
 const bytes=new TextEncoder().encode(raw);
 let binary='';
 for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
 return btoa(binary);
}
async function github(token,path,method='GET',data){
 const headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'Brandstudio-Editor-Review'};
 if(data!==undefined)headers['content-type']='application/json';
 const response=await fetch(API+path,{method,headers,
  body:data===undefined?undefined:JSON.stringify(data),redirect:'manual'});
 if(response.status===404)throw new GithubFailure(404);
 if(!response.ok)throw new GithubFailure(response.status);
 return response.status===204?null:response.json();
}
async function storedRevision(env,product,version,expectedSha){
 const ns=env.BRANDSTUDIO_OBJECTS;
 if(!ns)throw new Error('storage-unavailable');
 const url='https://brandstudio.internal/revisions?product='+encodeURIComponent(product);
 const response=await ns.get(ns.idFromName(product)).fetch(url);
 if(!response.ok)throw new Error('storage-unavailable');
 const data=await response.json();
 if(data?.sha!==expectedSha)throw new GithubFailure(409);
 const state=data?.document?.versions?.['v'+version]?.state;
 if(!state||typeof state!=='object'||Array.isArray(state)||
    !state.colors||!state.edits||!state.groups)throw new GithubFailure(409);
 return state;
}
function validPRUrl(value){
 return typeof value==='string'&&/^https:\/\/github\.com\/cinegitim\/design\/pull\/[1-9]\d*$/.test(value);
}
export function reviewPrStatus(context){
 if(!context.authenticated)return out({error:'Admin girişi gerekli'},401);
 return out({enabled:typeof context.env?.GITHUB_PR_TOKEN==='string'&&context.env.GITHUB_PR_TOKEN.length>=20,
  repo:REPO,mode:'draft-review-only'});
}
export async function submitEditorReview(context){
 const {request:req,env,authenticated}=context;
 if(!authenticated)return out({error:'Admin girişi gerekli'},401);
 const u=new URL(req.url);
 if(req.method!=='POST')return out({error:'Yöntem desteklenmiyor'},405);
 if(u.pathname!=='/visual-editor/api/github-pr')return out({error:'Yol bulunamadı'},404);
 if(req.headers.get('Origin')!==u.origin||req.headers.get('X-Brandstudio-Editor')!=='1'||
    !req.headers.get('Content-Type')?.startsWith('application/json'))
  return out({error:'Güvenli istek doğrulanamadı'},403);
 const raw=await req.text();
 if(raw.length>1200)return out({error:'İstek çok büyük'},413);
 let input;
 try{input=JSON.parse(raw)}catch(_){return out({error:'Geçersiz JSON'},400)}
 if(!validInput(input))return out({error:'Geçersiz PR isteği veya açık onay eksik'},400);
 const token=env.GITHUB_PR_TOKEN;
 if(typeof token!=='string'||token.length<20)
  return out({error:'GitHub PR bağlantısı henüz yapılandırılmadı'},503);
 try{
  const {product,version,expectedSha}=input;
  // Never trust a client-sent design state. Read exactly the Durable Object revision.
  const state=await storedRevision(env,product,version,expectedSha);
  const rev=expectedSha.replace(/-/g,'').slice(0,12);
  const branch='studio/editor-'+product.slice(0,70)+'-v'+version+'-'+rev;
  const path='studio/production/editor-proposals/'+product+'/v'+version+'-'+rev+'.json';
  const existing=await github(token,'/pulls?state=all&head=cinegitim%3A'+encodeURIComponent(branch)+'&base=main&per_page=20');
  const prior=Array.isArray(existing)&&existing.find(p=>validPRUrl(p.html_url));
  if(prior)return out({status:prior.merged_at?'merged':prior.state==='open'?'pr-open':'closed',
   url:prior.html_url,number:prior.number,branch,revision:expectedSha,existing:true});
  // A dangling branch may indicate partial upstream failure; do not overwrite or rebase it.
  let found=false;
  try{await github(token,'/git/ref/heads/'+branch);found=true}
  catch(e){if(!(e instanceof GithubFailure&&e.status===404))throw e}
  if(found)return out({error:'Bu sürüm için GitHub dalı var ancak PR doğrulanamadı; manuel inceleme gerekli'},409);
  const base=await github(token,'/git/ref/heads/main');
  if(!/^[a-f0-9]{40}$/.test(base?.object?.sha||''))throw new Error('invalid-base-ref');
  const snapshot={schema:1,kind:'brandstudio-editor-review',product,version,
   revision:expectedSha,source:'cloudflare-durable-object',savedState:state,
   approval:{creative:'pending',socialPublished:false},github:{status:'submitted-for-review'}};
  const serialized=JSON.stringify(snapshot,null,2)+'\n';
  if(new TextEncoder().encode(serialized).length>800000)
   return out({error:'Sürüm GitHub inceleme sınırını aşıyor; görsel varlıkları ayırın'},413);
  await github(token,'/git/refs','POST',{ref:'refs/heads/'+branch,sha:base.object.sha});
  await github(token,'/contents/'+path,'PUT',{message:'review: '+product+' v'+version+' cloud snapshot',
   content:encodeUtf8(serialized),branch});
  const description=[
   '## Brandstudio Visual Editor review (not publication)',
   '- Product: '+product,
   '- Saved version: v'+version,
   '- Immutable cloud revision at request time: '+expectedSha,
   '- Snapshot: '+path,
   '- State JSON is a review artifact; original HTML/CSS/SVG source and approved logos remain unchanged.',
   '- Approval: **pending**. No social publication, no rendered quality sign-off.',
   '- Review the snapshot against canonical brand locks, original source and browser rendering before merging.',
   '- Public repository: submitted only after the administrator explicitly acknowledged public visibility.'
  ].join('\n');
  const pr=await github(token,'/pulls','POST',{title:'Brandstudio editor review: '+product+' v'+version,
   head:branch,base:'main',body:description,draft:true,maintainer_can_modify:false});
  if(!validPRUrl(pr?.html_url)||!Number.isInteger(pr?.number))
   throw new Error('invalid-pr-response');
  return out({status:'pr-open',url:pr.html_url,number:pr.number,branch,
   revision:expectedSha,existing:false},201);
 }catch(e){
  if(e instanceof GithubFailure){
   if(e.status===409)return out({error:'Bulut kaydı değişti. Güncel sürümü yükleyip tekrar deneyin.'},409);
   if(e.status===401||e.status===403)return out({error:'GitHub yetkilendirmesi başarısız veya izinler yetersiz'},503);
   console.error('Brandstudio GitHub request failed',e.status);
  }else console.error('Brandstudio GitHub review failed',String(e?.message||e));
  return out({error:'GitHub inceleme PR’ı oluşturulamadı; tamamlandı olarak işaretlenmedi'},502);
 }
}

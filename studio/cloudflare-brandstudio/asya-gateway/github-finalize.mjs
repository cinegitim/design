// Single product-level, explicit and review-only GitHub transfer.
// Cloudflare stores drafts; this endpoint never persists an editor edit, merges, or publishes.
const REPO='cinegitim/design';
const API='https://api.github.com/repos/'+REPO;
const STATIC='https://brandstudio-pages-git.pages.dev';
const SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const REV=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SHA=/^[0-9a-f]{40}$/i;
const MAX_BODY=6200000,MAX_FILE=250000,MAX_FILES=600;
const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{
 'content-type':'application/json; charset=utf-8','cache-control':'no-store',
 'x-content-type-options':'nosniff','referrer-policy':'no-referrer'
}});
class GitFailure extends Error {
 constructor(status){super('GitHub API returned '+status);this.status=status}
}
async function git(token,path,method='GET',data){
 const headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'Brandstudio-Product-Finalization'};
 if(data!==undefined)headers['content-type']='application/json';
 const r=await fetch(API+path,{method,headers,body:data===undefined?undefined:JSON.stringify(data),redirect:'manual'});
 if(!r.ok)throw new GitFailure(r.status);
 return r.status===204?null:r.json()
}
const safeProduct=x=>typeof x==='string'&&x.length<=130&&SLUG.test(x);
const safeRev=x=>typeof x==='string'&&REV.test(x);
const cleanPR=x=>typeof x==='string'&&/^https:\/\/github\.com\/cinegitim\/design\/pull\/[1-9]\d*$/.test(x);
const byteLength=x=>new TextEncoder().encode(x).length;
const tagVersion=v=>'v'+String(v).padStart(2,'0');
const tagSlide=i=>String(i+1).padStart(2,'0');
const orderedVersions=doc=>Object.keys(doc?.versions||{}).map(k=>/^v([1-9]|1\d|2[0-6])$/.exec(k)).filter(Boolean).map(m=>Number(m[1])).sort((a,b)=>a-b);
async function authoritative(env,product,expectedSha){
 if(!env.BRANDSTUDIO_OBJECTS)throw Error('storage-not-configured');
 const ns=env.BRANDSTUDIO_OBJECTS;
 const r=await ns.get(ns.idFromName(product)).fetch('https://brandstudio.internal/revisions?product='+encodeURIComponent(product));
 if(!r.ok)throw Error('storage-read-failed');
 const stored=await r.json();
 if(stored.sha!==expectedSha)throw new GitFailure(409);
 if(!stored.document||!Array.isArray(stored.document.history)||!stored.document.versions)throw new GitFailure(409);
 return stored.document
}
async function canonicalProduct(product){
 const r=await fetch(STATIC+'/visual-editor/browser/catalog.json',{headers:{Accept:'application/json'},cf:{cacheTtl:120}});
 if(!r.ok)throw Error('catalog-unavailable');
 const catalog=await r.json();
 if(!Array.isArray(catalog))throw Error('invalid-catalog');
 const x=catalog.find(p=>p.id===product);
 if(!x||x.kind!=='html'||!Array.isArray(x.pages)||x.pages.length<1||x.pages.length>25||
    x.pages.some(p=>typeof p!=='string'||p.length>220||!SLUG.test(p.split('/')[0])||!/^[-a-z0-9_/]+\.(?:html|htm)$/.test(p)||p.includes('..')))
  throw new GitFailure(422);
 return x
}
function validateInput(x){
 return x&&typeof x==='object'&&!Array.isArray(x)&&
 Object.keys(x).sort().join(',')==='acknowledgePublicRepository,expectedSha,files,product,selectedVersion,sourcePages'&&
 x.acknowledgePublicRepository===true&&safeProduct(x.product)&&safeRev(x.expectedSha)&&
 Number.isInteger(x.selectedVersion)&&x.selectedVersion>=1&&x.selectedVersion<=26&&
 Array.isArray(x.sourcePages)&&Array.isArray(x.files)&&x.files.length<=MAX_FILES;
}
function validateFiles(input,product,versions){
 const pages=product.pages;
 if(JSON.stringify(input.sourcePages)!==JSON.stringify(pages))throw new GitFailure(409);
 const expected=new Set();
 for(const n of versions)for(let i=0;i<pages.length;i++)for(const ext of ['html','css'])
  expected.add('versions/'+tagVersion(n)+'/slides/'+tagSlide(i)+'.'+ext);
 if(!expected.size||expected.size>MAX_FILES||input.files.length!==expected.size)throw new GitFailure(413);
 const actual=new Map();
 let total=0;
 for(const file of input.files){
  if(!file||typeof file!=='object'||Array.isArray(file)||Object.keys(file).sort().join(',')!=='content,path'||
     typeof file.path!=='string'||!expected.has(file.path)||actual.has(file.path)||typeof file.content!=='string')
   throw new GitFailure(400);
  const size=byteLength(file.content);
  if(!size||size>MAX_FILE)throw new GitFailure(413);
  if(file.path.endsWith('.html')&&!/<!doctype html>/i.test(file.content.slice(0,100)))throw new GitFailure(400);
  actual.set(file.path,file.content);total+=size;
  if(total>MAX_BODY-1000000)throw new GitFailure(413);
 }
 if(actual.size!==expected.size)throw new GitFailure(400);
 return actual
}
export function finalizationStatus(context){
 if(!context.authenticated)return response({error:'Admin girişi gerekli'},401);
 return response({enabled:typeof context.env?.GITHUB_PR_TOKEN==='string'&&context.env.GITHUB_PR_TOKEN.length>=20,
  repo:REPO,mode:'product-bulk-draft-review'});
}
export async function submitProductFinalization(context){
 const {request:req,env,authenticated}=context;
 if(!authenticated)return response({error:'Admin girişi gerekli'},401);
 const u=new URL(req.url);
 if(req.method!=='POST'||u.pathname!=='/visual-editor/api/finalize')return response({error:'Yöntem veya yol geçersiz'},405);
 if(req.headers.get('Origin')!==u.origin||req.headers.get('X-Brandstudio-Editor')!=='1'||
    !req.headers.get('Content-Type')?.startsWith('application/json'))return response({error:'Güvenli istek doğrulanamadı'},403);
 const size=Number(req.headers.get('content-length')||0);
 if(size>MAX_BODY)return response({error:'Paket boyutu sınırı aşıldı'},413);
 const raw=await req.text();
 if(byteLength(raw)>MAX_BODY)return response({error:'Paket çok büyük'},413);
 let input;
 try{input=JSON.parse(raw)}catch(_){return response({error:'Geçersiz JSON'},400)}
 if(!validateInput(input))return response({error:'Geçersiz ürün paketi veya açık GitHub onayı eksik'},400);
 const token=env.GITHUB_PR_TOKEN;
 if(typeof token!=='string'||token.length<20)return response({error:'GitHub bağlantısı yapılandırılmadı'},503);
 try{
  const {product,expectedSha,selectedVersion}=input;
  // Trust only the authoritative cloud revisions. Browser may supply derived HTML/CSS for human review,
  // but cannot supply/rewrite saved-state JSON, product identity, paths or version inventory.
  const [doc,canonical]=await Promise.all([authoritative(env,product,expectedSha),canonicalProduct(product)]);
  const versions=orderedVersions(doc);
  if(!versions.length||!versions.includes(selectedVersion))throw new GitFailure(409);
  const files=validateFiles(input,canonical,versions);
  const suffix=expectedSha.replace(/-/g,'').slice(0,12);
  const branch='studio/finalize-'+product.slice(0,62)+'-'+suffix;
  const prefix='studio/production/finalized/'+product+'/'+suffix+'/';
  const prior=await git(token,'/pulls?state=all&head=cinegitim%3A'+encodeURIComponent(branch)+'&base=main&per_page=20');
  const existing=Array.isArray(prior)&&prior.find(p=>cleanPR(p.html_url));
  if(existing)return response({status:existing.merged_at?'merged':existing.state==='open'?'pr-open':'closed',
   url:existing.html_url,number:existing.number,branch,existing:true,versions:versions.length});
  let exists=false;
  try{await git(token,'/git/ref/heads/'+branch);exists=true}
  catch(e){if(!(e instanceof GitFailure&&e.status===404))throw e}
  if(exists)return response({error:'Bu ürün paketi için GitHub dalı mevcut; PR doğrulanamadı. İnceleme gerekli.'},409);
  const main=await git(token,'/git/ref/heads/main'),baseSha=main?.object?.sha;
  if(!SHA.test(baseSha||''))throw Error('invalid-main');
  const commit=await git(token,'/git/commits/'+baseSha),baseTree=commit?.tree?.sha;
  if(!SHA.test(baseTree||''))throw Error('invalid-main-tree');
  const entries=[];
  const add=(name,content)=>entries.push({path:prefix+name,mode:'100644',type:'blob',content});
  for(const [file,content] of [...files.entries()].sort((a,b)=>a[0].localeCompare(b[0])))add(file,content);
  for(const n of versions){
   const saved=doc.versions['v'+n];
   add('versions/'+tagVersion(n)+'/editor-state.json',JSON.stringify({
    schema:1,kind:'brandstudio-saved-editor-version',product,version:n,
    updatedAt:saved.updatedAt||null,note:saved.note||'',state:saved.state
   },null,2)+'\n');
  }
  add('history.json',JSON.stringify({schema:1,product,history:doc.history},null,2)+'\n');
  const manifest={schema:1,kind:'brandstudio-product-finalization',product,
   title:canonical.title||product,brand:canonical.family||null,
   selectedVersion,versions,revision:expectedSha,exportedAt:new Date().toISOString(),
   source:{repository:REPO,baseCommit:baseSha,paths:canonical.pages.map(p=>'docs/'+p)},
   files:{renderedSlides:files.size,versionStates:versions.length,history:'history.json'},
   review:{creative:'pending',socialPublished:false,sourceAuditRequired:true},
   explanation:'Saved states are server-authoritative; browser-generated HTML/CSS is for human source and visual review. No publication.'};
  add('manifest.json',JSON.stringify(manifest,null,2)+'\n');
  if(entries.length>MAX_FILES+28)throw new GitFailure(413);
  // One tree, one commit, one draft PR for the ENTIRE product.
  const tree=await git(token,'/git/trees','POST',{base_tree:baseTree,tree:entries});
  if(!SHA.test(tree?.sha||''))throw Error('invalid-tree-response');
  const made=await git(token,'/git/commits','POST',{
   message:'review: finalize '+product+' ('+versions.length+' saved versions)',
   tree:tree.sha,parents:[baseSha]});
  if(!SHA.test(made?.sha||''))throw Error('invalid-commit-response');
  await git(token,'/git/refs','POST',{ref:'refs/heads/'+branch,sha:made.sha});
  const body=[
   '## Brandstudio: completed product handoff for review',
   '- Product: '+product,
   '- Selected production candidate: v'+selectedVersion,
   '- Saved versions in one transfer: '+versions.map(v=>'v'+v).join(', '),
   '- Editable HTML/CSS slides: '+files.size,
   '- Saved cloud revision: '+expectedSha,
   '- Original source pinned to main commit: '+baseSha,
   '- Package: '+prefix+'manifest.json',
   '- This is a **draft review PR**, not a publication, merge, or creative approval.',
   '- Compare the generated source to the saved states, canonical logos, font assets, and visual preview before approval.'
  ].join('\n');
  const pr=await git(token,'/pulls','POST',{title:'Brandstudio product handoff: '+product,
   head:branch,base:'main',draft:true,body,maintainer_can_modify:false});
  if(!cleanPR(pr?.html_url)||!Number.isInteger(pr?.number))throw Error('invalid-pr-response');
  return response({status:'pr-open',url:pr.html_url,number:pr.number,branch,
   revision:expectedSha,versions:versions.length,renderedSlides:files.size,existing:false},201);
 }catch(e){
  if(e instanceof GitFailure){
   if(e.status===400)return response({error:'Paket dosyaları beklenen sürüm ve slaytlarla eşleşmiyor'},400);
   if(e.status===409)return response({error:'Bulut sürümü veya kaynak kataloğu değişmiş; güncel kaydı açın'},409);
   if(e.status===413)return response({error:'Ürün paketi güvenli aktarım sınırını aştı; tek bir PR içinde daha büyük paket desteği gerekli'},413);
   if(e.status===422)return response({error:'Bu ürün türü için HTML/CSS toplu aktarım henüz desteklenmiyor'},422);
   if(e.status===401||e.status===403)return response({error:'GitHub erişim yetkisi geçersiz'},503);
   console.error('Brandstudio finalized package GitHub failure',e.status);
  }else console.error('Brandstudio finalize failed',String(e?.message||e));
  return response({error:'GitHub aktarımı tamamlanamadı; ürün tamamlandı olarak işaretlenmedi'},502);
 }
}

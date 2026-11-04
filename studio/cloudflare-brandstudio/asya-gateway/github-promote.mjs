// On-demand, explicitly approved source promotion. No cron, no direct publication.
const API='https://api.github.com/repos/cinegitim/design';
const SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const UUID=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;
const SHA=/^[a-f0-9]{40}$/i;
const SOURCE=/^docs\/([a-z0-9-]+\/[a-z0-9-]+)\/v([1-9][0-9]*)\/(source)\/([a-z0-9-]+\.html)$/;
const PR_URL=/^https:\/\/github\.com\/cinegitim\/design\/pull\/[1-9]\d*$/;
const encoder=new TextEncoder(),decoder=new TextDecoder();
const json=(x,status=200)=>new Response(JSON.stringify(x),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
class Failure extends Error{constructor(status,message){super(message);this.status=status}}
const ensure=(ok,status,message)=>{if(!ok)throw new Failure(status,message)};
async function git(token,path,method='GET',body){
 const h={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'Brandstudio-Promote'};
 if(body!==undefined)h['content-type']='application/json';
 const r=await fetch(API+path,{method,headers:h,body:body===undefined?undefined:JSON.stringify(body),redirect:'manual'});
 if(!r.ok)throw new Failure(r.status,'GitHub yanıtı: '+r.status);
 return r.status===204?null:r.json();
}
function apiPath(path){return path.split('/').map(encodeURIComponent).join('/')}
async function getFile(token,path){
 const f=await git(token,'/contents/'+apiPath(path)+'?ref=main');
 ensure(f?.type==='file'&&f?.encoding==='base64'&&typeof f.content==='string'&&f.content.length<1500000,409,'Kaynak dosya geçersiz: '+path);
 return decoder.decode(Uint8Array.from(atob(f.content.replace(/\s/g,'')),c=>c.charCodeAt(0)));
}
async function onMain(token,path){
 try{await git(token,'/contents/'+apiPath(path)+'?ref=main');return true}
 catch(e){if(e instanceof Failure&&e.status===404)return false;throw e}
}
function planPaths(paths){
 ensure(Array.isArray(paths)&&paths.length>=1&&paths.length<=25,422,'Desteklenmeyen slayt sayısı');
 const a=paths.map(p=>SOURCE.exec(p));
 ensure(a.every(Boolean),422,'Yeni sürüm için standart vN/source kaynak yapısı gerekli');
 const first=a[0];
 ensure(a.every(m=>m[1]===first[1]&&m[2]===first[2]&&m[3]===first[3])&&
  new Set(paths).size===paths.length,422,'Kaynak dosyaları aynı sürüme ait değil');
 const version=Number(first[2]);
 ensure(Number.isInteger(version)&&version<50,422,'Sürüm sınırı aşıldı');
 return{folder:first[1],version,names:a.map(m=>m[4])};
}
function rebase(html,css,oldPath,newPath){
 ensure(typeof html==='string'&&typeof css==='string'&&encoder.encode(html).length<=250000&&
  encoder.encode(css).length<=250000,413,'Kaynak dosya büyük');
 ensure(/<!doctype html>/i.test(html.slice(0,100))&&/<html\b/i.test(html)&&/<\/head>/i.test(html)&&
  /class="slide\b/i.test(html),422,'Düzenlenmiş HTML geçersiz');
 ensure((html.match(/<base\b/gi)||[]).length===1&&!/<script\b/i.test(html)&&
  !/<\/style/i.test(css)&&css.includes('{')&&css.includes('}'),422,'Kaynak varlıkları doğrulanamadı');
 const a=newPath.split('/').slice(0,-1),b=oldPath.split('/');let n=0;
 while(n<a.length&&a[n]===b[n])n++;
 const base='../'.repeat(a.length-n)+b.slice(n).join('/');
 const out=html.replace(/<base\b[^>]*>/i,'<base href="'+base+'" data-brandstudio-source-base="immutable">');
 return out.replace(/<\/head>/i,'<style data-brandstudio-promoted="true">\n'+css+'\n</style></head>');
}
function gallery(title,paths,oldVersion,cloudSha){
 const clean=title.replace(/[&<>"]/g,'');
 return '<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
  '<title>'+clean+' · Brandstudio</title><style>body{font:18px/1.5 system-ui;max-width:800px;margin:40px auto;padding:0 20px}li{padding:7px}</style></head><body>'+
  '<h1>'+clean+'</h1><p>Visual Editor kaynak sürümü · Sosyal medyada yayımlanmadı.</p>'+
  '<p>Önceki kaynak v'+oldVersion+' · Bulut kaydı '+cloudSha+'</p><ol>'+
  paths.map((p,i)=>'<li><a href="source/'+p.split('/').at(-1)+'">Slayt '+(i+1)+'</a></li>').join('')+
  '</ol></body></html>\n';
}
const valid=x=>!!x&&typeof x==='object'&&!Array.isArray(x)&&
 Object.keys(x).sort().join(',')==='acknowledgeNewGitHubVersion,expectedSha,product,selectedVersion'&&
 x.acknowledgeNewGitHubVersion===true&&typeof x.product==='string'&&x.product.length<=130&&SLUG.test(x.product)&&
 typeof x.expectedSha==='string'&&UUID.test(x.expectedSha)&&
 Number.isInteger(x.selectedVersion)&&x.selectedVersion>=1&&x.selectedVersion<=26;
export function promotionStatus({authenticated,env}){
 if(!authenticated)return json({error:'Admin oturumu gerekli'},401);
 return json({enabled:typeof env?.GITHUB_PR_TOKEN==='string'&&env.GITHUB_PR_TOKEN.length>=20,
  mode:'immutable-new-source-version',repo:'cinegitim/design'});
}
export async function submitSourcePromotion({authenticated,request:req,env}){
 if(!authenticated)return json({error:'Admin oturumu gerekli'},401);
 const url=new URL(req.url);
 if(req.method!=='POST'||url.pathname!=='/visual-editor/api/promote')return json({error:'Desteklenmeyen yöntem'},405);
 if(req.headers.get('Origin')!==url.origin||req.headers.get('X-Brandstudio-Editor')!=='1'||
    !req.headers.get('Content-Type')?.startsWith('application/json'))return json({error:'Güvenli istek geçersiz'},403);
 let input;
 try{const text=await req.text();ensure(encoder.encode(text).length<=2048,413,'İstek büyük');input=JSON.parse(text)}
 catch(e){return json({error:'Geçersiz JSON'},400)}
 if(!valid(input))return json({error:'Geçersiz ürün, sürüm veya GitHub onayı'},400);
 const token=env.GITHUB_PR_TOKEN;
 if(typeof token!=='string'||token.length<20)return json({error:'GitHub bağlantısı yok'},503);
 try{
  const {product,expectedSha,selectedVersion}=input;
  ensure(env.BRANDSTUDIO_OBJECTS,503,'Bulut kaydı erişilemiyor');
  const obj=env.BRANDSTUDIO_OBJECTS;
  const rev=await obj.get(obj.idFromName(product)).fetch('https://brandstudio.internal/revisions?product='+encodeURIComponent(product));
  ensure(rev.ok,503,'Bulut kaydı alınamadı');
  const cloud=await rev.json();
  ensure(cloud.sha===expectedSha&&cloud.document?.versions?.['v'+selectedVersion]?.state,409,'Bulut kaydı güncel değil');
  const suffix=expectedSha.replace(/-/g,'').slice(0,12);
  const oldBranch='studio/finalize-'+product.slice(0,62)+'-'+suffix;
  const handed=await git(token,'/pulls?state=all&head=cinegitim%3A'+encodeURIComponent(oldBranch)+'&base=main&per_page=20');
  const handoff=Array.isArray(handed)&&handed.find(p=>p.head?.ref===oldBranch||p.head?.label==='cinegitim:'+oldBranch);
  ensure(handoff&&handoff.state==='closed'&&handoff.merged_at,409,'Önce toplu teslim PR birleştirilmeli');
  const archived='studio/production/finalized/'+product+'/'+suffix+'/';
  const manifest=JSON.parse(await getFile(token,archived+'manifest.json'));
  ensure(manifest.kind==='brandstudio-product-finalization'&&manifest.product===product&&
   manifest.revision===expectedSha&&manifest.selectedVersion===selectedVersion&&
   manifest.source?.repository==='cinegitim/design'&&SHA.test(manifest.source.baseCommit||''),
   409,'Teslim paketi ve seçilen sürüm uyuşmuyor');
  const parsed=planPaths(manifest.source.paths);
  ensure(parsed.folder.startsWith('instagram/'),422,'İlk pilot yalnızca Instagram karusellerini destekliyor');
  const catalog=JSON.parse(await getFile(token,'docs/visual-editor/browser/catalog.json'));
  const current=Array.isArray(catalog)&&catalog.find(x=>x.id===product&&x.kind==='html');
  ensure(current&&JSON.stringify(current.pages.map(x=>'docs/'+x))===JSON.stringify(manifest.source.paths),
   409,'Kaynak kataloğu farklı');
  const groups=JSON.parse(await getFile(token,'docs/visual-editor/browser/product-groups.json'));
  const family=groups.groups?.find(g=>g.versions?.some(v=>v.id===product));
  ensure(family&&family.currentId===product&&family.id+'-v'+parsed.version===product,
   409,'Yalnızca en güncel kaynak sürümü yükseltilebilir');
  const v=parsed.version+1,nextId=family.id+'-v'+v;
  ensure(!family.versions.some(x=>x.id===nextId),409,'Yeni sürüm zaten tanımlı');
  const targetPrefix='docs/'+parsed.folder+'/v'+v+'/';
  const dest=parsed.names.map(name=>targetPrefix+'source/'+name);
  const promotionBranch='studio/promote-'+product.slice(0,58)+'-'+suffix;
  const prior=await git(token,'/pulls?state=all&head=cinegitim%3A'+encodeURIComponent(promotionBranch)+'&base=main&per_page=20');
  const existing=Array.isArray(prior)&&prior.find(x=>PR_URL.test(x.html_url||''));
  if(existing)return json({status:existing.merged_at?'merged':existing.state==='open'?'pr-open':'closed',
   existing:true,url:existing.html_url,number:existing.number,newVersion:v,newProduct:nextId});
  try{await git(token,'/git/ref/heads/'+promotionBranch);throw new Failure(409,'Önceki sürüm dalı var')}
  catch(e){if(!(e instanceof Failure&&e.status===404))throw e}
  ensure(!(await onMain(token,dest[0])),409,'Hedef v'+v+' dosyası zaten mevcut');
  const stateDoc=JSON.parse(await getFile(token,archived+'versions/v'+String(selectedVersion).padStart(2,'0')+'/editor-state.json'));
  ensure(stateDoc.product===product&&stateDoc.version===selectedVersion&&
   JSON.stringify(stateDoc.state)===JSON.stringify(cloud.document.versions['v'+selectedVersion].state),
   409,'Onaylı kaynak bulut durumuyla uyuşmuyor');
  const exportRoot=archived+'versions/v'+String(selectedVersion).padStart(2,'0')+'/slides/';
  const entries=await Promise.all(dest.map(async(path,i)=>{
   const n=String(i+1).padStart(2,'0');
   const [html,css]=await Promise.all([getFile(token,exportRoot+n+'.html'),getFile(token,exportRoot+n+'.css')]);
   return{path,mode:'100644',type:'blob',content:rebase(html,css,manifest.source.paths[i],path)}
  }));
  family.versions.push({id:nextId,label:'v'+v+' · Visual Editor kaynak sürümü'});
  family.currentId=nextId;
  catalog.push({id:nextId,title:family.title+' · v'+v,family:current.family,kind:'html',pages:dest.map(p=>p.slice(5))});
  entries.push(
   {path:targetPrefix+'index.html',mode:'100644',type:'blob',content:gallery(family.title+' · v'+v,dest,parsed.version,expectedSha)},
   {path:targetPrefix+'brandstudio-version.json',mode:'100644',type:'blob',content:JSON.stringify({
    schema:1,productId:nextId,previousProductId:product,editorVersion:selectedVersion,sourceVersion:v,
    cloudRevision:expectedSha,finalizationPR:handoff.number,socialPublished:false,
    sharedAssetSource:'docs/'+parsed.folder+'/v'+parsed.version+'/'},null,2)+'\n'},
   {path:'docs/visual-editor/browser/product-groups.json',mode:'100644',type:'blob',content:JSON.stringify(groups,null,2)+'\n'},
   {path:'docs/visual-editor/browser/catalog.json',mode:'100644',type:'blob',content:JSON.stringify(catalog,null,2)+'\n'}
  );
  const main=await git(token,'/git/ref/heads/main');
  ensure(SHA.test(main?.object?.sha||''),503,'GitHub ana dalı bulunamadı');
  const parent=await git(token,'/git/commits/'+main.object.sha);
  ensure(SHA.test(parent?.tree?.sha||''),503,'GitHub dosya ağacı bulunamadı');
  const tree=await git(token,'/git/trees','POST',{base_tree:parent.tree.sha,tree:entries});
  ensure(SHA.test(tree?.sha||''),502,'Kaynak dosya ağacı oluşturulamadı');
  const commit=await git(token,'/git/commits','POST',{
   message:'review: new immutable source version '+nextId,tree:tree.sha,parents:[main.object.sha]});
  ensure(SHA.test(commit?.sha||''),502,'Kaynak commit’i oluşturulamadı');
  await git(token,'/git/refs','POST',{ref:'refs/heads/'+promotionBranch,sha:commit.sha});
  const body=[
   '## Brandstudio · yeni kaynak sürümü',
   '- Ürün: '+product+' → '+nextId,
   '- Bulut kaydı: v'+selectedVersion+' · '+expectedSha,
   '- Toplu teslim PR: #'+handoff.number+' (birleştirilmiş)',
   '- Yeni HTML/CSS kaynakları yalnız v'+v+' klasöründe; v'+parsed.version+' korunur.',
   '- Onaylı logo, görsel ve fontlar eski sürümün ortak varlıklarına bağlı kalır.',
   '- Katalogda currentId güncellenir, varsayılan ve yayımlanmış sürüm değişmez.',
   '- Taslak PR; sosyal medya yayını yapılmaz.'
  ].join('\n');
  const pr=await git(token,'/pulls','POST',{title:'Brandstudio kaynak sürümü '+nextId,
   head:promotionBranch,base:'main',draft:true,maintainer_can_modify:false,body});
  ensure(PR_URL.test(pr?.html_url||'')&&Number.isInteger(pr.number),502,'GitHub PR doğrulanamadı');
  return json({status:'pr-open',url:pr.html_url,number:pr.number,newProduct:nextId,newVersion:v,
   sourceFiles:dest.length,existing:false,fromFinalizationPR:handoff.number},201);
 }catch(e){
  if(e instanceof Failure){
   const code=[400,409,413,422].includes(e.status)?e.status:(e.status===401||e.status===403?503:502);
   return json({error:e.message},code);
  }
  console.error('Brandstudio promotion failed',String(e?.message||e));
  return json({error:'Yeni kaynak sürümü oluşturulamadı; mevcut sürümler korunuyor'},502);
 }
}

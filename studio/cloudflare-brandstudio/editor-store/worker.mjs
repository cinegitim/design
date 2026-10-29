// Brandstudio revisions — isolated free-plan SQLite-backed Durable Object.
// This Worker has no public API; Cloudflare Pages calls the object through a binding.
// Atomic compare-and-swap and durable history live in this dedicated object store.
const KEY=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const BASE="https://raw.githubusercontent.com/cinegitim/design/brandstudio-editor-history/docs/visual-editor/browser/cloud/";
const LIMIT=950000,MAX_HISTORY=240;
const json=(o,status=200)=>new Response(JSON.stringify(o),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
const invalid=(message,status=400)=>json({error:message},status);
function valid(p){return typeof p==="string"&&p.length<=130&&KEY.test(p)}
export class BrandstudioRevisionObject {
 constructor(ctx,env){this.ctx=ctx;this.env=env}
 async initial(product){
  const stored=await this.ctx.storage.get("record");
  if(stored)return stored;
  // Read-only, one-time bootstrap from the archived browser revisions. No PAT needed.
  const url=BASE+encodeURIComponent(product)+".json";
  let response;
  try{response=await fetch(url,{cache:"no-store",redirect:"error"})}
  catch(e){throw Error("Geçmiş arşivine ulaşılamadı")}
  if(response.status===404)return {sha:null,document:{schema:1,product,versions:{},history:[]}};
  if(!response.ok)throw Error("Geçmiş arşivi geçici olarak okunamıyor");
  const raw=await response.text();
  if(raw.length>LIMIT)throw Error("Arşiv boyutu sınırı");
  let doc;try{doc=JSON.parse(raw)}catch(e){throw Error("Arşiv biçimi")}
  if(doc.schema!==1||doc.product!==product||!doc.versions||!Array.isArray(doc.history))throw Error("Arşiv kimliği uyuşmuyor");
  const value={sha:product==="instagram-creative-breakout-bavul-001"?"legacy-v2":"initial-archive",document:doc};
  await this.ctx.storage.put("record",value);
  return value
 }
 async fetch(request){
  const u=new URL(request.url),product=u.searchParams.get("product");
  if(!valid(product))return invalid("Geçersiz tasarım");
  try{
   const existing=await this.initial(product);
   if(request.method==="GET")return json(existing);
   if(request.method!=="POST")return invalid("Desteklenmeyen yöntem",405);
   const payload=await request.json();
   if(payload.product!==product||!Number.isInteger(payload.version)||payload.version<1||payload.version>26)return invalid("Geçersiz kayıt");
   const current=await this.ctx.storage.get("record")||existing;
   if(current.sha!==payload.expectedSha)return invalid("Başka bir oturumda daha yeni değişiklik var",409);
   const next=structuredClone(current.document),at=new Date().toISOString(),v=payload.version;
   if(next.history.length>=MAX_HISTORY)return invalid("Geçmiş sınırına ulaşıldı; arşivleme gerekli",409);
   if(payload.kind==="new"&&next.versions["v"+v])return invalid("Sürüm zaten mevcut",409);
   if(!next.history.length&&v===1){
    next.history.push({id:"baseline-v1",at,version:1,kind:"original",note:"Özgün kaynak",state:{colors:{paper:"#f7f3e9",ink:"#1d2027",red:"#bd2120"},edits:{},groups:{}}});
   }
   const clean=JSON.parse(JSON.stringify(payload.state)),note=String(payload.note||"").slice(0,140);
   next.versions["v"+v]={state:clean,updatedAt:at,note};
   const historyId=crypto.randomUUID();
   next.history.push({id:historyId,at,version:v,kind:payload.kind||"autosave",note,state:clean});
   next.updatedAt=at;
   if(new TextEncoder().encode(JSON.stringify(next)).length>LIMIT)return invalid("Kayıt boyutu sınırı aşıldı",413);
   const revision=crypto.randomUUID();
   // Durable Object storage transaction prevents concurrent writers from clobbering snapshots.
   const result=await this.ctx.storage.transaction(async txn=>{
    const latest=await txn.get("record")||existing;
    if(latest.sha!==payload.expectedSha)return null;
    const item={sha:revision,document:next};
    await txn.put("record",item);
    return item
   });
   if(!result)return invalid("Kayıt çakışması; taslak korunuyor",409);
   return json({...result,historyId});
  }catch(e){
   console.error("Brandstudio DO revision operation failed",String(e?.message||e));
   return invalid("Kayıt hizmeti geçici olarak kullanılamıyor",503)
  }
 }
}
export default {fetch(){return new Response("Not Found",{status:404})}};

// Brandstudio revisions — isolated free-plan SQLite-backed Durable Object.
// This Worker has no public API; Cloudflare Pages calls the object through a binding.
// Atomic compare-and-swap and durable history live in this dedicated object store.
const KEY=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const RECOVERED_BAVUL={"schema":1,"product":"instagram-creative-breakout-bavul-001","versions":{"v2":{"state":{"colors":{"paper":"#f7f3e9","ink":"#1d2027","red":"#bd2120"},"edits":{"0:2":{"styles":{"display":"none"},"mode":"inherit"},"0:1":{"styles":{"width":"623px","height":"29px","max-width":"none","transform":"translate(0px,0px)"},"mode":"inherit","segments":["ASYA'DA EĞİTİM ","/"," EĞİTİMİN YENİ ROTASI"]},"0:15":{"styles":{"display":"none"},"mode":"inherit"},"0:10":{"mode":"inherit","styles":{"width":"441px","height":"52px","max-width":"none","transform":"translate(0px,0px)"},"segments":["ASYA'NIN KAPILARI SANA AÇILSIN ","↗"]}},"groups":{}},"updatedAt":"2026-10-29T13:36:29.778Z","note":"Cloudflare ücretsiz D1 kotası dolduğu için tarayıcıdan korunan v2 değişiklikleri"}},"history":[{"id":"baseline-v1","at":"2026-10-29T10:12:21.071Z","version":1,"kind":"original","note":"Kaynak v1: değiştirilmemiş","state":{"colors":{"paper":"#f7f3e9","ink":"#1d2027","red":"#bd2120"},"edits":{},"groups":{}}},{"id":"import-v2-20261029","at":"2026-10-29T10:12:21.071Z","version":2,"kind":"import","note":"Chrome'da doğrulanmış v2 (sonraki kaydedilmemiş düzenlemeler bu aktarımda yok)","state":{"colors":{"paper":"#f7f3e9","ink":"#1d2027","red":"#bd2120"},"edits":{"0:2":{"styles":{"display":"none"},"mode":"inherit"},"0:1":{"styles":{"width":"623px","height":"29px","max-width":"none","transform":"translate(0px,0px)"},"mode":"inherit","segments":["ASYA'DA EĞİTİM ","/"," EĞİTİMİN YENİ ROTASI"]},"0:15":{"styles":{"display":"none"},"mode":"inherit"}},"groups":{}}},{"id":"emergency-recovery-20261029133229502","at":"2026-10-29T13:36:29.784Z","version":2,"kind":"emergency-recovery","note":"Cloudflare ücretsiz D1 kotası dolduğu için tarayıcıdan korunan v2 değişiklikleri","state":{"colors":{"paper":"#f7f3e9","ink":"#1d2027","red":"#bd2120"},"edits":{"0:2":{"styles":{"display":"none"},"mode":"inherit"},"0:1":{"styles":{"width":"623px","height":"29px","max-width":"none","transform":"translate(0px,0px)"},"mode":"inherit","segments":["ASYA'DA EĞİTİM ","/"," EĞİTİMİN YENİ ROTASI"]},"0:15":{"styles":{"display":"none"},"mode":"inherit"},"0:10":{"mode":"inherit","styles":{"width":"441px","height":"52px","max-width":"none","transform":"translate(0px,0px)"},"segments":["ASYA'NIN KAPILARI SANA AÇILSIN ","↗"]}},"groups":{}},"sourceTimestamp":"2026-10-29T13:32:29.502Z"}],"updatedAt":"2026-10-29T13:36:29.784Z"};
const LIMIT=950000,MAX_HISTORY=240;
const json=(o,status=200)=>new Response(JSON.stringify(o),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
const invalid=(message,status=400)=>json({error:message},status);
function valid(p){return typeof p==="string"&&p.length<=130&&KEY.test(p)}
function compactRetryHistory(history){
 const compacted=[];
 for(const entry of history){
  const previous=compacted[compacted.length-1];
  if(previous&&entry.kind==="autosave"&&previous.kind==="autosave"&&JSON.stringify(entry.state)===JSON.stringify(previous.state)){
   const old=Number(previous.repeatedAutosaves||1);
   compacted[compacted.length-1]={...entry,repeatedAutosaves:old+1,firstRepeatedAt:previous.firstRepeatedAt||previous.at};
  }else compacted.push(entry)
 }
 return compacted
}
export class BrandstudioRevisionObject {
 constructor(ctx,env){this.ctx=ctx;this.env=env}
 async initial(product){
  const stored=await this.ctx.storage.get("record");
  if(stored){
   // Archived all original retry-loop snapshots in GitHub before enabling
   // this lossless-for-design-state compaction of identical automatic retries.
   if(stored.document.history.length>=100){
    const cleaned=compactRetryHistory(stored.document.history);
    if(cleaned.length<stored.document.history.length){
     return await this.ctx.storage.transaction(async txn=>{
      const latest=await txn.get("record");
      if(!latest)return stored;
      const cleanedLatest=compactRetryHistory(latest.document.history);
      if(cleanedLatest.length===latest.document.history.length)return latest;
      const updated={...latest,document:{...latest.document,history:cleanedLatest}};
      await txn.put("record",updated);
      return updated
     })
    }
   }
   return stored
  }
  if(product==="instagram-creative-breakout-bavul-001"){
   const value={sha:"legacy-v2",document:structuredClone(RECOVERED_BAVUL)};
   await this.ctx.storage.put("record",value);
   return value
  }
  // Other products have no migrated browser-cloud history; start a new overlay
  // without introducing runtime dependence on external GitHub or shared D1.
  return {sha:null,document:{schema:1,product,versions:{},history:[]}}
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
   // Repeated identical autosaves must not consume history slots or new writes.
   if(payload.kind!=="new"&&JSON.stringify(current.document.versions?.["v"+payload.version]?.state)===JSON.stringify(payload.state))return json({...current,unchanged:true});
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

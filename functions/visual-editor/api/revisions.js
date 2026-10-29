// Brandstudio private editor API — Cloudflare Pages Functions / D1.
// Only an Access-verified personal Cloudflare session may read or change drafts.
// This is intentionally independent of GitHub PATs, cookies managed by JS, and D1 staging.
const ISSUER='https://dawn-voice-4b40.cloudflareaccess.com';
const OWNER='iakfiratt@gmail.com';
const DB='BRANDSTUDIO_EDITOR';
const KEY=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const enc=new TextEncoder();
let cachedKeys=null,cachedAt=0;
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'no-referrer'}});
function decode(s){const raw=atob(s.replace(/-/g,'+').replace(/_/g,'/').padEnd(Math.ceil(s.length/4)*4,'='));return Uint8Array.from(raw,c=>c.charCodeAt(0))}
function parse(s){return JSON.parse(new TextDecoder().decode(decode(s)))}
async function keys(){
 if(cachedKeys&&Date.now()-cachedAt<600000)return cachedKeys;
 const res=await fetch(ISSUER+'/cdn-cgi/access/certs',{headers:{Accept:'application/json'}});
 if(!res.ok)throw Error('Access certificates unavailable');
 const value=await res.json();
 if(!Array.isArray(value.keys)||!value.keys.length)throw Error('Invalid Access certificates');
 cachedKeys=value.keys;cachedAt=Date.now();return cachedKeys
}
async function authorized(request,env){
 const token=request.headers.get('Cf-Access-Jwt-Assertion')||'';
 if(token.length<100||token.length>15000||!env.BRANDSTUDIO_ACCESS_AUD)return false;
 const parts=token.split('.');if(parts.length!==3)return false;
 const header=parse(parts[0]),payload=parse(parts[1]);
 if(header.alg!=='RS256'||!header.kid)return false;
 const now=Math.floor(Date.now()/1000),aud=Array.isArray(payload.aud)?payload.aud:[payload.aud];
 if(payload.iss!==ISSUER||!aud.includes(env.BRANDSTUDIO_ACCESS_AUD))return false;
 if(!Number.isFinite(payload.exp)||payload.exp<=now||!Number.isFinite(payload.iat)||payload.iat>now+60)return false;
 if(String(payload.email||'').toLowerCase()!==OWNER)return false;
 let list=await keys(),jwk=list.find(x=>x.kid===header.kid);
 if(!jwk){cachedAt=0;list=await keys();jwk=list.find(x=>x.kid===header.kid)}
 if(!jwk)return false;
 const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
 return crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,decode(parts[2]),enc.encode(parts[0]+'.'+parts[1]))
}
async function guard(context){
 if(!context.env?.[DB])return json({error:'Kayıt hizmeti yapılandırılmamış'},503);
 try{if(!await authorized(context.request,context.env))return json({error:'Oturum açılması gerekiyor'},401)}
 catch(_){return json({error:'Oturum şu anda doğrulanamıyor'},503)}
 return null
}
function safeProduct(p){return typeof p==='string'&&p.length<=130&&KEY.test(p)}
function validateState(s){
 if(!s||typeof s!=='object'||Array.isArray(s)||!s.colors||!s.edits||!s.groups)return false;
 if(!['paper','ink','red'].every(k=>/^#[a-f\d]{6}$/i.test(s.colors[k]||'')))return false;
 if(typeof s.edits!=='object'||Array.isArray(s.edits)||Object.keys(s.edits).length>800)return false;
 if(typeof s.groups!=='object'||Array.isArray(s.groups))return false;
 for(const [key,edit] of Object.entries(s.edits)){
  if(!/^\d{1,3}:\d{1,4}$/.test(key)||!edit||typeof edit!=='object')return false;
  if(edit.styles&&(!edit.styles||typeof edit.styles!=='object'||Array.isArray(edit.styles)||Object.keys(edit.styles).length>80))return false;
  if(edit.segments&&(!Array.isArray(edit.segments)||edit.segments.length>40||edit.segments.some(x=>typeof x!=='string'||x.length>1200)))return false;
  if(edit.image!==undefined&&(!/^data:image\/(?:png|jpeg|webp);base64,[a-zA-Z0-9+/=]+$/.test(edit.image)||edit.image.length>650000))return false;
  for(const value of Object.values(edit.styles||{})){if(typeof value!=='string'||value.length>1200||/expression\s*\(|javascript:|@import|url\s*\(/i.test(value))return false}
 }
 return true
}
function snapshot(doc,version,state,note,kind){
 const now=new Date().toISOString();
 if(!doc.versions||!Array.isArray(doc.history))throw Error('Kayıt biçimi geçersiz');
 if(doc.history.length>=240)throw Error('Sürüm geçmişi doldu');
 const key='v'+version;
 if(kind==='new'&&doc.versions[key])throw Error('Bu sürüm zaten mevcut');
 if(!doc.history.length&&version===1){
  doc.history.push({id:'baseline-v1',at:now,version:1,kind:'original',note:'Değiştirilmemiş kaynak',state:{colors:{paper:'#f7f3e9',ink:'#1d2027',red:'#bd2120'},edits:{},groups:{}}});
 }
 doc.versions[key]={state,updatedAt:now,note};
 const id=crypto.randomUUID();
 doc.history.push({id,at:now,version,kind,note,state});
 doc.updatedAt=now;
 if(enc.encode(JSON.stringify(doc)).length>950000)throw Error('Kayıt boyutu sınırı aşıldı');
 return id
}
export async function onRequestGet(context){
 const fail=await guard(context);if(fail)return fail;
 const product=new URL(context.request.url).searchParams.get('product');
 if(!safeProduct(product))return json({error:'Geçersiz tasarım'},400);
 try{
  const row=await context.env[DB].prepare('SELECT body,revision FROM editor_documents WHERE product=?').bind(product).first();
  return json({sha:row?.revision??null,document:row?JSON.parse(row.body):{schema:1,product,versions:{},history:[]}})
 }catch(_){return json({error:'Kayıtlar okunamadı'},503)}
}
export async function onRequestPost(context){
 const fail=await guard(context);if(fail)return fail;
 const req=context.request,url=new URL(req.url);
 if(req.headers.get('Origin')!==url.origin||req.headers.get('X-Brandstudio-Editor')!=='1'||!req.headers.get('Content-Type')?.startsWith('application/json'))return json({error:'Güvenli istek doğrulanamadı'},403);
 const raw=await req.text();if(enc.encode(raw).length>900000)return json({error:'Kayıt çok büyük'},413);
 let input;
 try{input=JSON.parse(raw)}catch(_){return json({error:'Geçersiz veri'},400)}
 const {product,version,state,expectedSha}=input;
 if(!safeProduct(product)||!Number.isInteger(version)||version<1||version>26||!validateState(state)||!Object.prototype.hasOwnProperty.call(input,'expectedSha')||!(typeof expectedSha==='string'||expectedSha===null))return json({error:'Geçersiz kayıt'},400);
 const note=String(input.note||'').slice(0,140),kind=['autosave','save','new','restore'].includes(input.kind)?input.kind:'autosave';
 try{
  const db=context.env[DB];
  const row=await db.prepare('SELECT body,revision FROM editor_documents WHERE product=?').bind(product).first();
  if((row?.revision??null)!==expectedSha)return json({error:'Başka bir oturumda daha yeni düzenleme var'},409);
  const document=row?JSON.parse(row.body):{schema:1,product,versions:{},history:[]};
  const clean=JSON.parse(JSON.stringify(state));let historyId;
  try{historyId=snapshot(document,version,clean,note,kind)}catch(e){return json({error:e.message},409)}
  const next=crypto.randomUUID(),body=JSON.stringify(document),now=new Date().toISOString();
  const saved=row?await db.prepare('UPDATE editor_documents SET body=?,revision=?,updated_at=? WHERE product=? AND revision=? RETURNING revision').bind(body,next,now,product,expectedSha).first():await db.prepare('INSERT INTO editor_documents(product,body,revision,updated_at) VALUES(?,?,?,?) ON CONFLICT DO NOTHING RETURNING revision').bind(product,body,next,now).first();
  if(!saved)return json({error:'Kayıt çakışması; değişiklikler korunuyor'},409);
  return json({sha:next,historyId,document});
 }catch(_){return json({error:'Kayıt hizmetine erişilemiyor'},503)}
}

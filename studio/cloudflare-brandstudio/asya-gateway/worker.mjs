// Brandstudio Asyada Egitim Cloudflare gateway. Authenticated cloud revisions + public static CDN.
const ISSUER='https://polished-flower-7330.cloudflareaccess.com';
const OWNERS=new Set(['info@asyadaegitim.com','iakfiratt@gmail.com']);
const ACCESS_AUD='b5683875c2c6ed863458f18daca51546236eab3a61d41b6c4a453a001f3eb074';
const STORE='BRANDSTUDIO_OBJECTS';
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
 if(token.length<100||token.length>15000||!ACCESS_AUD)return false;
 const parts=token.split('.');if(parts.length!==3)return false;
 const header=parse(parts[0]),payload=parse(parts[1]);
 if(header.alg!=='RS256'||!header.kid)return false;
 const now=Math.floor(Date.now()/1000),aud=Array.isArray(payload.aud)?payload.aud:[payload.aud];
 if(payload.iss!==ISSUER||!aud.includes(ACCESS_AUD))return false;
 if(!Number.isFinite(payload.exp)||payload.exp<=now||!Number.isFinite(payload.iat)||payload.iat>now+60)return false;
 if(!OWNERS.has(String(payload.email||'').toLowerCase()))return false;
 let list=await keys(),jwk=list.find(x=>x.kid===header.kid);
 if(!jwk){cachedAt=0;list=await keys();jwk=list.find(x=>x.kid===header.kid)}
 if(!jwk)return false;
 const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
 return crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,decode(parts[2]),enc.encode(parts[0]+'.'+parts[1]))
}
async function guard(context){
 if(!context.env?.[STORE])return json({error:'Kayıt hizmeti yapılandırılmamış'},503);
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
function objectFor(context,product){
 const binding=context.env[STORE];
 return binding.get(binding.idFromName(product))
}
export async function onRequestGet(context){
 const fail=await guard(context);if(fail)return fail;
 const product=new URL(context.request.url).searchParams.get('product');
 if(!safeProduct(product))return json({error:'Geçersiz tasarım'},400);
 try{return await objectFor(context,product).fetch('https://brandstudio.internal/revisions?product='+encodeURIComponent(product))}
 catch(e){console.error('Editor store read failed',String(e?.message||e));return json({error:'Kayıtlar okunamadı'},503)}
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
 const body=JSON.stringify({product,version,state,expectedSha,note:String(input.note||'').slice(0,140),kind:['autosave','save','new','restore'].includes(input.kind)?input.kind:'autosave'});
 try{
  return await objectFor(context,product).fetch(new Request('https://brandstudio.internal/revisions?product='+encodeURIComponent(product),{method:'POST',headers:{'content-type':'application/json'},body}))
 }catch(e){console.error('Editor store write failed',String(e?.message||e));return json({error:'Kayıt hizmetine erişilemiyor'},503)}
}

const STATIC_ORIGIN='https://cinegitim.github.io/design';
export default {
 async fetch(request,env,ctx){
  const url=new URL(request.url);
  if(url.pathname==='/visual-editor/api/revisions'){
   const context={request,env};
   if(request.method==='GET')return onRequestGet(context);
   if(request.method==='POST')return onRequestPost(context);
   return json({error:'Desteklenmeyen yöntem'},405)
  }
  if(request.method!=='GET'&&request.method!=='HEAD')return new Response('Method Not Allowed',{status:405});
  const upstreamUrl=new URL(STATIC_ORIGIN+url.pathname+url.search);
  try {
   const res=await fetch(upstreamUrl.toString(),{
    method:request.method,
    redirect:'follow',
    headers:{Accept:request.headers.get('Accept')||'*/*'},
    cf:{cacheEverything:true,cacheTtl:120}
   });
   const headers=new Headers(res.headers);
   headers.delete('set-cookie');
   headers.delete('access-control-allow-origin');
   headers.set('X-Content-Type-Options','nosniff');
   headers.set('Referrer-Policy','strict-origin-when-cross-origin');
   if(url.pathname.startsWith('/visual-editor/'))headers.set('Cache-Control','no-store');
   return new Response(res.body,{status:res.status,headers})
  } catch(e) {
   console.error('Brandstudio static CDN fetch failed',String(e?.message||e));
   return new Response('Tasarım kaynaklarına geçici olarak ulaşılamıyor',{status:503,headers:{'cache-control':'no-store'}})
  }
 }
};

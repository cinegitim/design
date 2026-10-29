// Branddesign admin gateway — Asyada Egitim. Username/password + trusted browser sessions.
// No password, derived verifier or token is committed to GitHub.
const STORE='BRANDSTUDIO_OBJECTS', AUTH='BRANDSTUDIO_AUTH';
const KEY=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const enc=new TextEncoder(),COOKIE='__Host-branddesign_session';
const YEAR=31536000;
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'no-referrer'}});
const hex=bytes=>Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
function fromHex(s){if(typeof s!=='string'||s.length%2||!/^[a-f0-9]+$/i.test(s))throw Error('hex');return Uint8Array.from(s.match(/.{2}/g),x=>parseInt(x,16))}
async function sha256(x){return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(x))))}
function sessionToken(req){
 const cookie=req.headers.get('Cookie')||'';
 const match=cookie.match(/(?:^|;\s*)__Host-branddesign_session=([a-f0-9]{64})(?:;|$)/);
 return match?.[1]||null
}
async function authObject(env,action,id,extra={}){
 if(!env[AUTH])throw Error('Auth object binding missing');
 const ns=env[AUTH],obj=ns.get(ns.idFromName('branddesign-admin'));
 const r=await obj.fetch('https://branddesign.internal/session',{
  method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({action,id,...extra})
 });
 if(!r.ok)throw Error('Auth backend unavailable');
 return r.json()
}
async function session(req,env){
 const token=sessionToken(req);if(!token)return {ok:false};
 const id=await sha256(token);
 const result=await authObject(env,'check',id);
 return result.ok?{ok:true,token,renewed:!!result.renewed}:{ok:false}
}
function cookieHeader(token,maxAge=YEAR){
 return COOKIE+'='+token+'; Path=/; Max-Age='+maxAge+'; HttpOnly; Secure; SameSite=Lax'
}
function sameOrigin(req){
 const url=new URL(req.url);
 return req.headers.get('Origin')===url.origin;
}
function redirect(url,header){
 const headers={'Location':url,'Cache-Control':'no-store'};
 if(header)headers['Set-Cookie']=header;
 return new Response(null,{status:303,headers})
}
function target(value){
 const s=String(value||'');
 if(s.length>0&&s.length<350&&s.startsWith('/')&&!s.startsWith('//')&&!s.includes('\\')&&!/[\x00-\x1F\x7F]/.test(s))return s;
 return '/visual-editor/browser/'
}
// Password stretching happens in the browser to respect Workers Free 10ms CPU limit.
// A short-lived, one-use challenge prevents replay of a captured proof.
const LOGIN_SCRIPT=String.raw`(function(){
 const form=document.querySelector('form[action="/admin/login"]');
 const button=form.querySelector('button[type=submit]');
 const toBytes=s=>Uint8Array.from(s.match(/.{2}/g),x=>parseInt(x,16));
 const toHex=b=>Array.from(new Uint8Array(b),v=>v.toString(16).padStart(2,'0')).join('');
 const encoder=new TextEncoder();
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(button.disabled)return;
  const username=form.elements.namedItem('username').value;
  const password=form.elements.namedItem('password').value;
  button.disabled=true;button.textContent='Güvenli giriş doğrulanıyor…';
  try{
   const req=await fetch('/admin/challenge',{credentials:'same-origin',cache:'no-store'});
   if(!req.ok)throw Error('Çok fazla deneme veya geçici bağlantı sorunu');
   const c=await req.json();
   if(!/^[a-f0-9]{64}$/.test(c.challenge)||!/^[a-f0-9]+$/.test(c.salt))throw Error('Geçersiz doğrulama');
   const material=await crypto.subtle.importKey('raw',encoder.encode(password),'PBKDF2',false,['deriveBits']);
   const bits=await crypto.subtle.deriveBits({name:'PBKDF2',salt:toBytes(c.salt),iterations:c.iterations,hash:'SHA-256'},material,256);
   const hmac=await crypto.subtle.importKey('raw',bits,{name:'HMAC',hash:'SHA-256'},false,['sign']);
   const message=['branddesign-admin-login:v1',c.challenge,username,location.host].join('\n');
   const proof=toHex(await crypto.subtle.sign('HMAC',hmac,encoder.encode(message)));
   form.elements.namedItem('password').removeAttribute('name');
   for(const [name,value] of [['challenge',c.challenge],['proof',proof]]){
    const input=document.createElement('input');input.type='hidden';input.name=name;input.value=value;form.append(input)
   }
   form.submit()
  }catch(e){
   button.disabled=false;button.textContent='Admin paneline gir';
   document.getElementById('message').textContent='Giriş hazırlanamadı. Lütfen tekrar dene.'
  }
 })
})();`;
function loginHtml(next,error,nonce){
 const safe=next.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
 return `<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Branddesign · Admin Girişi</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 20% 10%,#27334b 0,#111927 50%,#0c111b 100%);color:#edf2f8;font:15px/1.5 system-ui,Arial;display:grid;place-items:center;padding:25px}main{width:min(100%,435px);background:#182334;border:1px solid #34415a;box-shadow:0 22px 65px #0007;border-radius:18px;padding:34px}h1{font-size:27px;letter-spacing:-.8px;margin:4px 0 6px}p{color:#abb8cc;margin:0 0 24px}.brand{color:#f6a67e;font-size:12px;letter-spacing:.15em;font-weight:800}label{display:block;margin:16px 0 6px;color:#d5e0ef;font-weight:600;font-size:13px}input{width:100%;border:1px solid #45556d;border-radius:9px;padding:13px;background:#0e1725;color:#fff;font:inherit}input:focus{outline:2px solid #f5a47b;outline-offset:2px}button{margin:25px 0 10px;background:#bd2120;border:0;border-radius:10px;padding:14px;color:white;font:inherit;font-weight:750;width:100%;cursor:pointer}button:disabled{opacity:.65}small{color:#9faec2}aside{color:#ffbeb5;margin-top:12px;font-size:13px}</style></head><body><main><div class="brand">BRANDDESIGN / ADMIN</div><h1>Tekrar hoş geldin.</h1><p>Bu tarayıcıda bir kez giriş yap. Güvenli oturumun sonraki ziyaretlerinde otomatik hatırlanır.</p><form method="post" action="/admin/login"><input type="hidden" name="next" value="${safe}"><label for="username">Kullanıcı adı</label><input id="username" name="username" required autocomplete="username" maxlength="64"><label for="password">Şifre</label><input id="password" name="password" type="password" required autocomplete="current-password"><button type="submit">Admin paneline gir</button></form><aside id="message">${error?'Giriş bilgileri doğrulanamadı veya çok fazla deneme yapıldı.':''}</aside><small>Güvenilen tarayıcı oturumu · 365 günlük yenilenen oturum · Çıkış yaparak sonlandırılabilir</small></main><script nonce="${nonce}">${LOGIN_SCRIPT}</script></body></html>`
}
function loginPage(next,error,status=200){
 const nonce=hex(crypto.getRandomValues(new Uint8Array(16)));
 const html=loginHtml(next,error,nonce);
 return new Response(html,{status,headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store','content-security-policy':"default-src 'none'; script-src 'nonce-"+nonce+"'; connect-src 'self'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",'x-frame-options':'DENY','x-content-type-options':'nosniff'}})
}
async function correctProof(username,challenge,proof,env,host){
 if(!env.ADMIN_PBKDF2_SALT||!env.ADMIN_PBKDF2_HASH)throw Error('Admin password secret missing');
 if(username!=='adminasya'||!/^[a-f0-9]{64}$/.test(challenge)||!/^[a-f0-9]{64}$/.test(proof))return false;
 const key=await crypto.subtle.importKey('raw',fromHex(env.ADMIN_PBKDF2_HASH),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const msg=['branddesign-admin-login:v1',challenge,username,host].join('\n');
 const expected=new Uint8Array(await crypto.subtle.sign('HMAC',key,enc.encode(msg)));
 const actual=fromHex(proof);let diff=0;
 for(let i=0;i<expected.length;i++)diff|=actual[i]^expected[i];
 return diff===0
}
async function handleAdmin(req,env,url){
 if(url.pathname==='/admin/logout'){
  if(req.method!=='POST'||!sameOrigin(req))return json({error:'Güvenli istek gerekli'},403);
  const token=sessionToken(req);
  if(token)await authObject(env,'revoke',await sha256(token));
  return redirect('/admin/login',cookieHeader('',0))
 }
 if(url.pathname==='/admin/session'){
  if(req.method!=='GET')return json({error:'method'},405);
  const status=await session(req,env);
  return json({authenticated:status.ok,session:'trusted-device',expiresAfterDays:365})
 }
 if(url.pathname==='/admin/challenge'){
  if(req.method!=='GET')return json({error:'method'},405);
  if(!env.ADMIN_PBKDF2_SALT||!env.ADMIN_PBKDF2_HASH)return json({error:'Giriş yapılandırılmamış'},503);
  const clientId=await sha256(req.headers.get('CF-Connecting-IP')||'unknown');
  const check=await authObject(env,'attempt',clientId,{op:'probe'});
  if(!check.ok)return json({error:'Çok fazla giriş denemesi'},429);
  const challenge=await authObject(env,'challenge',clientId);
  return json({challenge:challenge.challenge,salt:env.ADMIN_PBKDF2_SALT,iterations:210000})
 }
 if(url.pathname!=='/admin/login'&&url.pathname!=='/admin'&&url.pathname!=='/admin/')return json({error:'Yol bulunamadı'},404);
 if(req.method==='GET'){
  if((await session(req,env)).ok)return redirect(target(url.searchParams.get('next')));
  return loginPage(target(url.searchParams.get('next')),false)
 }
 if(req.method!=='POST'||!sameOrigin(req)||!req.headers.get('content-type')?.startsWith('application/x-www-form-urlencoded'))return json({error:'Güvenli istek gerekli'},403);
 const body=await req.text();
 if(body.length>1600)return json({error:'Çok büyük istek'},413);
 const data=new URLSearchParams(body);
 const username=String(data.get('username')||'').slice(0,64);
 const proof=String(data.get('proof')||'').slice(0,128),challenge=String(data.get('challenge')||'').slice(0,128);
 const clientId=await sha256(req.headers.get('CF-Connecting-IP')||'unknown');
 const ratelimit=await authObject(env,'attempt',clientId,{op:'probe'});
 if(!ratelimit.ok)return loginPage(target(data.get('next')),true,429);
 const consumed=await authObject(env,'consume',clientId,{challenge});
 const valid=consumed.ok&&await correctProof(username,challenge,proof,env,url.host);
 if(!valid){await authObject(env,'attempt',clientId,{op:'failed'});return loginPage(target(data.get('next')),true,401)}
 await authObject(env,'attempt',clientId,{op:'success'});
 const secret=hex(crypto.getRandomValues(new Uint8Array(32)));
 await authObject(env,'issue',await sha256(secret));
 return redirect(target(data.get('next')),cookieHeader(secret))
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
 if(!context.authenticated)return json({error:'Admin girişi gerekiyor'},401);
 if(!context.env?.[STORE])return json({error:'Kayıt hizmeti yapılandırılmamış'},503);
 const product=new URL(context.request.url).searchParams.get('product');
 if(!safeProduct(product))return json({error:'Geçersiz tasarım'},400);
 try{return await objectFor(context,product).fetch('https://brandstudio.internal/revisions?product='+encodeURIComponent(product))}
 catch(e){console.error('Editor store read failed',String(e?.message||e));return json({error:'Kayıtlar okunamadı'},503)}
}
export async function onRequestPost(context){
 if(!context.authenticated)return json({error:'Admin girişi gerekiyor'},401);
 if(!context.env?.[STORE])return json({error:'Kayıt hizmeti yapılandırılmamış'},503);
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
  try{
   if(url.pathname==='/favicon.ico')return new Response(null,{status:204});
   if(url.pathname.startsWith('/admin'))return handleAdmin(request,env,url);
   if(request.method!=='GET'&&request.method!=='HEAD'&&!(url.pathname==='/visual-editor/api/revisions'&&request.method==='POST'))return new Response('Method Not Allowed',{status:405});
   const user=await session(request,env);
   if(!user.ok){
    if(url.pathname==='/visual-editor/api/revisions')return json({error:'Admin girişi gerekli'},401);
    const next=target(url.pathname+url.search);
    return redirect('/admin/login?next='+encodeURIComponent(next))
   }
   if(url.pathname==='/visual-editor/api/revisions'){
    const context={request,env,authenticated:true};
    if(request.method==='GET')return onRequestGet(context);
    if(request.method==='POST')return onRequestPost(context);
    return json({error:'Desteklenmeyen yöntem'},405)
   }
   const upstreamUrl=new URL(STATIC_ORIGIN+url.pathname+url.search);
   const res=await fetch(upstreamUrl.toString(),{method:request.method,redirect:'follow',headers:{Accept:request.headers.get('Accept')||'*/*'},cf:{cacheEverything:true,cacheTtl:120}});
   const headers=new Headers(res.headers);
   headers.delete('set-cookie');headers.delete('access-control-allow-origin');
   headers.set('X-Content-Type-Options','nosniff');
   headers.set('Referrer-Policy','strict-origin-when-cross-origin');
   if(url.pathname.startsWith('/visual-editor/'))headers.set('Cache-Control','no-store');
   if(user.renewed)headers.append('Set-Cookie',cookieHeader(user.token));
   return new Response(res.body,{status:res.status,headers});
  }catch(e){
   console.error('Branddesign gateway unavailable',String(e?.message||e));
   return json({error:'Hizmet geçici olarak kullanılamıyor'},503)
  }
 }
};

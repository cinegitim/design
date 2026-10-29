/* Brandstudio GitHub-backed revisions, MIT-compatible browser JS (no external auth SDK).
   The public branch contains non-sensitive design states; writing requires explicit
   owner-approved, repository-scoped GitHub token, held only in JS memory. */
(function(root) {
"use strict";
const REPO="cinegitim/design";
const BRANCH="brandstudio-editor-history";
const API="https://api.github.com/repos/"+REPO;
const PREFIX="docs/visual-editor/browser/cloud/";
const KEY_RE=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const MAX_HISTORY=240;
const MAX_DOC_BYTES=950000;
let accessToken="";
function setToken(v) {accessToken=String(v||"").trim();return !!accessToken}
function authenticated(){return !!accessToken}
function apiHeaders(useAuth){
 const h={Accept:"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"};
 if(useAuth && accessToken)h.Authorization="Bearer "+accessToken;
 return h
}
async function request(path,opts={}) {
 const headers={...apiHeaders(!!opts.auth),...(opts.body!==undefined?{"content-type":"application/json"}:{})};
 let result;
 try{result=await fetch(API+path,{method:opts.method||"GET",headers,body:opts.body===undefined?undefined:JSON.stringify(opts.body),cache:"no-store",credentials:"omit",redirect:"error"})}
 catch(e){throw Error("GitHub bağlantısı kurulamadı: "+e.message)}
 const data=await result.json().catch(()=>({}));
 if(!result.ok && !(opts.allow404&&result.status===404)){
   if(result.status===401)throw Error("GitHub yetkilendirmesi geçersiz. Token'ı kontrol edin.");
   if(result.status===403)throw Error("GitHub erişimi reddetti; token kapsamını ve hesabın repository izinlerini denetleyin.");
   if([409,412,422].includes(result.status))throw Error("GitHub üzerinde eşzamanlı değişiklik var; kayıt yapılmadı. Önce buluttaki son hali yeniden okuyun.");
   throw Error("GitHub HTTP "+result.status+": "+String(data.message||"İşlem başarısız").slice(0,160));
 }
 return result.status===404?null:data
}
function utf8base64(s){
 const bytes=new TextEncoder().encode(s);let out="";
 for(let i=0;i<bytes.length;i+=8192)out+=String.fromCharCode(...bytes.slice(i,i+8192));
 return btoa(out)
}
function from64(s){
 const raw=atob(String(s).replace(/\s+/g,""));let b=Uint8Array.from(raw,c=>c.charCodeAt(0));
 return new TextDecoder("utf-8",{fatal:true}).decode(b)
}
function pathFor(product){if(!KEY_RE.test(product))throw Error("Geçersiz ürün kimliği");return PREFIX+product+".json"}
async function load(product,auth=false) {
 const path=pathFor(product),enc=path.split("/").map(encodeURIComponent).join("/");
 const item=await request("/contents/"+enc+"?ref="+encodeURIComponent(BRANCH),{auth,allow404:true});
 if(!item)return{sha:null,document:{schema:1,product,versions:{},history:[]}};
 if(item.type!=="file"||typeof item.content!=="string")throw Error("Geçersiz bulut dosyası");
 const content=JSON.parse(from64(item.content));
 if(content.schema!==1||content.product!==product||!content.versions||!Array.isArray(content.history))throw Error("Bulut kayıt biçimi geçersiz");
 return{sha:item.sha,document:content}
}
async function ensureBranch(){
 if(!authenticated())throw Error("Buluta yazmak için GitHub erişim anahtarını bu oturumda girin");
 const target=await request("/git/ref/heads/"+BRANCH,{auth:true,allow404:true});
 if(target)return;
 const main=await request("/git/ref/heads/main",{auth:true});
 try{await request("/git/refs",{auth:true,method:"POST",body:{ref:"refs/heads/"+BRANCH,sha:main.object.sha}})}
 catch(e){if(!/eşzamanlı/.test(e.message))throw e}
}
function cleanState(s) {return JSON.parse(JSON.stringify(s))}
async function commit({product,version,state,note="",kind="save"}) {
 if(!authenticated())throw Error("GitHub erişim anahtarı gerekli");
 if(!Number.isInteger(version)||version<1||version>26)throw Error("Sürüm 1–26 aralığında olmalı");
 await ensureBranch();
 const {sha,document:prev}=await load(product,true);
 const doc=structuredClone(prev),now=new Date().toISOString();
 const history=doc.history;
 if(!history.length&&version===1){
  // Distinguish original untouched file from the first editable v1 overlay.
  const original={colors:{paper:"#f7f3e9",ink:"#1d2027",red:"#bd2120"},edits:{},groups:{}};
  history.push({id:"baseline-v1",at:now,version:1,kind:"original",note:"Değiştirilmemiş kaynak v1",state:original});
 }
 if(history.length>=MAX_HISTORY)throw Error("Bulut geçmişi sınırına ulaşıldı. GitHub commit geçmişi korunuyor; yeni kayıttan önce arşiv oluşturun.");
 const saved=cleanState(state),cleanNote=String(note).slice(0,160);
 doc.versions["v"+version]={state:saved,updatedAt:now,note:cleanNote};
 const id=now+"-"+Math.random().toString(36).slice(2,8);
 history.push({id,at:now,version,kind,note:cleanNote,state:saved});
 doc.updatedAt=now;
 const json=JSON.stringify(doc,null,2)+"\n";
 if(new TextEncoder().encode(json).length>MAX_DOC_BYTES)throw Error("GitHub geçmiş dosyası boyut sınırına ulaştı; önce arşiv alın.");
 const filename=pathFor(product);
 const body={message:"brandstudio(editor): "+product+" v"+version+" "+kind+" "+now,content:utf8base64(json),branch:BRANCH};
 if(sha)body.sha=sha;
 const result=await request("/contents/"+filename.split("/").map(encodeURIComponent).join("/"),{method:"PUT",body,auth:true});
 return{sha:result.content?.sha||null,commit:result.commit?.sha||null,historyId:id,document:doc};
}
root.BrandstudioCloud={branch:BRANCH,setToken,authenticated,load,commit,MAX_HISTORY};
})(globalThis);

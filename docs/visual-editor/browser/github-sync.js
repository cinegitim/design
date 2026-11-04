/* Brandstudio cloud revisions client — one private Cloudflare editor.
   Cloudflare Access controls entry; the separate Brandstudio admin session authorizes cloud revisions;
   the application never asks for or stores GitHub access tokens. */
(function(root){
"use strict";
const API="/visual-editor/api/revisions";
const RE=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
async function request(method,product,body){
 if(!RE.test(product))throw Error("Geçersiz tasarım");
 const url=API+"?product="+encodeURIComponent(product);
 let response;
 try{response=await fetch(url,{method,credentials:"same-origin",cache:"no-store",redirect:"follow",
  headers:method==="POST"?{"content-type":"application/json","X-Brandstudio-Editor":"1"}:{"Accept":"application/json"},
  body:body?JSON.stringify(body):undefined})}
 catch(e){throw Error("Bulut bağlantısı kurulamadı: "+e.message)}
 const contentType=response.headers.get("content-type")||"";
 if(!contentType.includes("application/json"))throw Error("Oturum süresi dolmuş olabilir. Editörü yeniden açıp giriş yapın.");
 const data=await response.json();
 if(!response.ok)throw Error(response.status===409?"Sürüm başka bir yerde değişmiş. Önce güncel kaydı açın.":data.error||"Bulut bağlantısında hata oluştu");
 return data
}
async function load(product){return request("GET",product)}
async function commit({product,version,state,note="",kind="autosave",expectedSha}){
 if(!Number.isInteger(version)||version<1||version>26)throw Error("Sürüm numarası geçersiz");
 return request("POST",product,{product,version,state,note,kind,expectedSha})
}
async function openReviewPr({product,version,expectedSha}){
 if(!RE.test(product)||!Number.isInteger(version)||version<1||version>26||
    !/^[a-f0-9-]{36}$/i.test(expectedSha||''))throw Error("Kaydedilmiş geçerli sürüm gerekli");
 let response;
 try{
  response=await fetch("/visual-editor/api/github-pr",{
   method:"POST",credentials:"same-origin",cache:"no-store",redirect:"follow",
   headers:{"content-type":"application/json","X-Brandstudio-Editor":"1"},
   body:JSON.stringify({product,version,expectedSha,acknowledgePublicRepository:true})
  })
 }catch(e){throw Error("GitHub bağlantısı kurulamadı: "+e.message)}
 if(!(response.headers.get("content-type")||"").includes("application/json"))
  throw Error("Admin oturumu gerekli. Editörü yeniden açın.");
 const data=await response.json();
 if(!response.ok)throw Error(data.error||"GitHub inceleme PR'ı oluşturulamadı");
 if(!/^https:\/\/github\.com\/cinegitim\/design\/pull\/[1-9]\d*$/.test(data.url||""))
  throw Error("GitHub PR yanıtı doğrulanamadı");
 return data
}

async function reviewPrAvailable(){
 try{
  const response=await fetch("/visual-editor/api/github-pr",{
   method:"GET",credentials:"same-origin",cache:"no-store",redirect:"follow",
   headers:{"Accept":"application/json"}
  });
  if(!response.ok||!(response.headers.get("content-type")||"").includes("application/json"))return false;
  const data=await response.json();
  return data.enabled===true&&data.repo==="cinegitim/design"&&data.mode==="draft-review-only"
 }catch(_){return false}
}

async function finalizeAvailable(){
 try{
  const r=await fetch('/visual-editor/api/finalize',{method:'GET',credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});
  if(!r.ok||!(r.headers.get('content-type')||'').includes('application/json'))return false;
  const data=await r.json();
  return data.enabled===true&&data.repo==='cinegitim/design'&&data.mode==='product-bulk-draft-review'
 }catch(_){return false}
}
async function finalizeProduct({product,expectedSha,selectedVersion,sourcePages,files}){
 if(!RE.test(product)||!/^[0-9a-f-]{36}$/i.test(expectedSha||'')||!Number.isInteger(selectedVersion)||
    !Array.isArray(sourcePages)||!Array.isArray(files))throw Error('Geçersiz tamamlanmış ürün paketi');
 let r;
 try{r=await fetch('/visual-editor/api/finalize',{method:'POST',credentials:'same-origin',cache:'no-store',
  headers:{'content-type':'application/json','X-Brandstudio-Editor':'1'},
  body:JSON.stringify({product,expectedSha,selectedVersion,sourcePages,files,acknowledgePublicRepository:true})})}
 catch(e){throw Error('GitHub toplu aktarımına bağlanılamadı: '+e.message)}
 if(!(r.headers.get('content-type')||'').includes('application/json'))throw Error('Admin oturumu gerekli');
 const data=await r.json();
 if(!r.ok)throw Error(data.error||'Toplu aktarım başarısız');
 if(!/^https:\/\/github\.com\/cinegitim\/design\/pull\/[1-9]\d*$/.test(data.url||''))throw Error('GitHub PR adresi geçersiz');
 return data
}

root.BrandstudioCloud={
 load,commit,openReviewPr,reviewPrAvailable,finalizeAvailable,finalizeProduct,
 authenticated:()=>true,
 setToken:()=>true,
 MAX_HISTORY:240
}
})(globalThis);

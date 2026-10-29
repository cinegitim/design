/* Brandstudio cloud revisions client — one private Cloudflare editor.
   Cloudflare Access authenticates the browser with a normal long-lived session;
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
root.BrandstudioCloud={
 load,commit,
 authenticated:()=>true,
 setToken:()=>true,
 MAX_HISTORY:240
}
})(globalThis);

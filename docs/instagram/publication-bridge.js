/* Read-only multi-channel publication proof overlay. No platform keys in browser. */
(function(root){
"use strict";
const ENDPOINT="https://brandstudio-publications.lucky-truth-c0b3.workers.dev/api/proofs";
function platformOf(p){return p.platform||"instagram"}
function validProof(p,groups){
 if(!p||p.match_status!=="family_verified"||p.product_id!=null||
    !p.group_id||!groups.some(g=>g.id===p.group_id)||!p.published_at)return false;
 if(typeof p.permalink!=="string")return false;
 try{
  const u=new URL(p.permalink),h=u.hostname.toLowerCase().replace(/^www\./,""),path=u.pathname;
  if(u.protocol!=="https:"||u.username||u.password||u.hash||u.search)return false;
  switch(p.platform){
   case "instagram":return h==="instagram.com"&&/^\/(p|reel|tv)\/[A-Za-z0-9_-]+\/?$/.test(path);
   case "facebook":return (h==="facebook.com"||h==="m.facebook.com")&&
     (/\/posts\//.test(path)||/\/permalink\//.test(path));
   case "linkedin":return h==="linkedin.com"&&/^\/feed\/update\/urn:li:(?:share|ugcPost):\d+\/?$/.test(path);
   case "x":return (h==="x.com"||h==="twitter.com")&&/^\/[^/]+\/status\/\d+\/?$/.test(path);
   default:return false;
  }
 }catch(_){return false}
}
async function get(registry){
 const groups=Array.isArray(registry?.groups)?registry.groups:[];
 if(!groups.length)return [];
 try{
  const r=await fetch(ENDPOINT,{cache:"no-store",signal:AbortSignal.timeout(4500)});
  if(!r.ok)return [];
  const data=await r.json();
  if(!Array.isArray(data.posts))return [];
  return data.posts.filter(p=>validProof(p,groups)).slice(0,150).map(p=>({
   platform:p.platform,groupId:p.group_id,productId:null,url:p.permalink,publishedAt:p.published_at,
   verified:true,source:p.platform==="instagram"?"Official Meta API":"Voholabs verified published post",
   matching:"family-level publication; exact design version not established"
  }));
 }catch(_){return []}
}
async function merged(registry){
 const prior=(registry?.socialPublication?.posts||[]).map(p=>Object.assign({platform:"instagram"},p));
 const additional=await get(registry);
 function key(p){
  const platform=platformOf(p),url=String(p.url||"");
  if(platform==="instagram"){
   const found=url.match(/\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
   if(found)return platform+":"+found[1];
  }
  return platform+":"+url.replace(/\/$/,"");
 }
 const seen=new Set(prior.map(key));
 return prior.concat(additional.filter(p=>{
  const keyValue=key(p);
  if(seen.has(keyValue))return false;seen.add(keyValue);return true;
 }));
}
root.BrandstudioPublicationBridge={get,merged,validProof,platformOf};
})(typeof window!=="undefined"?window:globalThis);

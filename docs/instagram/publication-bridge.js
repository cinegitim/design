/* Brandstudio: read-only, Chrome-free Instagram publication proof overlay.
   The official API and Cloudflare D1 remain separate from canonical GitHub decisions.
   No token is sent to the browser, and candidate matches never mark a product published. */
(function(root){
"use strict";
const ENDPOINT="https://brandstudio-publications.lucky-truth-c0b3.workers.dev/api/proofs";
function validProof(p,groups){
 if(!p||p.platform!=="instagram"||p.match_status!=="family_verified"||p.product_id!=null||
    !p.group_id||!groups.some(g=>g.id===p.group_id)||!p.published_at)return false;
 if(typeof p.permalink!=="string")return false;
 try{
  const u=new URL(p.permalink);
  return u.protocol==="https:"&&["instagram.com","www.instagram.com"].includes(u.hostname)&&
   /^\/(p|reel|tv)\/[A-Za-z0-9_-]+\/?$/.test(u.pathname)&&!u.username&&!u.password&&!u.search&&!u.hash;
 }catch(_){return false}
}
async function get(registry){
 const groups=registry&&Array.isArray(registry.groups)?registry.groups:[];
 if(!groups.length)return [];
 try{
  const r=await fetch(ENDPOINT,{cache:"no-store",signal:AbortSignal.timeout(4500)});
  if(!r.ok)return [];
  const data=await r.json();
  if(!Array.isArray(data.posts))return [];
  return data.posts.filter(p=>validProof(p,groups)).slice(0,100).map(p=>({
   groupId:p.group_id,productId:null,url:p.permalink,publishedAt:p.published_at,verified:true,
   source:"Official Meta API via Cloudflare D1; unique caption anchor",
   matching:"verified publication at design-family level; revision not established"
  }));
 }catch(_){return []}
}
async function merged(registry){
 const existing=registry?.socialPublication?.posts||[];
 const additional=await get(registry);
 const keys=new Set(existing.map(p=>(p.url||"").match(/\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/)?.[1]).filter(Boolean));
 return existing.concat(additional.filter(p=>{
  const id=p.url.match(/\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/)?.[1];
  if(!id||keys.has(id))return false;
  keys.add(id);return true;
 }));
}
root.BrandstudioPublicationBridge={get,merged,validProof};
})(typeof window!=="undefined"?window:globalThis);

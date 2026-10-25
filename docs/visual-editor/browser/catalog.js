/* Public, browser-only Brandstudio design discovery. No account tokens, writes or paid API. */
(function(root){
"use strict";
var IMAGE=/\.(png|jpe?g|webp|svg)$/i,HTML=/\.html$/i;
function validPath(p){return typeof p==='string'&&p.startsWith('docs/')&&!p.split('/').some(function(x){return x==='..'||x===''||x.startsWith('.')})}
function slug(p){return p.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,125)}
function label(s){return s.replace(/[-_]+/g,' ').replace(/\b\w/g,function(c){return c.toUpperCase()})}
function fromPaths(paths){
 var groups=new Map(),raster=new Map(),single=[];
 Array.from(new Set(paths)).sort().forEach(function(p){
  if(!validPath(p))return;
  var m=p.match(/^docs\/(.+?)\/(source|editable)\/([^/]+\.html)$/i);
  if(m){
   var key=m[1],variant=/-plate\.html$/i.test(m[3])?'-plates':'';
   var rootKey=key+variant;
   var group=groups.get(rootKey)||{id:key==='instagram/carousel-01-v3'&&!variant?'carousel-01-v3':slug(rootKey),title:label(key.split('/').at(-1))+(variant?' · Plakalar':''),family:key.split('/')[0],kind:'html',pages:[]};
   group.pages.push(p.slice(5));groups.set(rootKey,group);return
  }
  if(IMAGE.test(p)){
   // Assets are preserved as separate browser-editable whole-image compositions.
   var groupPath=p.slice(5).split('/').slice(0,-1).join('/'),g=raster.get(groupPath)||[];
   g.push(p.slice(5));raster.set(groupPath,g);return
  }
  // Standalone design HTML, but not navigation pages or galleries.
  if(HTML.test(p)&&!/(?:^|\/)index\.html$|(?:^|\/)review\.html$|(?:^|\/)legacy\.html$/i.test(p)
      &&/\/(rollup|banners|typography|applications|social|poster|flyer|design)/i.test(p)){
   single.push(p.slice(5))
  }
 });
 var records=[...groups.values()];
 single.forEach(function(p){records.push({id:slug(p.replace(/\.html$/i,'')),title:label(p.split('/').at(-1).replace(/\.html$/i,'')),family:p.split('/')[0],kind:'html',pages:[p]})});
 raster.forEach(function(v,key){
  // Keep image bundles small enough for existing portable archive page validation.
  for(var j=0;j<v.length;j+=25){
   var batch=v.slice(j,j+25);
   records.push({id:'asset-'+slug(key)+(j?'-'+String(j/25+1):''),title:label(key.split('/').at(-1))+(j?' · '+String(j/25+1):''),family:key.split('/')[0],kind:'image',pages:batch})
  }
 });
 records.forEach(function(r){r.pages.sort(function(a,b){return a.localeCompare(b,undefined,{numeric:true})})});
 var seen=new Set();return records.filter(function(r){
  if(!r.pages.length||!r.id||seen.has(r.id))return false;seen.add(r.id);return true
 }).sort(function(a,b){return(a.kind==='html'?0:1)-(b.kind==='html'?0:1)||a.family.localeCompare(b.family)||a.title.localeCompare(b.title)})
}
function fromTree(tree){if(!Array.isArray(tree))throw Error('Geçersiz GitHub dosya ağacı');return fromPaths(tree.filter(function(x){return x&&x.type==='blob'}).map(function(x){return x.path}))}
function byId(records,id){return records.find(function(r){return r.id===id})||null}
async function load(url){
 var snapshot=[];
 try{var r=await fetch(url,{cache:'no-store'});if(r.ok){var data=await r.json();snapshot=Array.isArray(data)?data:[]}}catch(_){}
 try{
  var remote=await fetch('https://api.github.com/repos/cinegitim/design/git/trees/main?recursive=1',{headers:{Accept:'application/vnd.github+json'},cache:'no-store'});
  if(remote.ok){
   var data=await remote.json();
   if(!data.truncated&&Array.isArray(data.tree)){var live=fromTree(data.tree);if(live.length)return live}
  }
 }catch(_){}
 return snapshot
}
root.BrandstudioCatalog={fromPaths:fromPaths,fromTree:fromTree,byId:byId,load:load};
})(typeof globalThis!=='undefined'?globalThis:this);

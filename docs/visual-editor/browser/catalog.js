/* Public, browser-only Brandstudio design discovery. No account tokens, writes or paid API. */
(function(root){
"use strict";
var IMAGE=/\.(png|jpe?g|webp|svg)$/i,HTML=/\.html$/i;
function validPath(p){return typeof p==='string'&&p.startsWith('docs/')&&!p.split('/').some(function(x){return x==='..'||x===''||x.startsWith('.')})}
function slug(p){return p.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,125)}
function label(s){return s.replace(/[-_]+/g,' ').replace(/\b\w/g,function(c){return c.toUpperCase()})}
function fromPaths(paths){
 var works=new Map(),media=new Map(),standalone=[],list=Array.from(new Set(paths)).filter(validPath).sort();
 function work(key){
  var item=works.get(key);
  if(!item){item={id:key==='instagram/carousel-01-v3'?'carousel-01-v3':slug(key),title:label(key.split('/').at(-1)),family:key.split('/')[0],kind:'html',pages:[]};works.set(key,item)}
  return item
 }
 function addMedia(key,file){
  var g=media.get(key)||[];g.push(file.slice(5));media.set(key,g)
 }
 list.forEach(function(p){
  // True authored compositions: not review plates, source previews or comparison galleries.
  var m=p.match(/^docs\/(.+?)\/(source|editable)\/([^/]+\.html)$/i);
  if(m){
   if(/-plate\.html$/i.test(m[3])||/(?:^|\/)(?:history|drafts|review|previews?)\//i.test(m[1]))return;
   work(m[1]).pages.push(p.slice(5));return
  }
  // Standalone print-format deliverables are source documents, unlike typography direction boards.
  if(/^docs\/[^/]+\/(?:rollup|poster|flyer|banner|banners)\/(?!index\.html$|review\.html$)[^/]+\.html$/i.test(p)){
   standalone.push(p.slice(5));return
  }
 });
 var authored=new Set(works.keys());
 list.forEach(function(p){
  if(!IMAGE.test(p))return;
  var m=p.match(/^docs\/instagram\/([^/]+)\/(.+)$/i);
  if(m){
   var project='instagram/'+m[1],tail=m[2];
   if(authored.has(project))return;
   // Only finished/public artwork. Never use raw photography, brand assets or review comparisons as a design.
   if(/^(?:\d\d[-_][^/]+\.(?:png|jpe?g|webp|svg)|(?:export|png|final|renders|composited)\/[^/]+\.(?:png|jpe?g|webp|svg))$/i.test(tail)){
    addMedia(project,p);return
   }
   if(/^profile-photo\/(?:[^/]+\.(?:png|svg)|variants\/[^/]+\.(?:png|svg))$/i.test(m[1]+'/'+tail)){
    addMedia('instagram/profile-photo',p);return
   }
  }
  var covers=p.match(/^docs\/social-covers\/(assets|[a-z0-9-]+)\/([^/]+\.(?:png|jpe?g|webp|svg))$/i);
  if(covers&&(covers[1]!=='assets'||/^(?:facebook|instagram|linkedin|x-profile|youtube)/i.test(covers[2])))
   addMedia('social-covers/cover-graphics',p);
 });
 var records=Array.from(works.values());
 standalone.forEach(function(p){
  var parent=p.replace(/\.html$/i,''),dir=p.split('/')[0];
  records.push({id:slug(parent),title:label(p.split('/').at(-1).replace(/\.html$/i,'')),family:dir,kind:'html',pages:[p]})
 });
 media.forEach(function(files,key){
  // Prefer editable SVG sources over duplicate PNG renders of the same basename.
  var variants=new Map();
  files.forEach(function(p){
   var k=p.replace(/\.(?:png|jpe?g|webp|svg)$/i,'');
   var old=variants.get(k);
   if(!old||/\.svg$/i.test(p))variants.set(k,p)
  });
  var sorted=Array.from(variants.values()).sort(function(a,b){return a.localeCompare(b,undefined,{numeric:true})});
  for(var j=0;j<sorted.length;j+=25)records.push({
   id:'asset-'+slug(key)+(j?'-'+String(j/25+1):''),
   title:label(key.split('/').at(-1))+(j?' · '+String(j/25+1):'')+' (görsel)',
   family:key.split('/')[0],kind:'image',pages:sorted.slice(j,j+25)
  })
 });
 records.forEach(function(r){r.pages.sort(function(a,b){return a.localeCompare(b,undefined,{numeric:true})})});
 var seen=new Set();
 return records.filter(function(r){if(!r.pages.length||seen.has(r.id))return false;seen.add(r.id);return true})
  .sort(function(a,b){return(a.kind==='html'?0:1)-(b.kind==='html'?0:1)||a.family.localeCompare(b.family)||a.title.localeCompare(b.title)})
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

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
function migrateLegacyPhase2CState(old){
 if(!old||typeof old!=='object')throw Error('Geçersiz eski slayt durumu');
 var next=JSON.parse(JSON.stringify(old)),edits={},groups={};
 Object.entries(old.edits||{}).forEach(function(pair){
  var key=pair[0],m=key.match(/^(\d+):(\d+)$/);
  if(!m)throw Error('Geçersiz slayt katmanı: '+key);
  edits[(Number(m[1])+1)+':'+m[2]]=pair[1]
 });
 Object.entries(old.groups||{}).forEach(function(pair){
  var key=pair[0];
  if(!/^\d+$/.test(key))throw Error('Geçersiz sayfa grubu: '+key);
  groups[String(Number(key)+1)]=pair[1]
 });
 next.edits=edits;next.groups=groups;return next
}
function groupRecords(raw,config){
 if(!config||config.schema!==1||!Array.isArray(config.groups))return raw;
 var items=new Map(raw.map(function(r){return[r.id,r]})),used=new Set(),groups=[];
 var publications=config.socialPublication&&Array.isArray(config.socialPublication.posts)?config.socialPublication.posts:[];
 function publicationFor(ids,groupId){
  return publications.filter(function(p){return (ids.includes(p.productId)||(groupId&&p.groupId===groupId))&&
   p.verified===true&&
   /^https:\/\/(?:www\.)?instagram\.com\/(?:asyadaegitim\/)?(?:p|reel|tv)\/[A-Za-z0-9_-]+\/?(?:\?.*)?$/.test(p.url||'')&&p.publishedAt})
 }
 config.groups.forEach(function(g){
  var versions=(g.versions||[]).map(function(v){
   var item=items.get(v.id);
   if(!item)return null;
   used.add(v.id);
   var pages=item.pages.slice();
   // Phase 2C retains its unchanged first slide from 2B. Preserve the true seven/eight-slide composition.
   if(/^instagram-phase-2c-[a-d]-/.test(v.id)){
    var previous=items.get(v.id.replace('phase-2c-','phase-2b-'));
    if(previous&&previous.pages[0]&&!pages.some(function(p){return /\/(?:01|01-[^/]+)\.html$/.test(p)}))
      pages.unshift(previous.pages[0]);
   }
   var result=Object.assign({},item,{label:v.label,pages:pages,groupId:g.defaultId||g.currentId,category:g.category,categoryPath:(g.categoryPath||[]).slice(),brand:g.brand});
   var proof=publicationFor([v.id]);
   result.lifecycle=proof.length?'published':'in-review';
   result.publications=proof;
   return result
  }).filter(Boolean);
  if(!versions.length)return;
  var latest=versions.find(function(v){return v.id===g.currentId})||versions[versions.length-1];
  var preferred=versions.find(function(v){return v.id===(g.publishedVersionId||g.defaultId)})||latest;
  var matches=publicationFor(versions.map(function(v){return v.id}),g.id);
  groups.push(Object.assign({},preferred,{id:preferred.id,title:g.title,family:g.brand,brand:g.brand,
   category:g.category,categoryPath:(g.categoryPath||[]).slice(),familyId:g.id,
   groupId:preferred.id,defaultId:preferred.id,currentId:latest.id,publishedVersionId:g.publishedVersionId||null,versions:versions,
   lifecycle:matches.length?'published':g.lifecycle||'in-review',publications:matches}));
 });
 var retired=new Set((config.retired||[]).map(function(x){return x.id}));
 raw.forEach(function(r){if(!used.has(r.id)&&!retired.has(r.id))groups.push(Object.assign({},r,{
  category:r.family==='cin-egitim'?'Baskı / Diğer':'Sosyal Medya / Diğer',
  categoryPath:r.family==='cin-egitim'?['Baskı','Diğer']:['Sosyal Medya','Diğer'],
  groupId:r.id,
  currentId:r.id,versions:[Object.assign({},r,{label:'güncel',groupId:r.id})],
  lifecycle:'in-review',publications:[]
 }))});
 return groups.sort(function(a,b){return a.family.localeCompare(b.family)||
  (a.category||'').localeCompare(b.category||'')||a.title.localeCompare(b.title,'tr')})
}
function byId(records,id){
 for(var i=0;i<records.length;i++){
  var g=records[i];
  if(g.id===id||g.groupId===id)return g;
  var v=(g.versions||[]).find(function(x){return x.id===id});
  if(v)return Object.assign({},v,{title:g.title,groupTitle:g.title,category:g.category,brand:g.brand,
   versions:g.versions,groupId:g.groupId||g.id,currentId:g.currentId||g.id,
   categoryPath:g.categoryPath||[],publishedVersionId:g.publishedVersionId||null,
   familyPublications:g.publications||[]})
 }
 return null
}
async function load(url){
 var snapshot=[],config=null;
 try{var r=await fetch(url,{cache:'no-store'});if(r.ok){var data=await r.json();snapshot=Array.isArray(data)?data:[]}}catch(_){}
 try{
  var registryUrl=new URL('product-groups.json',url);
  var response=await fetch(registryUrl,{cache:'no-store'});
  if(response.ok)config=await response.json();
 }catch(_){}
 try{
  var remote=await fetch('https://api.github.com/repos/cinegitim/design/git/trees/main?recursive=1',{headers:{Accept:'application/vnd.github+json'},cache:'no-store'});
  if(remote.ok){
   var data=await remote.json();
   if(!data.truncated&&Array.isArray(data.tree)){var live=fromTree(data.tree);if(live.length)return groupRecords(live,config)}
  }
 }catch(_){}
 return groupRecords(snapshot,config)
}
root.BrandstudioCatalog={fromPaths:fromPaths,fromTree:fromTree,groupRecords:groupRecords,migrateLegacyPhase2CState:migrateLegacyPhase2CState,byId:byId,load:load};
})(typeof globalThis!=='undefined'?globalThis:this);

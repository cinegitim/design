/* Brandstudio shared-style index. Pure, read-only, no storage, API, or side effects.
   Product records, canonical style families, and proposed associations stay separate. */
(function(root){
"use strict";
const MAIN_STYLE_CATEGORY={"Karuseller":"instagram-carousel","Tekil Paylaşımlar":"social-post",
 "Profil ve Kapaklar":"identity-application","Roll-up":"print-catalog"};
const STANDARD_MAIN=["Karuseller","Tekil Paylaşımlar","Profil ve Kapaklar","Roll-up"];
const SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
function check(ok,message){if(!ok)throw Error("Katalog gezinmesi: "+message)}
function asText(x){return typeof x==="string"?x:""}
function categoryOf(product){
 const p=product.categoryPath||[];
 if(p[0]==="Sosyal Medya"){
  if(p[1]==="Karuseller"||p[1]==="Tekil Paylaşımlar")
   return{main:p[1],sub:p[2]||"Diğer"};
  if(p[1]==="Kimlik Uygulamaları")
   return{main:"Profil ve Kapaklar",sub:product.id?.includes("profile-photo")?"Profil Kimliği":"Platform Kapakları"};
 }
 if(p[0]==="Baskı")return{main:"Roll-up",sub:"Fuar ve Kurumsal Tanıtım"};
 return{main:"Sınıflandırılmamış",sub:"Diğer"}
}
function styleFor(registry,brand,main,id,preset){
 const family=(registry.styles||[]).find(s=>s.brand===brand&&s.style_id===id
  &&s.category===MAIN_STYLE_CATEGORY[main]);
 check(!!family,"Bu marka ve ana kategoride kayıtlı olmayan tarz: "+id);
 check(Object.prototype.hasOwnProperty.call(family.presets||{},preset),
  "Tarza ait olmayan çeşitleme: "+preset);
 return family
}
function build(records,config,registry,active){
 check(Array.isArray(records),"Geçersiz ürün kataloğu");
 check(config?.schema===1&&Array.isArray(config.items)&&Array.isArray(config.confirmedVersions),
  "Sınıflandırma belgesi bulunamadı");
 check(registry?.schema===1&&Array.isArray(registry.styles),"Tarz kütüphanesi bulunamadı");
 const byId=new Map(),byProduct=new Map(),sources=new Set();
 for(const p of records){
  const groupId=p.familyId||p.id;
  check(!byId.has(groupId),"Tekrarlanan ürün: "+groupId);
  byId.set(groupId,p);
  const versions=(p.versions||[]).map(v=>v.id);
  check(new Set(versions).size===versions.length,"Tekrarlanan ürün sürümü: "+groupId);
  byProduct.set(groupId,{record:p,versions:new Set(versions)});
  for(const v of versions){check(!sources.has(v),"Bir kaynak sürümü iki ürüne bağlı: "+v);sources.add(v)}
 }
 const defs=new Map();
 for(const item of config.items){
  check(typeof item.groupId==="string"&&SLUG.test(item.groupId)&&!defs.has(item.groupId),"Tekrarlanan veya hatalı sınıflandırma");
  check(byProduct.has(item.groupId),"Katalogda olmayan ürün: "+item.groupId);
  check(STANDARD_MAIN.includes(item.mainCategory)&&typeof item.subCategory==="string"&&item.subCategory.length>0&&item.subCategory.length<=90,
   "Ana/alt kategori hatalı: "+item.groupId);
  const record=byProduct.get(item.groupId).record;
  if(item.suggestion){
   const s=item.suggestion;
   check(s.status==="proposed"&&s.scope==="future-design","Bir öneri geçmiş tasarımı onaylayamaz");
   styleFor(registry,record.brand||record.family,item.mainCategory,s.styleId,s.presetId);
  }
  defs.set(item.groupId,item)
 }
 const confirmed=new Map();
 for(const link of config.confirmedVersions){
  const p=byProduct.get(link.groupId);
  check(!!p&&p.versions.has(link.versionId),"Bağlı olmayan kaynak sürümüne tarz ataması");
  check(link.status==="verified"&&typeof link.evidence==="string"&&/^https:\/\/github\.com\/cinegitim\/design\/(pull|commit)\/[0-9a-fA-F]+\/?$/.test(link.evidence),
   "Kaynak sürümü için doğrulanmış GitHub kanıtı gerekli");
  const definition=defs.get(link.groupId);
  check(!!definition,"Doğrulanmış sürüm sınıflandırılmamış");
  styleFor(registry,p.record.brand||p.record.family,definition.mainCategory,link.styleId,link.presetId);
  check(!confirmed.has(link.versionId),"Sürüme birden fazla kesin tarz ataması");
  confirmed.set(link.versionId,{styleId:link.styleId,presetId:link.presetId,status:"verified",
   versionId:link.versionId,evidence:link.evidence});
 }
 const products=records.map(p=>{
  const id=p.familyId||p.id,def=defs.get(id),fallback=categoryOf(p);
  const main=def?.mainCategory||fallback.main,sub=def?.subCategory||fallback.sub;
  const links=(p.versions||[]).filter(v=>confirmed.has(v.id)).map(v=>confirmed.get(v.id));
  if(def?.suggestion)links.push({styleId:def.suggestion.styleId,presetId:def.suggestion.presetId,
    status:"proposed",versionId:null});
  if(active?.groupId===id&&active.selection?.style_id&&active.selection?.preset_id){
   try{
    styleFor(registry,p.brand||p.family,main,active.selection.style_id,active.selection.preset_id);
    links.unshift({styleId:active.selection.style_id,presetId:active.selection.preset_id,
      status:"draft",versionId:active.versionId||null})
   }catch(_){}
  }
  return{groupId:id,openId:p.id,title:p.title,brand:p.brand||p.family,main,sub,
   versions:(p.versions||[]).map(v=>({id:v.id,label:v.label||"Sürüm"})),
   currentId:p.currentId||p.id,defaultId:p.defaultId||p.id,
   publishedVersionId:p.publishedVersionId||null,links}
 });
 return{products,registry,mainCategories:STANDARD_MAIN.slice(),styleCategories:MAIN_STYLE_CATEGORY}
}
function sortProducts(items,sort){
 const compare=(a,b)=>asText(a).localeCompare(asText(b),"tr");
 return items.sort((a,b)=>{
  if(sort==="style"){
   const left=(a.match?.styleId||"zzzz")+" "+(a.match?.presetId||"zzzz");
   const right=(b.match?.styleId||"zzzz")+" "+(b.match?.presetId||"zzzz");
   return compare(left,right)||compare(a.main,b.main)||compare(a.sub,b.sub)||compare(a.title,b.title)
  }
  if(sort==="category")return compare(a.main,b.main)||compare(a.sub,b.sub)||compare(a.title,b.title);
  return compare(a.title,b.title)||compare(a.groupId,b.groupId)
 })
}
function filter(index,opts={}){
 const brand=opts.brand||"",main=opts.main||"",sub=opts.sub||"",style=opts.style||"",
  preset=opts.preset||"",scope=opts.scope||"all",sort=opts.sort||"category";
 const query=asText(opts.query).trim().toLocaleLowerCase("tr");
 const items=[];
 for(const product of index.products){
  if(brand&&product.brand!==brand||main&&product.main!==main||sub&&product.sub!==sub)continue;
  const matches=product.links.filter(link=>(!style||style===link.styleId)&&(!preset||preset===link.presetId));
  let eligible=matches;
  if(style==="unassigned"){eligible=product.links.filter(x=>x.status==="draft"||x.status==="verified");
   if(eligible.length)continue;eligible=[]}
  else if(style&&matches.length===0)continue;
  if(scope==="verified"){eligible=eligible.filter(x=>x.status==="verified");if(!eligible.length)continue}
  if(scope==="proposed"){eligible=eligible.filter(x=>x.status==="proposed");if(!eligible.length)continue}
  if(scope==="draft"){eligible=eligible.filter(x=>x.status==="draft");if(!eligible.length)continue}
  if(scope==="unassigned"&&product.links.some(x=>x.status==="verified"||x.status==="draft"))continue;
  const match=eligible.find(x=>x.status==="verified")||eligible.find(x=>x.status==="draft")||eligible[0]||null;
  const haystack=[product.title,product.groupId,product.main,product.sub,...product.versions.map(x=>x.label+" "+x.id)].join(" ").toLocaleLowerCase("tr");
  if(query&&!haystack.includes(query))continue;
  items.push({...product,match,matchCount:eligible.length})
 }
 return sortProducts(items,sort)
}
function facets(index,brand,main){
 const products=index.products.filter(p=>(!brand||p.brand===brand)&&(!main||p.main===main));
 const unique=xs=>[...new Set(xs)].sort((a,b)=>a.localeCompare(b,"tr"));
 const allStyles=index.registry.styles.filter(s=>(!brand||s.brand===brand)
  &&(!main||s.category===MAIN_STYLE_CATEGORY[main]));
 return{
  brands:unique(index.products.map(p=>p.brand)),
  mains:unique(index.products.filter(p=>!brand||p.brand===brand).map(p=>p.main)),
  subs:unique(products.map(p=>p.sub)),
  styles:allStyles,
  counts:{products:products.length,proposals:products.filter(p=>p.links.some(x=>x.status==="proposed")).length,
   verified:products.filter(p=>p.links.some(x=>x.status==="verified")).length}
 }
}
function useStats(index,styleId,brand){
 const linked=index.products.filter(p=>(!brand||p.brand===brand)&&p.links.some(x=>x.styleId===styleId));
 return{products:linked.length,subcategories:new Set(linked.map(p=>p.main+"/"+p.sub)).size,
  verified:linked.filter(p=>p.links.some(x=>x.styleId===styleId&&x.status==="verified")).length,
  proposed:linked.filter(p=>p.links.some(x=>x.styleId===styleId&&x.status==="proposed")).length}
}
root.BrandstudioCatalogNavigation={build,filter,facets,useStats,categoryOf,MAIN_STYLE_CATEGORY};
})(globalThis);

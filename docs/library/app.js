/* Brandstudio main-site canonical design library.
   Public, read-only static snapshot; no autosave or API/polling. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=String(text);return el};
const nameBrand=b=>b==="asyada-egitim"?"Asya'da Eğitim":b==="cin-egitim"?"Çin Eğitim":b;
const canonicalURL=(g,v)=>"../visual-editor/browser/?product="+encodeURIComponent(v||g.defaultId);
const styleKey=(styleId,brand)=>brand+"/"+styleId;
const FORMAT={Karuseller:"instagram-carousel","Tekil Paylaşımlar":"social-post","Profil ve Kapaklar":"identity-application","Roll-up":"print-catalog"};
const labels={verified:"Kaynağı doğrulandı",proposed:"Yeni tasarım önerisi"};
const norm=x=>String(x||"").toLocaleLowerCase("tr").normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/ı/g,"i");
let catalog=null;
const query=new URLSearchParams(location.search);
const state={
 brand:["asyada-egitim","cin-egitim"].includes(query.get("brand"))?query.get("brand"):"asyada-egitim",
 view:query.get("view")==="style"?"style":"content",
 main:query.get("main")||"",sub:query.get("sub")||"",style:query.get("style")||"",preset:query.get("preset")||"",
 status:["proposed","verified","unassigned"].includes(query.get("status"))?query.get("status"):"all",
 sort:query.get("view")==="style"?"style":"category",search:""
};
const known=(id)=>$(id)?.value;
const keys=styles=>styles.map(s=>s.id);
const unique=arr=>[...new Set(arr)];
const tr=(a,b)=>String(a).localeCompare(String(b),"tr");
function validCatalog(d){
 if(d?.schema!==1||!Array.isArray(d.products)||!Array.isArray(d.styles)||!Array.isArray(d.categories))
  throw Error("Katalog şeması tanınmadı");
 const groups=new Set(),versions=new Set(),styleMap=new Map();
 for(const s of d.styles){
  const key=styleKey(s.id,s.brand);
  if(styleMap.has(key)||!s.presets?.length||!s.sourcePath)throw Error("Stil tanımı yinelendi veya eksik");
  styleMap.set(key,s)
 }
 for(const p of d.products){
  if(groups.has(p.groupId)||!p.title||!p.mainCategory||!p.subCategory||!Array.isArray(p.versions))
   throw Error("Ürün sınıflandırması geçersiz");
  groups.add(p.groupId);
  for(const v of p.versions){if(versions.has(v.id))throw Error("Kaynak sürümü iki aileye bağlanmış");versions.add(v.id)}
  for(const link of p.styleLinks||[]){
   const s=styleMap.get(styleKey(link.styleId,p.brand));
   if(!s||s.category!==FORMAT[p.mainCategory]||!s.presets.some(v=>v.id===link.presetId))
    throw Error("Ürüne yanlış marka, format veya çeşitleme bağlanmış");
   if(!["verified","proposed"].includes(link.status))throw Error("Desteklenmeyen tarz ilişki durumu")
  }
 }
 return styleMap
}
const styleByKey=new Map();
function styleFor(p,id){return styleByKey.get(styleKey(id,p.brand))}
function stylesForBrand(){return catalog.styles.filter(s=>s.brand===state.brand)}
function filteredProducts(){
 return catalog.products.filter(p=>{
  if(p.brand!==state.brand)return false;
  if(state.main&&p.mainCategory!==state.main)return false;
  if(state.sub&&p.subCategory!==state.sub)return false;
  if(state.search&&!norm([p.title,p.mainCategory,p.subCategory,p.groupId,
   ...p.versions.map(v=>v.id+" "+v.label)].join(" ")).includes(norm(state.search)))return false;
  if(state.style==="unassigned"&&p.styleLinks.length)return false;
  const associations=p.styleLinks.filter(l=>(!state.style||state.style==="unassigned"||l.styleId===state.style)
   &&(!state.preset||l.presetId===state.preset));
  if(state.style&&state.style!=="unassigned"&&!associations.length)return false;
  if(state.preset&&!associations.length)return false;
  if(state.status==="unassigned")return p.styleLinks.length===0;
  if(["verified","proposed"].includes(state.status))
   return associations.some(l=>l.status===state.status);
  return true
 })
}
function usage(s,products=catalog.products){
 const involved=products.filter(p=>p.brand===s.brand&&p.styleLinks.some(l=>l.styleId===s.id));
 const subject=unique(involved.map(p=>p.subCategory));
 return {products:involved.length,subjects:subject,verified:involved.filter(p=>p.styleLinks.some(l=>l.styleId===s.id&&l.status==="verified")).length}
}
function setSelect(id,opts,value,disabled){
 const select=$(id);select.replaceChildren();
 for(const o of opts){const entry=node("option","",o.label);entry.value=o.id;select.append(entry)}
 select.value=opts.some(x=>x.id===value)?value:opts[0]?.id||"";
 select.disabled=Boolean(disabled)||opts.length<2;
 return select.value
}
function updateURL(){
 const q=new URLSearchParams();
 if(state.brand!=="asyada-egitim")q.set("brand",state.brand);
 if(state.view!=="content")q.set("view",state.view);
 for(const key of ["main","sub","style","preset","status"])
  if(state[key]&&!(key==="status"&&state.status==="all"))q.set(key,state[key]);
 history.replaceState(null,"",location.pathname+(q.size?"?"+q.toString():"")+location.hash)
}
function refreshControls(){
 const brands=unique(catalog.products.map(p=>p.brand));
 state.brand=setSelect("brand",brands.map(b=>({id:b,label:nameBrand(b)})),state.brand);
 const products=catalog.products.filter(p=>p.brand===state.brand);
 const mains=unique(products.map(p=>p.mainCategory));
 if(state.main&&!mains.includes(state.main)){state.main="";state.sub=""}
 state.main=setSelect("main",[{id:"",label:"Bütün ana kategoriler"},...mains.map(x=>({id:x,label:x}))],state.main);
 const subs=unique(products.filter(p=>!state.main||p.mainCategory===state.main).map(p=>p.subCategory));
 if(state.sub&&!subs.includes(state.sub))state.sub="";
 state.sub=setSelect("sub",[{id:"",label:"Bütün alt kategoriler"},...subs.map(x=>({id:x,label:x}))],state.sub);
 const ss=stylesForBrand().filter(style=>!state.main||style.category===FORMAT[state.main]);
 const choices=[{id:"",label:"Bütün ortak tarzlar"},...ss.map(style=>({id:style.id,label:style.name})),
  {id:"unassigned",label:"Tarzı belirlenmemiş"}];
 if(state.style&&!choices.some(o=>o.id===state.style)){state.style="";state.preset=""}
 state.style=setSelect("style",choices,state.style);
 const focus=ss.find(x=>x.id===state.style);
 state.preset=setSelect("preset",[{id:"",label:"Bütün çeşitlemeler"},...(focus?.presets||[]).map(x=>({id:x.id,label:x.label}))],
   state.preset,!focus);
 $("mode-content").setAttribute("aria-pressed",String(state.view==="content"));
 $("mode-style").setAttribute("aria-pressed",String(state.view==="style"));
 $("library-content").dataset.view=state.view;
 $("catalog-crumb").textContent="";
 $("sort").value=state.sort;
 $("status").value=state.status;
 if($("search").value!==state.search)$("search").value=state.search;
 updateURL()
}
function syncMobileSections(mode=state.view){
 const mobile=window.matchMedia("(max-width:700px)").matches;
 $("sidebar-categories").open=!mobile||mode==="content";
 $("sidebar-styles").open=!mobile||mode==="style"
}
const clickNav=(button,selected,callback)=>{
 button.type="button";button.setAttribute("aria-pressed",String(Boolean(selected)));
 button.onclick=callback;
 return button
};
function renderCategories(){
 const root=$("category-tree");root.replaceChildren();
 const items=catalog.products.filter(p=>p.brand===state.brand);
 const all=clickNav(node("button","nav-item","Bütün ürünler"),!state.main&&state.view==="content",()=>{
  state.view="content";state.main="";state.sub="";state.style="";state.preset="";state.sort="category";syncMobileSections("content");render()
 });
 all.append(node("span","count",items.length));root.append(all);
 const mains=unique(items.map(x=>x.mainCategory));
 for(const main of mains){
  const members=items.filter(p=>p.mainCategory===main);
  const details=node("details","sidebar-group");
  details.open=state.main===main||(!state.main&&main==="Karuseller"&&window.matchMedia("(min-width:701px)").matches);
  const summary=node("summary");
  summary.append(node("span","",main),node("b","",members.length));details.append(summary);
  const options=node("div","sidebar-options");
  const allMain=clickNav(node("button","nav-item","Tüm "+main),state.view==="content"&&
   state.main===main&&!state.sub,()=>{
    state.view="content";state.main=main;state.sub="";state.style="";state.preset="";state.sort="category";syncMobileSections("content");render()
   });
  allMain.append(node("span","count",members.length));options.append(allMain);
  const subjects=unique(members.map(p=>p.subCategory)).sort(tr);
  for(const sub of subjects){
   const btn=clickNav(node("button","nav-item"),state.view==="content"&&state.main===main&&state.sub===sub,()=>{
    state.view="content";state.main=main;state.sub=sub;state.style="";state.preset="";state.sort="category";syncMobileSections("content");render()
   });
   btn.append(node("span","",sub),node("span","count",members.filter(p=>p.subCategory===sub).length));
   options.append(btn)
  }
  details.append(options);root.append(details)
 }
}
function renderStyleCards(){
 const root=$("style-rail");root.replaceChildren();
 const ss=stylesForBrand().filter(x=>!state.main||x.category===FORMAT[state.main]);
 const total=catalog.products.filter(p=>p.brand===state.brand).length;
 const all=clickNav(node("button","nav-item","Bütün tarzlar"),state.view==="style"&&!state.style,()=>{
  state.view="style";state.main="";state.sub="";state.style="";state.preset="";state.sort="style";syncMobileSections("style");render()
 });
 all.append(node("span","count",total));root.append(all);
 for(const style of ss){
  const info=usage(style);
  const btn=clickNav(node("button","nav-item nav-style"),state.view==="style"&&state.style===style.id,()=>{
   state.view="style";state.main="";state.sub="";state.style=style.id;state.preset="";state.sort="style";syncMobileSections("style");render()
  });
  btn.dataset.style=style.id;
  const copy=node("span","nav-copy");
  copy.append(node("span","",style.name),node("small","",info.subjects.length+" içerik alanı · "+style.presets.length+" çeşitleme"));
  btn.append(copy,node("span","count",info.products));
  root.append(btn)
 }
}
function linkBadge(link,p){
 const style=styleFor(p,link.styleId);
 const name=style?.name||link.styleId;
 const preset=style?.presets.find(x=>x.id===link.presetId)?.label||link.presetId;
 const row=node("span","association "+link.status);
 row.append(node("strong","",name+" / "+preset),
  node("small","",link.status==="proposed"?"· Öneri":"· Kaynağı doğrulandı"));
 row.title=link.status==="proposed"
  ?"Gelecek tasarımlar için öneridir; bu kaynağın tarzı doğrulanmış değildir."
  :"Bu tarzın ilişkisi kaynak sürümü üzerinden doğrulandı.";
 return row
}
function productCard(p,focus){
 const outer=node("article","product-card");
 const main=node("div","product-main");
 const label=node("div","product-label",p.mainCategory+" › "+p.subCategory);
 const title=node("h3","",p.title);
 const marker=node("div","associations");
 let links=focus?[focus]:p.styleLinks;
 if(state.view==="content"&&(state.style||state.preset||state.status!=="all"))
  links=p.styleLinks.filter(l=>(!state.style||state.style==="unassigned"||l.styleId===state.style)
   &&(!state.preset||l.presetId===state.preset)&&(["all","unassigned"].includes(state.status)||l.status===state.status));
 for(const link of links||[])marker.append(linkBadge(link,p));
 if(!links?.length)marker.append(node("span","unassigned","Tarz henüz belirlenmedi"));
 main.append(label,title,marker);
 const actions=node("div","product-actions");
 const editor=node("a","primary-link","Aç ↗");
 editor.href=canonicalURL(p,focus?.status==="verified"&&focus.versionId?focus.versionId:p.defaultId);
 editor.setAttribute("aria-label",p.title+" · Visual Editor'da aç");
 const detail=node("details","versions-details");
 const summary=node("summary","",p.versions.length+" sürüm ▾");
 summary.setAttribute("aria-label",p.title+" için kaynak sürümleri");
 const versions=node("div","versions-list");
 for(const v of p.versions){
  const item=node("a","",v.label+(v.id===p.currentId?" · Son taslak":"")+
   (v.id===p.publishedVersionId?" · Yayınlanan":""));
  item.href=canonicalURL(p,v.id);
  versions.append(item)
 }
 detail.append(summary,versions);
 actions.append(detail,editor);
 outer.append(main,actions);
 return outer
}
function entries(products){
 if(state.view==="content")return products.map(p=>({p,link:null}));
 const rows=[];
 for(const p of products){
  const links=p.styleLinks.filter(l=>(!state.style||state.style==="unassigned"||l.styleId===state.style)
   &&(!state.preset||l.presetId===state.preset)
   &&(["all","unassigned"].includes(state.status)||l.status===state.status));
  if(links.length){
   for(const link of links)rows.push({p,link})
  }else if(!p.styleLinks.length&&(!state.style||state.style==="unassigned")){
   rows.push({p,link:null})
  }
 }
 return rows
}
function associationForRow(row){
 return row.link||row.p.styleLinks.find(l=>(!state.style||l.styleId===state.style)&&
  (!state.preset||l.presetId===state.preset)&&
  (state.status==="all"||l.status===state.status))||row.p.styleLinks[0]||null
}
function sortRows(rows){
 const group=row=>{
  const link=associationForRow(row);
  return state.view==="style"||state.sort==="style"
   ?(link?.styleId||"zzzz")+"/"+(link?.presetId||"zzzz")
   :row.p.mainCategory+"/"+row.p.subCategory
 };
 return rows.sort((a,b)=>{
  if(state.sort==="title")return tr(a.p.title,b.p.title);
  return tr(group(a),group(b))||tr(a.p.subCategory,b.p.subCategory)||tr(a.p.title,b.p.title)
 })
}
function heading(row){
 if(state.sort==="title")return "Ürün adına göre";
 if(state.view==="style"||state.sort==="style"){
  const link=associationForRow(row);
  if(!link)return "Tarz belirlenmeyenler";
  const s=styleFor(row.p,link.styleId);
  return s?.name||link.styleId
 }
 return state.main?row.p.subCategory:row.p.mainCategory+" / "+row.p.subCategory
}
function renderResults(){
 const products=filteredProducts(),rows=sortRows(entries(products));
 const total=catalog.products.filter(p=>p.brand===state.brand).length;
 const root=$("results");root.replaceChildren();
 $("result-count").textContent=products.length+" / "+total+" ürün";
 const style=stylesForBrand().find(x=>x.id===state.style);
 $("active-heading").textContent=state.view==="style"
  ?(style?.name||"Ortak tarzlar"):state.sub||state.main||"Bütün ürünler";
 $("scope-note").textContent=state.view==="style"&&rows.length
  ?"Farklı içeriklerdeki ortak tarz önerileri ve doğrulanmış sürümler bir arada gösterilir.":"";
 if(!rows.length){
  root.append(node("p","empty","Bu seçimde ürün yok. Bir kategori veya filtreyi kaldırarak diğer kayıtları görebilirsin."));
  return
 }
 let last="",section=null,countElement=null,currentCount=0;
 for(const row of rows){
  const label=heading(row);
  if(label!==last){
   section=node("section","result-group");
   const header=node("div","result-heading");
   countElement=node("span","", "0 ürün");
   header.append(node("h2","",label),countElement);
   section.append(header,node("div","product-grid"));
   root.append(section);last=label;currentCount=0
  }
  currentCount++;countElement.textContent=currentCount+" kayıt";
  section.lastChild.append(productCard(row.p,row.link))
 }
}
function renderFacts(){
 const products=catalog.products.filter(p=>p.brand===state.brand);
 const count=products.reduce((n,p)=>n+p.versions.length,0);
 const links=products.flatMap(p=>p.styleLinks);
 $("metric-products").textContent=String(products.length);
 $("metric-versions").textContent=String(count);
 $("metric-styles").textContent=String(stylesForBrand().length);
 const verified=links.filter(x=>x.status==="verified").length;
 const proposals=links.filter(x=>x.status==="proposed").length;
 $("metric-connections").textContent=verified?verified+" doğrulanmış · "+proposals+" öneri":proposals+" tarz önerisi";
 const style=stylesForBrand().find(x=>x.id===state.style);
 const el=$("style-explanation");
 if(!style){el.hidden=true;return}
 el.hidden=false;el.replaceChildren();
 const info=usage(style);
 el.append(node("h2","",style.name),
  node("p","",style.description),
  node("p","usage",info.products+" ürün · "+info.subjects.length+" içerik alanı · "+
   info.verified+" kaynak sürümü doğrulanmış"));
 const tags=node("div","topic-tags");
 for(const label of info.subjects)tags.append(node("span","topic-tag",label));
 el.append(tags);
 const source=node("a","source-link","Kanonik stil tanımı ↗");
 source.href="https://github.com/cinegitim/design/blob/main/"+style.sourcePath;
 source.target="_blank";source.rel="noopener noreferrer";
 el.append(source)
}
function renderActiveFilters(){
 const root=$("active-filters");root.replaceChildren();
 const set=(label,reset)=>{
  const chip=node("button","filter-pill",label+" ×");chip.type="button";
  chip.setAttribute("aria-label",label+" filtresini kaldır");
  chip.onclick=()=>{reset();render()};
  root.append(chip)
 };
 if(state.main)set(state.main,()=>{state.main="";state.sub="";state.style="";state.preset=""});
 if(state.sub)set(state.sub,()=>{state.sub=""});
 const style=stylesForBrand().find(x=>x.id===state.style);
 if(state.style)set(style?.name||"Tarzı belirlenmemiş",()=>{state.style="";state.preset=""});
 if(state.preset){
  const preset=style?.presets.find(x=>x.id===state.preset);
  set(preset?.label||state.preset,()=>{state.preset=""})
 }
 if(state.status!=="all")set(state.status==="proposed"?"Öneriler":state.status==="verified"?"Doğrulananlar":"Atanmamış",
  ()=>{state.status="all"})
}

function render(){
 refreshControls();renderCategories();renderStyleCards();renderFacts();renderResults();renderActiveFilters()
}
function connect(){
 $("mode-content").onclick=()=>{state.view="content";state.sort="category";syncMobileSections("content");render()};
 $("mode-style").onclick=()=>{state.view="style";state.main="";state.sub="";state.sort="style";syncMobileSections("style");render()};
 for(const key of ["brand","main","sub","style","preset"]){
  $(key).onchange=()=>{
   state[key]=$(key).value;
   if(key==="brand"){state.main="";state.sub="";state.style="";state.preset=""}
   if(key==="main"){state.sub="";state.style="";state.preset=""}
   if(key==="style"){state.preset="";if(state.view==="style"){state.main="";state.sub=""}}
   render()
  }
 }
 $("advanced-filters").addEventListener("toggle",()=>{
  $("advanced-panel").hidden=!$("advanced-filters").open
 });
 $("sort").onchange=()=>{state.sort=$("sort").value;renderResults()};
 $("status").onchange=()=>{state.status=$("status").value;renderResults();renderActiveFilters();updateURL()};
 $("search").oninput=()=>{state.search=$("search").value;renderResults()};
 $("reset").onclick=()=>{
  state.main="";state.sub="";state.style="";state.preset="";
  state.search="";state.status="all";state.sort=state.view==="style"?"style":"category";
  render()
 }
}

async function init(){
 try{
  const response=await fetch("catalog.json",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  catalog=await response.json();
  const validated=validCatalog(catalog);
  for(const [k,v] of validated)styleByKey.set(k,v);
  const styleQuery=query.get("style");
  if(styleQuery&&stylesForBrand().some(s=>s.id===styleQuery))state.style=styleQuery;
  connect();syncMobileSections();
  const mobileQuery=window.matchMedia("(max-width:700px)");
  if(mobileQuery.addEventListener)mobileQuery.addEventListener("change",()=>syncMobileSections());
  render();
  $("load-status").hidden=true;$("library-content").hidden=false
 }catch(err){
  $("load-status").textContent="Tasarım kütüphanesi yüklenemedi: "+err.message;
  $("load-status").setAttribute("role","alert")
 }
}
init()
})();

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
const clickNav=(button,selected,callback)=>{
 button.type="button";button.setAttribute("aria-pressed",String(Boolean(selected)));
 button.onclick=callback;
 return button
};
function renderCategories(){
 const root=$("category-tree");root.replaceChildren();
 const items=catalog.products.filter(p=>p.brand===state.brand);
 const all=clickNav(node("button","nav-item","Bütün ürünler"),!state.main&&state.view==="content",()=>{
  state.view="content";state.main="";state.sub="";state.style="";state.preset="";state.sort="category";render()
 });
 all.append(node("span","count",items.length));root.append(all);
 const mains=unique(items.map(x=>x.mainCategory));
 for(const main of mains){
  const members=items.filter(p=>p.mainCategory===main);
  const details=node("details","sidebar-group");
  details.open=state.main===main||(!state.main&&main==="Karuseller");
  const summary=node("summary");
  summary.append(node("span","",main),node("b","",members.length));details.append(summary);
  const options=node("div","sidebar-options");
  const allMain=clickNav(node("button","nav-item","Tüm "+main),state.view==="content"&&
   state.main===main&&!state.sub,()=>{
    state.view="content";state.main=main;state.sub="";state.style="";state.preset="";state.sort="category";render()
   });
  allMain.append(node("span","count",members.length));options.append(allMain);
  const subjects=unique(members.map(p=>p.subCategory)).sort(tr);
  for(const sub of subjects){
   const btn=clickNav(node("button","nav-item"),state.view==="content"&&state.main===main&&state.sub===sub,()=>{
    state.view="content";state.main=main;state.sub=sub;state.style="";state.preset="";state.sort="category";render()
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
  state.view="style";state.main="";state.sub="";state.style="";state.preset="";state.sort="style";render()
 });
 all.append(node("span","count",total));root.append(all);
 for(const style of ss){
  const info=usage(style);
  const btn=clickNav(node("button","nav-item nav-style"),state.view==="style"&&state.style===style.id,()=>{
   state.view="style";state.main="";state.sub="";state.style=style.id;state.preset="";state.sort="style";render()
  });
  btn.dataset.style=style.id;
  const copy=node("span","nav-copy");
  copy.append(node("span","",style.name),node("small","",info.subjects.length+" içerik alanı · "+style.presets.length+" çeşitleme"));
  btn.append(copy,node("span","count",info.products));
  root.append(btn)
 }
}
function linkBadge(link,p){
 const s=styleFor(p,link.styleId);
 const text=(s?.name||link.styleId)+" · "+(s?.presets.find(x=>x.id===link.presetId)?.label||link.presetId);
 const row=node("span","association "+link.status);
 row.append(node("strong","",text),node("small","",labels[link.status]||link.status));
 return row
}
function productCard(p,focus){
 const outer=node("article","product-card");
 const header=node("div","product-label",p.mainCategory+" / "+p.subCategory);
 const name=node("h3","",p.title);const meta=node("p","meta",p.versions.length+" kaynak sürümü"
  +(p.publishedVersionId?" · Kayıtlı yayın sürümü":" · Yayın sürümü eşleştirilmemiş"));
 const marker=node("div","associations");
 const links=focus?[focus]:(p.styleLinks.length?p.styleLinks:[null]);
 for(const link of links)marker.append(link?linkBadge(link,p):node("span","unassigned","Tarz belirlenmedi"));
 const foot=node("div","product-actions");
 const open=node("a","primary-link","Visual Editor'da aç");
 open.href=canonicalURL(p,focus?.status==="verified"&&focus.versionId?focus.versionId:p.defaultId);
 const details=node("details","versions-details");
 const summary=node("summary","","Kaynak sürümleri ("+p.versions.length+")");
 const versions=node("div","versions-list");
 for(const v of p.versions){
  const item=node("a","",v.label+(v.id===p.currentId?" · Son taslak":"")+
   (v.id===p.publishedVersionId?" · Yayınlanan":""));
  item.href=canonicalURL(p,v.id);versions.append(item)
 }
 details.append(summary,versions);
 foot.append(open,details);
 outer.append(header,name,meta,marker,foot);
 return outer
}
function entries(products){
 if(state.view==="content")return products.map(p=>({p,link:null}));
 const rows=[];
 for(const p of products){
  const links=p.styleLinks.filter(l=>(!state.style||l.styleId===state.style)&&(!state.preset||l.presetId===state.preset)&&
   (state.status==="all"||state.status==="unassigned"||l.status===state.status));
  if(links.length)for(const l of links)rows.push({p,link:l});
  else if(!state.style&&!p.styleLinks.length)rows.push({p,link:null})
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
 return rows.sort((a,b)=>state.sort==="title"?tr(a.p.title,b.p.title):
  tr(group(a),group(b))||tr(a.p.subCategory,b.p.subCategory)||tr(a.p.title,b.p.title))
}
function heading(row){
 if(state.view==="style"||state.sort==="style"){
  const link=associationForRow(row);
  if(!link)return "Tarz belirlenmeyenler";
  const s=styleFor(row.p,link.styleId);
  const preset=s?.presets.find(x=>x.id===link.presetId);
  return (s?.name||link.styleId)+" / "+(preset?.label||link.presetId)
 }
 return row.p.mainCategory+" / "+row.p.subCategory
}
function renderResults(){
 const products=filteredProducts(),rows=sortRows(entries(products));
 const total=catalog.products.filter(p=>p.brand===state.brand).length;
 const root=$("results");root.replaceChildren();
 $("result-count").textContent=products.length+" / "+total+" ürün · "+rows.length+" görünüm kaydı";
 $("scope-note").textContent=state.view==="style"
 ?"Aynı ürün farklı sürümlerde birden fazla ortak tarza bağlanabilir; kaynak ürün kopyalanmaz."
 :"İçerik konumu sabittir; ortak görsel tarzlar farklı içerik kategorilerinde tekrar kullanılabilir.";
 if(!rows.length){root.append(node("p","empty","Bu seçimde ürün bulunamadı. Başka kategori, tarz veya ilişki durumu seçebilirsiniz."));return}
 let last="",group=null;
 for(const row of rows){
  const h=heading(row);
  if(h!==last){
   group=node("section","result-group");const title=node("div","result-heading");
   title.append(node("h2","",h),node("span","",state.view==="style"||state.sort==="style"?"Ortak tasarım dili":"İçerik grubu"));
   group.append(title);
   const grid=node("div","product-grid");group.append(grid);root.append(group);last=h
  }
  group.lastChild.append(productCard(row.p,row.link))
 }
}
function renderFacts(){
 const products=catalog.products.filter(p=>p.brand===state.brand);
 const all=products.reduce((n,p)=>n+p.versions.length,0),linked=products.filter(p=>p.styleLinks.length).length;
 $("metric-products").textContent=String(products.length);
 $("metric-versions").textContent=String(all);
 $("metric-styles").textContent=String(stylesForBrand().length);
 $("metric-connections").textContent=linked+" öneri / bağlantı";
 const s=stylesForBrand().find(s=>s.id===state.style);
 const el=$("style-explanation");
 if(s){
  const use=usage(s);
  el.hidden=false;el.replaceChildren();
  el.append(node("span","eyebrow","Paylaşılan tasarım dili"),node("h2","",s.name),
   node("p","",s.description),
   node("p","usage",use.products+" ürün · "+use.subjects.length+" içerik alt kategorisi · "+use.verified+" kaynak sürümü doğrulanmış"));
  const where=node("div","topic-tags");
  for(const sub of use.subjects){const tag=node("span","topic-tag",sub);where.append(tag)}
  el.append(where);
  const source=node("a","source-link","Kanonik tarz tanımı");
  source.href="https://github.com/cinegitim/design/blob/main/"+s.sourcePath;
  source.target="_blank";source.rel="noopener noreferrer";
  el.append(source)
 }else el.hidden=true
}
function render(){
 refreshControls();renderStyleCards();renderFacts();renderResults()
}
function connect(){
 $("mode-content").onclick=()=>{state.view="content";state.sort="category";render()};
 $("mode-style").onclick=()=>{state.view="style";state.main="";state.sub="";state.sort="style";render()};
 for(const key of ["brand","main","sub","style","preset"]){
  $(key).onchange=()=>{state[key]=$(key).value;
   if(key==="brand"){state.main="";state.sub="";state.style="";state.preset=""}
   if(key==="main"){state.sub="";state.style="";state.preset=""}
   if(key==="style"){state.preset="";if(state.view==="style"){state.main="";state.sub=""}}
   render()
  }
 }
 $("sort").onchange=()=>{state.sort=$("sort").value;renderResults()};
 $("status").onchange=()=>{state.status=$("status").value;renderResults()};
 $("search").oninput=()=>{state.search=$("search").value;renderResults()};
 $("reset").onclick=()=>{state.main="";state.sub="";state.style="";state.preset="";state.search="";state.status="all";state.sort=state.view==="style"?"style":"category";render()};
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
  connect();render();
  $("load-status").hidden=true;$("library-content").hidden=false
 }catch(err){
  $("load-status").textContent="Tasarım kütüphanesi yüklenemedi: "+err.message;
  $("load-status").setAttribute("role","alert")
 }
}
init()
})();

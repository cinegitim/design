/* Browser UI for the shared Brandstudio catalog. No writes, no new API.
   All DOM text is textContent; source assets and edit state are untouched. */
(function(root){
"use strict";
const $=id=>document.getElementById(id);
const el=(tag,className,label)=>{const x=document.createElement(tag);if(className)x.className=className;if(label!==undefined)x.textContent=label;return x};
function optionList(id,items,selected){
 const select=$(id),current=String(selected||"");select.replaceChildren();
 for(const item of items){
  const option=el("option","",item.label);option.value=item.id;select.append(option)
 }
 select.value=items.some(x=>x.id===current)?current:items[0]?.id||"";
 select.disabled=items.length<2;
 return select.value
}
const any={id:"",label:"Tümü"};
function create({model,records,classification,styleRegistry,onOpen,getActive}){
 let opened=false,mode="content",brand="",main="",sub="",style="",preset="",scope="all",sort="category",query="";
 const shell=$("catalog-navigator");
 if(!shell||!model||!Array.isArray(records))throw Error("Gezinme denetimi eksik");
 let index;
 function current(){
  return typeof getActive==="function"?getActive():null
 }
 function refreshIndex(){index=model.build(records,classification,styleRegistry,current())}
 function formats(){
  const f=model.facets(index,brand,main);
  if(!f.mains.includes(main))main="";
  if(!f.subs.includes(sub))sub="";
  brand=optionList("nav-brand",[{id:"",label:"Tüm markalar"},...f.brands.map(x=>({id:x,label:x==="cin-egitim"?"Çin Eğitim":"Asya'da Eğitim"}))],brand);
  // Facets must be recalculated when a parent filter was invalidated.
  const fresh=model.facets(index,brand,main);
  main=optionList("nav-main",[any,...fresh.mains.map(x=>({id:x,label:x}))],main);
  const narrower=model.facets(index,brand,main);
  sub=optionList("nav-sub",[any,...narrower.subs.map(x=>({id:x,label:x}))],sub);
  const allStyles=narrower.styles;
  style=optionList("nav-style",[{id:"",label:"Bütün tarzlar"},
   ...allStyles.map(x=>({id:x.style_id,label:x.name+" · "+(x.status==="review-only"?"incelemede":x.status)})),
   {id:"unassigned",label:"Tarzı belirlenmemiş"}],style);
  const selectedStyle=allStyles.find(x=>x.style_id===style);
  preset=optionList("nav-preset",[any,...Object.entries(selectedStyle?.presets||{})
   .map(([id,p])=>({id,label:p.label}))],preset);
  $("nav-category-label").textContent=mode==="content"
   ?"Ana kategori → İçerik alt kategorisi → Tarz → Çeşitleme → Ürün"
   :"Ortak tarz → Çeşitleme → Ana kategori → İçerik alt kategorisi → Ürün";
  shell.dataset.mode=mode;
  $("nav-mode-content").setAttribute("aria-pressed",String(mode==="content"));
  $("nav-mode-style").setAttribute("aria-pressed",String(mode==="style"));
 }
 const statusText=link=>!link?"Tarz atanmamış":link.status==="verified"?"Kaynağı doğrulandı"
  :link.status==="draft"?"Bu çalışma alanında seçili":"Öneri · geçmiş ürüne atanmadı";
 function renderRows(){
  const products=model.filter(index,{mode,brand,main,sub,style,preset,scope,sort,query});
  const target=$("nav-results");target.replaceChildren();
  const selectedStyle=index.registry.styles.find(s=>s.brand===brand&&s.style_id===style);
  const stats=style&&style!=="unassigned"?model.useStats(index,style,brand):null;
  $("nav-summary").textContent=products.length+" ürün ailesi gösteriliyor"
   +(stats?" · "+(selectedStyle?.name||style)+" "+stats.subcategories+
    " içerik alt kategorisinde · "+stats.verified+" doğrulanmış / "+stats.proposed+" öneri":"")
   +" · İçerik konumu ile tarz bağımsızdır; kaynak sürümleri korunur.";
  if(!products.length){
   target.append(el("p","nav-empty",
    style&&scope==="verified"?"Bu tarza doğrulanarak bağlanmış geçmiş kaynak sürümü yok. Önerileri görmek için 'Öneriler ve doğrulananlar' seçin."
    :"Bu filtrelerde ürün yok. Kategoriyi, tarzı veya doğrulama durumunu değiştirebilirsiniz."));
   return
  }
  let prev="";
  for(const item of products){
   const family=index.registry.styles.find(s=>s.brand===item.brand&&s.style_id===item.match?.styleId);
   const familyLabel=family?.name||"Tarzı belirlenmemiş";
   const presetLabel=item.match?.presetId?family?.presets?.[item.match.presetId]?.label||item.match.presetId:null;
   const header=mode==="style"||sort==="style"
    ?familyLabel+(presetLabel?" / "+presetLabel:""):item.main+" / "+item.sub;
   if(header!==prev){target.append(el("h3","nav-group-heading",header));prev=header}
   const card=el("div","nav-product");
   if(item.openId===current()?.openId||item.groupId===current()?.groupId)card.dataset.active="true";
   const mainCell=el("div","nav-product-main");
   const title=el("strong","nav-product-title",item.title);
   const meta=el("div","nav-product-meta",item.main+" › "+item.sub);
   const badge=el("div","nav-product-status",statusText(item.match));
   const trail=el("div","nav-product-details",
    (family?"Ortak tarz: "+family.name+(presetLabel?" › "+presetLabel:""):"Sınıflandırma bekliyor")+
    " · "+item.versions.length+" kaynak sürümü"+
    (item.publishedVersionId?" · Yayınlanan sürüm kaydı var":""));
   mainCell.append(title,meta,badge,trail);
   const actions=el("div","nav-product-actions");
   const open=el("button","btn nav-product-open","Ürünü aç");
   open.type="button";
   open.addEventListener("click",()=>{
    const targetVersion=item.match?.status==="verified"&&item.match.versionId?item.match.versionId:item.defaultId;
    if(onOpen(targetVersion)!==false)show(false)
   });
   actions.append(open);card.append(mainCell,actions);target.append(card)
  }
 }
 function render(){refreshIndex();formats();renderRows()}
 function show(value){
  opened=Boolean(value);
  shell.hidden=!opened;
  $("catalog-explore-toggle").setAttribute("aria-expanded",String(opened));
  if(opened){render();$("nav-search").focus()}
 }
 for(const [id,key] of [
  ["nav-brand","brand"],["nav-main","main"],["nav-sub","sub"],["nav-style","style"],["nav-preset","preset"]]){
  $(id).addEventListener("change",()=>{
   const val=$(id).value;
   if(key==="brand"){brand=val;main="";sub="";style="";preset=""}
   else if(key==="main"){main=val;sub="";style="";preset=""}
   else if(key==="sub"){sub=val}
   else if(key==="style"){style=val;preset=""}
   else if(key==="preset")preset=val;
   render()
  })
 }
 $("nav-scope").addEventListener("change",()=>{scope=$("nav-scope").value;renderRows()});
 $("nav-sort").addEventListener("change",()=>{sort=$("nav-sort").value;renderRows()});
 $("nav-search").addEventListener("input",()=>{query=$("nav-search").value;renderRows()});
 $("nav-mode-content").addEventListener("click",()=>{mode="content";sort="category";$("nav-sort").value=sort;render()});
 $("nav-mode-style").addEventListener("click",()=>{mode="style";sort="style";$("nav-sort").value=sort;render()});
 $("catalog-explore-toggle").addEventListener("click",()=>show(!opened));
 $("nav-close").addEventListener("click",()=>show(false));
 document.addEventListener("keydown",event=>{
  if(event.key==="Escape"&&opened){show(false);$("catalog-explore-toggle").focus()}
 });
 const a=current();
 brand=a?.brand||"asyada-egitim";
 refreshIndex();
 return{show,sync(){
  if(opened)render()
 },getState:()=>({mode,brand,main,sub,style,preset,scope,sort,query})}
}
root.BrandstudioCatalogNavigatorUI={create};
})(globalThis);

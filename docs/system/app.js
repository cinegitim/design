/* Brandstudio System Hub: read-only UI built from a validated GitHub snapshot. */
(function(){
"use strict";
const el=id=>document.getElementById(id);
const node=(tag,cls,content)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=String(content);return n};
let data,category="instagram-carousel",activeStyle=null;
function options(select,items,preferred){select.replaceChildren();items.forEach(x=>{const opt=node("option","",x.label);opt.value=x.value;select.appendChild(opt)});if(items.some(x=>x.value===preferred))select.value=preferred;select.disabled=items.length===0}
function styles(cat){return data.styles.filter(x=>x.category===cat&&x.brand===data.brand.id)}
function selectedStyle(){return styles(el("category-picker").value).find(x=>x.id===el("style-picker").value)}
function colorChip(label,value){const x=node("div","swatch"),b=node("b");if(/^#[0-9a-f]{6}$/i.test(value))b.style.backgroundColor=value;x.append(b,node("span","",label+" · "+value));return x}
function drawCategories(){const host=el("category-list");host.replaceChildren();data.categories.forEach(c=>{const btn=node("button","category");btn.type="button";btn.setAttribute("aria-pressed",String(c.id===category));const left=node("span");left.append(node("strong","",c.label),node("small","",c.style_count?c.style_count+" tasarım dili kayıtlı":"Henüz stil kaydı yok"));btn.append(left,node("span","mini",c.style_count?"Kayıtlı":"Hazırlanacak"));btn.addEventListener("click",()=>chooseCategory(c.id));host.append(btn)})}
function drawStyle(){
 const host=el("style-detail"),found=styles(category);host.replaceChildren();
 if(!found.length){
  const c=data.categories.find(x=>x.id===category),empty=node("div","empty");
  empty.append(node("span","eyebrow","Kategori / Henüz kayıtlı tarz yok"),
   node("h3","",c?.label||category),
   node("p","","Bu kategorinin altında birden fazla bağımsız tasarım tarzı yer alabilir. Henüz gerçek kaynak dosyasıyla tanımlanmış tarz bulunmuyor."));
  const a=node("a","link","Yeni tarz ekleme kaynakları ↗");a.href="https://github.com/cinegitim/design/tree/main/brands/asyada-egitim/styles";
  empty.append(a);host.append(empty);return
 }
 const selected=found.find(s=>s.id===activeStyle)||found[0];activeStyle=selected.id;
 host.append(node("span","eyebrow","Kategori → Tasarım tarzı → Alt varyasyon"),
   node("h3","",data.categories.find(c=>c.id===category)?.label||category),
   node("p","description",found.length+" bağımsız tasarım dili. Görsel dil seçimi markanın kanonik logo, font ve renklerini değiştirmez."));
 const grid=node("div","style-family-grid");grid.setAttribute("role","group");grid.setAttribute("aria-label","Kategoriye ait tasarım tarzları");
 for(const s of found){
  const btn=node("button","style-family-card");btn.type="button";
  btn.setAttribute("aria-pressed",String(s.id===selected.id));
  btn.setAttribute("aria-label",s.name+" · "+s.presets.length+" alt varyasyon · "+(s.production_approved?"Onaylı":"İncelemede"));
  const visual=node("span","style-family-visual");visual.dataset.style=s.id;visual.setAttribute("aria-hidden","true");
  const copy=node("span","style-family-copy");
  copy.append(node("strong","",s.name),
   node("small","",s.presets.length+" alt varyasyon · "+(s.production_approved?"Onaylı":"İncelemede")));
  btn.append(visual,copy);
  btn.addEventListener("click",()=>{
   if(activeStyle===s.id)return;
   activeStyle=s.id;
   el("category-picker").value=category;
   el("style-picker").value=s.id;
   updatePresets();drawStyle()
  });
  grid.append(btn)
 }
 host.append(grid);
 const focus=node("div","style-focus");
 focus.append(node("span","eyebrow","Seçili tasarım dili"),
  node("h3","",selected.name),node("p","description",selected.description));
 const m=node("div","meta");
 m.append(node("span","","v"+selected.version),
  node("span","",selected.production_approved?"Kreatif tarz onaylı":"İncelemede; henüz kreatif onay yok"),
  node("span","",selected.font));
 focus.append(m);
 const colors=node("div","swatches");
 for(const key of ["paper","red","ink"])if(selected.palette[key])colors.append(colorChip(key,selected.palette[key]));
 focus.append(colors,node("div","eyebrow","Bu tarza ait alt varyasyonlar"));
 const presets=node("div","presets");
 for(const preset of selected.presets){
  const tile=node("div","preset");tile.append(node("i"),node("strong","",preset.label));presets.append(tile)
 }
 focus.append(presets,node("p","description","Marka kimliği sabit: "+selected.lockups.join(" · ")+" · Jost ve onaylı renkler."));
 const source=node("p","source"),link=node("a","","Stil tanımını GitHub’da aç ↗");
 link.href="https://github.com/cinegitim/design/blob/main/"+selected.source_path;
 source.append(link);focus.append(source);host.append(focus)
}
function chooseCategory(id){category=id;activeStyle=null;drawCategories();el("category-picker").value=id;updateStyleOptions();drawStyle()}
function updateStyleOptions(){const found=styles(el("category-picker").value);options(el("style-picker"),found.map(s=>({value:s.id,label:s.name+" · "+s.status})),activeStyle||found[0]?.id);updatePresets()}
function updatePresets(){const s=selectedStyle();options(el("preset-picker"),s?s.presets.map(p=>({value:p.id,label:p.label})):[],s?.presets[0]?.id);updateInfo()}
function updateInfo(){if(!data)return;const s=selectedStyle(),route=data.executors.find(x=>x.id===el("executor-picker").value),model=data.model_families.find(x=>x.id===el("model-picker").value),host=el("production-status");host.replaceChildren();el("copy-brief").disabled=!(s&&route&&model);if(!s){host.append(node("p","","Bu kategoride kayıtlı tasarım dili yok. Önce marka kapsamına uygun bir stil eklenmeli."));return}host.append(node("strong","",s.name+" · "+s.status),node("p","","Ortam: "+(route?.executor||"—")+" ("+(route?.strategy||"—")+"). Model: "+(model?.name||"—")+". Yetenekler oturumda doğrulanır."),node("p","","Onaylı SVG, Jost, kurumsal palet ve kreatif onay şartı her modelde geçerli."))}
function makeBrief(){const s=selectedStyle(),route=data.executors.find(x=>x.id===el("executor-picker").value),model=data.model_families.find(x=>x.id===el("model-picker").value),preset=el("preset-picker").value;if(!s||!route||!model||!s.presets.some(p=>p.id===preset))throw Error("Kayıtlı stil ve üretim profili seçin.");return{
schema:1,origin:"brandstudio-system-hub",repository:"cinegitim/design",
selection:{brand:data.brand.id,category:s.category,style_id:s.id,style_version:s.version,style_source_blob_sha:s.source_blob_sha,preset_id:preset,style_status:s.status,canonical_lockups:s.lockup_assets,seal_sha256:data.brand_identity.seal_sha256,font:data.brand_identity.font,palette:s.palette},
environment:{executor_profile_id:route.id,executor:route.executor,strategy:route.strategy,required_capabilities:route.required_capabilities,reference_paths:route.references,model_family_id:model.id,model_family_status:"advisory",model_capabilities_verified:false},
model_guidance:{code:model.emphasis.code,image:model.emphasis.image},
mandatory_rules:["GitHub kanonik marka ve stil kurallarını oku; onaylı tam SVG logo baytlarını kullan.","Logoyu LLM ile yeniden çizme, yeniden yazma veya renklendirme.","Gerçek model/araç yeteneğini oturumda doğrula; doğrulanmayanı başarılı gösterme.","Düzenlenebilir kaynak, gerçek render ve GitHub PR kanıtını ayrı teslim et.","Kreatif onay ve sosyal medya yayını ayrı insan onayı ve harici kanıt gerektirir."],
github:{status:"not-submitted",branch:null,commit:null,pr:null},approval:{creative:"pending",social_published:false}
}}
async function copyBrief(){const feedback=el("copy-feedback");try{const brief=makeBrief();if(brief.github.status!=="not-submitted")throw Error("GitHub durum kontrolü hatalı.");const text=JSON.stringify(brief,null,2)+"\n";if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(text);else{const f=document.createElement("textarea");f.value=text;f.style.position="fixed";f.style.opacity="0";document.body.append(f);f.select();const ok=document.execCommand("copy");f.remove();if(!ok)throw Error("Tarayıcı kopyalama izni vermedi.")}feedback.textContent="Üretim fişi kopyalandı. Seçtiğiniz ajana iletebilirsiniz; henüz üretim başlamadı."}catch(e){feedback.textContent="Fiş kopyalanamadı: "+e.message}}
async function init(){try{const response=await fetch("catalog.json",{cache:"no-store"});if(!response.ok)throw Error("HTTP "+response.status);const value=await response.json();if(value.schema!==1||!Array.isArray(value.styles)||!Array.isArray(value.executors)||!Array.isArray(value.model_families))throw Error("Katalog şeması geçersiz");data=value;
el("metric-categories").textContent=data.categories.length;el("metric-styles").textContent=data.styles.length;el("metric-executors").textContent=data.executors.length;el("metric-models").textContent=data.model_families.length;
category=data.categories.find(x=>x.id==="instagram-carousel")?.id||data.categories[0]?.id||"";drawCategories();drawStyle();const colors=el("identity-palette");["paper","red","ink"].forEach(k=>{if(data.brand_identity.palette[k])colors.append(colorChip(k,data.brand_identity.palette[k]))});
options(el("category-picker"),data.categories.map(x=>({value:x.id,label:x.label})),category);
options(el("executor-picker"),data.executors.map(x=>({value:x.id,label:x.executor+" · "+x.id})),"work-connected-v1");
options(el("model-picker"),data.model_families.map(x=>({value:x.id,label:x.name+" · rehber"})),"gpt");
updateStyleOptions();
el("category-picker").addEventListener("change",()=>chooseCategory(el("category-picker").value));
el("style-picker").addEventListener("change",()=>{activeStyle=el("style-picker").value;updatePresets();drawStyle()});
["preset-picker","executor-picker","model-picker"].forEach(id=>el(id).addEventListener("change",updateInfo));
el("copy-brief").addEventListener("click",copyBrief);
}catch(e){el("production-status").textContent="Katalog yüklenemedi: "+e.message;el("style-detail").textContent="Tasarım sistemi şu anda kullanılamıyor."}}
init();
})();
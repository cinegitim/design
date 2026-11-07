/* Brandstudio style picker: browser presentation only, no network or GitHub writes. */
(function(root){
"use strict";
const $=id=>document.getElementById(id);
function options(select,records,wanted){
 select.replaceChildren();
 records.forEach(function(x){const o=document.createElement("option");o.value=x.value;o.textContent=x.label;select.appendChild(o)});
 if(records.some(x=>x.value===wanted))select.value=wanted;
 select.disabled=!records.length;
}
function create({module,getContext,commit,exportBrief,copyPrompt}){
 let registry=null;
 const status=message=>$("style-status").textContent=message;
 const eligible=ctx=>!!ctx.record&&ctx.record.family==="instagram"&&ctx.record.kind==="html"&&
   (ctx.record.pages?.length>1||ctx.record.categoryPath?.includes("Karuseller"));
 const find=()=>registry?.styles?.find(x=>{
  const c=getContext();
  return x.brand===c.brand&&x.category===$("style-category").value&&x.style_id===$("style-family").value;
 })||null;
 function pending(){ $("style-export").disabled=true;$("style-copy").disabled=true }
 function drawChoices(records){
  const host=$("style-choices"),details=$("style-choice-description");
  host.replaceChildren();
  const selected=find();
  if(!records.length){details.textContent="Henüz kayıtlı tarz yok. Mevcut tasarım korunuyor.";return}
  for(const spec of records){
   const button=document.createElement("button");
   button.type="button";button.className="style-choice";
   button.setAttribute("aria-pressed",String(spec.style_id===selected?.style_id));
   button.setAttribute("aria-label",spec.name+" — "+Object.keys(spec.presets).length+" alt varyasyon — "+(spec.status==="review-only"?"İncelemede":spec.status));
   const mini=document.createElement("span");mini.className="style-mini";
   mini.dataset.style=spec.style_id;mini.setAttribute("aria-hidden","true");
   const info=document.createElement("span");info.className="style-choice-copy";
   const name=document.createElement("strong");name.textContent=spec.name;
   const meta=document.createElement("small");
   meta.textContent=Object.keys(spec.presets).length+" alt varyasyon · "+(spec.status==="review-only"?"İncelemede":spec.status);
   info.append(name,meta);button.append(mini,info);
   button.addEventListener("click",()=>{
    if($("style-family").value===spec.style_id)return;
    $("style-family").value=spec.style_id;
    fillPresets(null);drawChoices(records);pending();
    status("Tarz adayı değişti: "+spec.name+". Çalışma alanına uygulamak için düğmeye basın.");
   });
   host.append(button);
  }
  if(selected){
   details.textContent=selected.description+" · "+Object.keys(selected.presets).length+" alt varyasyon. Bu çizimler gerçek tasarım önizlemesi değil, şematik tarz işaretleridir.";
  }
 }
 function axes(spec,selected){
  const node=$("style-axes");node.replaceChildren();
  if(!spec)return;
  const preset=spec.presets[$("style-preset").value]||spec.presets[spec.default_preset];
  for(const [key,axis] of Object.entries(spec.variation_axes)){
   const label=document.createElement("label"),select=document.createElement("select");
   label.textContent=key.replaceAll("_"," ");select.dataset.axis=key;select.title=axis.description||key;
   options(select,axis.options.map(v=>({value:v,label:v.replaceAll("-"," ")})),
    selected?.[key]||preset.variants[key]||axis.default);
   label.append(select);node.append(label);
  }
 }
 function fillPresets(saved){
  const s=find();
  options($("style-preset"),s?Object.entries(s.presets).map(([id,p])=>({value:id,label:p.label})):[],
    saved?.preset_id||s?.default_preset);
  options($("style-logo"),s?s.lockups.map(p=>({value:p.id,label:p.id})):[],
    saved?.lockup_id||"H-02/dark");
  axes(s,saved?.variation);
 }
 function fillFamilies(saved){
  const ctx=getContext(),category=$("style-category").value;
  const styles=(registry?.styles||[]).filter(s=>s.brand===ctx.brand&&s.category===category);
  options($("style-family"),styles.map(s=>({value:s.style_id,label:s.name+" · "+s.status})),
    saved?.style_id||styles[0]?.style_id);
  fillPresets(saved);drawChoices(styles);
  const maySave=eligible(ctx)&&category==="instagram-carousel"&&styles.length>0;
  $("style-save").disabled=!maySave;
  if(!maySave)status("Bu ürün için kayıtlı tasarım dili yok. Mevcut tasarım korunuyor.");
  else if(!saved)status("Stil adayı · henüz çalışma alanına uygulanmadı. İnsan kreatif onayı gerekiyor.");
 }
 function sync(){
  if(!registry||!module){status("Stil kataloğu yüklenemedi.");$("style-save").disabled=true;$("style-export").disabled=true;$("style-copy").disabled=true;return}
  const ctx=getContext();let chosen=ctx.state?.designStyle||null;
  if(chosen){try{module.validate(registry,chosen)}catch(e){status("Kayıtlı stil güncel katalogla eşleşmiyor: "+e.message);chosen=null}}
  const category=chosen?.category||(eligible(ctx)?"instagram-carousel":null);
  options($("style-category"),registry.categories.map(c=>({value:c.id,label:c.label+(c.registered?"":" · stil yok")})),category);
  if(!category)$("style-category").selectedIndex=-1;
  fillFamilies(chosen);
  $("style-export").disabled=!chosen;
  $("style-copy").disabled=!chosen;
  if(chosen)status("Çalışma alanında seçili · "+chosen.style_id+" / "+chosen.preset_id+" · "+chosen.approval_status+"");
 }
 function read(){
  const ctx=getContext(),s=find();
  if(!eligible(ctx)||!s||$("style-category").value!=="instagram-carousel")
   throw Error("Bu tasarımın kategorisi için stil seçilemedi");
  const preset=s.presets[$("style-preset").value],overrides={};
  $("style-axes").querySelectorAll("select[data-axis]").forEach(el=>{
   const defaultValue=preset.variants[el.dataset.axis]||s.variation_axes[el.dataset.axis].default;
   if(el.value!==defaultValue)overrides[el.dataset.axis]=el.value;
  });
  return module.resolve(registry,{brand:ctx.brand,category:s.category,style_id:s.style_id,
    preset_id:$("style-preset").value,lockup_id:$("style-logo").value,overrides});
 }
 $("style-category").addEventListener("change",()=>{fillFamilies(null);pending()});
 $("style-family").addEventListener("change",()=>{
  fillPresets(null);
  drawChoices((registry?.styles||[]).filter(x=>x.brand===getContext().brand&&x.category===$("style-category").value));
  pending();status("Tarz adayı değişti. Çalışma alanına uygulamak için butona basın.")
 });
 $("style-preset").addEventListener("change",()=>{axes(find(),null);pending();status("Alt varyasyonu uygulamak için butona basın.")});
 $("style-axes").addEventListener("change",()=>{pending();status("İnce ayarlar değişti; stili yeniden uygula.")});
 $("style-logo").addEventListener("change",()=>{pending();status("Onaylı logo varyantı değişti; stili yeniden uygula.")});
 $("style-save").addEventListener("click",()=>{
  try{const selection=read();commit(selection);
   $("style-export").disabled=false;$("style-copy").disabled=false;
   status("Stil uygulandı, ancak buluta kaydedilmedi. Üstteki kayıt düğmelerini kullanın · "+selection.approval_status+"")
  }catch(e){status("Stil uygulanamadı: "+e.message)}
 });
 $("style-export").addEventListener("click",()=>{
  try{
   const ctx=getContext(),selection=ctx.state?.designStyle;
   if(!selection)throw Error("Önce stili çalışma alanına uygulayın");
   module.validate(registry,selection);
   exportBrief(selection,ctx);
   status("Üretim fişi indirildi · GitHub PR henüz açılmadı. Bir ajan bu fişi PR'a eklemeli.")
  }catch(e){status("Üretim fişi hazırlanamadı: "+e.message)}
 });
 $("style-copy").addEventListener("click",async()=>{
  const button=$("style-copy");button.disabled=true;
  try{
   const ctx=getContext(),selected=ctx.state?.designStyle;
   if(!selected)throw Error("Önce stili çalışma alanına uygulayın");
   module.validate(registry,selected);
   if(typeof copyPrompt!=="function")throw Error("Pano desteği mevcut değil");
   const prompt=module.agentPrompt(registry,{selection:selected,product:ctx.slug,version:ctx.current});
   await copyPrompt(prompt);
   status("Ajan komutu panoya kopyalandı · aynı kilitli marka kuralları, seçili stil ve kaynak SHA kimliği ile. Üretim veya PR başlatılmadı.");
  }catch(e){status("Ajan komutu kopyalanamadı: "+e.message+" · alternatif: üretim fişini indir.")}
  finally{button.disabled=!Boolean(getContext().state?.designStyle)}
 });
 $("style-save").disabled=true;$("style-export").disabled=true;$("style-copy").disabled=true;
 return{setRegistry(value){if(!value||value.schema!==1||!Array.isArray(value.styles))throw Error("Geçersiz stil kataloğu");registry=value;sync()},sync};
}
root.BrandstudioStyleUI={create};
})(globalThis);
